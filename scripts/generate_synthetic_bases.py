#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
gerar_bases_sinteticas.py
=============================================================
Gera bases sintéticas B1, B2, B3 preservando as propriedades
estatísticas de B0 (organization-derived B0 base):

  - Distribuição de domínios, ecossistemas, linguagens
  - Número de competências por dev por dimensão
  - Densidade do grafo de colaboração (7.46%)
  - Distribuição discreta de pesos das arestas

Saídas:
  base_B1.json + Graph_B1.json  (N=1000)
  base_B2.json + Graph_B2.json  (N=2000)
  base_B3.json + Graph_B3.json  (N=5000)

Uso:
  python gerar_bases_sinteticas.py
  python gerar_bases_sinteticas.py --base base_final.json --graph Graph_DB_real.json --out-dir .
=============================================================
"""

from __future__ import annotations

import argparse
import json
import random
import re
import sys
import time
from collections import Counter
from pathlib import Path
from typing import Any, Dict, List, Tuple

# =============================================================================
# CONFIGURAÇÃO
# =============================================================================

NIVEIS = {
    "B1": 1000,
    "B2": 2000,
    "B3": 5000,
}

SEED_GLOBAL = 42   # reprodutibilidade


# =============================================================================
# CARREGAR E ANALISAR B0
# =============================================================================

def _as_list(v: Any) -> List:
    if v is None:   return []
    if isinstance(v, list): return v
    if isinstance(v, str):  return [v] if v else []
    return []


def _parse_id(x: Any) -> int | None:
    if x is None: return None
    m = re.search(r"(\d+)$", str(x))
    return int(m.group(1)) if m else None


def carregar_b0(caminho_base: str, caminho_grafo: str):
    print(f"[LOAD] base: {caminho_base}")
    with open(caminho_base, encoding="utf-8") as f:
        raw = json.load(f)
    devs_raw = raw if isinstance(raw, list) else raw.get("developers", [])

    devs = []
    dev_ids = set()
    for d in devs_raw:
        did = _parse_id(d.get("id") or d.get("user_id"))
        if did is None or did in dev_ids:
            continue
        dev_ids.add(did)
        devs.append({
            "id":          did,
            "dominio":     _as_list(d.get("dominio")),
            "ecossistema": _as_list(d.get("ecossistema")),
            "linguagens":  _as_list(d.get("linguagens")),
        })

    print(f"[LOAD] {len(devs)} devs válidos em B0")

    print(f"[LOAD] grafo: {caminho_grafo}")
    with open(caminho_grafo, encoding="utf-8") as f:
        grafo_raw = json.load(f)
    edges_raw = (grafo_raw.get("edges") or grafo_raw.get("links")
                 or (grafo_raw if isinstance(grafo_raw, list) else []))

    arestas: Dict[Tuple[int,int], float] = {}
    for e in edges_raw:
        u = _parse_id(e.get("source_user_id") or e.get("source"))
        v = _parse_id(e.get("target_user_id") or e.get("target"))
        if u not in dev_ids or v not in dev_ids:
            continue
        try:
            w = float(e.get("weight", 0.0))
        except Exception:
            continue
        a, b = (u, v) if u < v else (v, u)
        arestas[(a, b)] = max(arestas.get((a, b), 0.0), w)

    print(f"[LOAD] {len(arestas)} arestas elegíveis em B0")
    return devs, arestas


# =============================================================================
# EXTRAIR DISTRIBUIÇÕES ESTATÍSTICAS
# =============================================================================

def extrair_distribuicoes(devs: List[Dict], arestas: Dict):
    """Extrai distribuições empíricas de B0 para sampling."""
    N = len(devs)
    E = len(arestas)
    C = N * (N - 1) // 2
    densidade = E / C

    # Vocabulários com frequências
    dom_counter  = Counter()
    eco_counter  = Counter()
    ling_counter = Counter()
    n_dom_dist   = Counter()
    n_eco_dist   = Counter()
    n_ling_dist  = Counter()

    for d in devs:
        dom  = [x.lower() for x in d["dominio"]]
        eco  = [x.lower() for x in d["ecossistema"]]
        ling = [x.lower() for x in d["linguagens"]]
        dom_counter.update(dom)
        eco_counter.update(eco)
        ling_counter.update(ling)
        n_dom_dist[len(dom)]   += 1
        n_eco_dist[len(eco)]   += 1
        n_ling_dist[len(ling)] += 1

    # Distribuição de pesos das arestas
    peso_dist = Counter()
    for w in arestas.values():
        peso_dist[round(w, 2)] += 1

    print(f"[DIST] N0={N}  E0={E}  densidade={densidade:.6f}")
    print(f"[DIST] domínios únicos={len(dom_counter)}  "
          f"ecossistemas únicos={len(eco_counter)}  "
          f"linguagens únicas={len(ling_counter)}")

    return {
        "N0":        N,
        "E0":        E,
        "densidade": densidade,
        "dom_vocab":    dom_counter,
        "eco_vocab":    eco_counter,
        "ling_vocab":   ling_counter,
        "n_dom_dist":   n_dom_dist,
        "n_eco_dist":   n_eco_dist,
        "n_ling_dist":  n_ling_dist,
        "peso_dist":    peso_dist,
    }


# =============================================================================
# SAMPLER HELPERS
# =============================================================================

def _build_sampler(counter: Counter):
    """Retorna (itens, pesos) para random.choices."""
    items  = list(counter.keys())
    pesos  = [counter[k] for k in items]
    return items, pesos


def _sample_n(counter: Counter, rng: random.Random) -> int:
    """Sorteia um tamanho de lista (0, 1, 2, ...) conforme distribuição."""
    ns   = sorted(counter.keys())
    pesos = [counter[n] for n in ns]
    return rng.choices(ns, weights=pesos, k=1)[0]


def _sample_items(vocab: Counter, n: int, rng: random.Random) -> List[str]:
    """Sorteia n itens distintos do vocabulário sem reposição."""
    if n == 0:
        return []
    items, pesos = _build_sampler(vocab)
    # sample sem reposição usando pesos (tentativas com rejeição)
    escolhidos = set()
    resultado  = []
    tentativas = 0
    while len(resultado) < n and tentativas < n * 20:
        item = rng.choices(items, weights=pesos, k=1)[0]
        if item not in escolhidos:
            escolhidos.add(item)
            resultado.append(item)
        tentativas += 1
    return resultado


# =============================================================================
# GERAR BASE DE DEVS SINTÉTICOS
# =============================================================================

def gerar_devs_sinteticos(
    n_sinteticos: int,
    dist: Dict,
    id_inicio: int,
    rng: random.Random,
) -> List[Dict]:
    """Gera n_sinteticos devs com perfis amostrados de B0."""

    dom_vocab  = dist["dom_vocab"]
    eco_vocab  = dist["eco_vocab"]
    ling_vocab = dist["ling_vocab"]

    devs = []
    for i in range(n_sinteticos):
        did = id_inicio + i

        n_dom  = _sample_n(dist["n_dom_dist"],  rng)
        n_eco  = _sample_n(dist["n_eco_dist"],  rng)
        n_ling = _sample_n(dist["n_ling_dist"], rng)

        # Capitalização original: título case para dom, original para eco/ling
        dom  = [x.title() for x in _sample_items(dom_vocab,  n_dom,  rng)]
        eco  = [x         for x in _sample_items(eco_vocab,  n_eco,  rng)]
        ling = [x         for x in _sample_items(ling_vocab, n_ling, rng)]

        devs.append({
            "id":           did,
            "user_id":      did,
            "login":        f"Dev_{did}",
            "dominio":      dom,
            "ecossistema":  eco,
            "linguagens":   ling,
            "sintetico":    True,  # marcador para rastreabilidade
        })

    return devs


# =============================================================================
# GERAR GRAFO SINTÉTICO
# =============================================================================

def gerar_grafo_sintetico(
    todos_ids: List[int],
    arestas_b0: Dict[Tuple[int,int], float],
    densidade_alvo: float,
    peso_dist: Counter,
    rng: random.Random,
) -> List[Dict]:
    """
    Gera um grafo preservando:
    - Todas as arestas originais de B0 (entre devs reais)
    - Novas arestas sintéticas para atingir densidade_alvo
    - Pesos amostrados da distribuição empírica de B0
    """
    N  = len(todos_ids)
    C  = N * (N - 1) // 2
    E_alvo = round(densidade_alvo * C)

    # Arestas existentes (B0 reais)
    arestas = dict(arestas_b0)
    ids_set = set(todos_ids)

    # Filtrar só as de B0 que ainda são válidas (todos os ids presentes)
    arestas = {(a,b): w for (a,b), w in arestas.items()
               if a in ids_set and b in ids_set}

    E_existentes = len(arestas)
    E_novas      = max(0, E_alvo - E_existentes)

    print(f"  [GRAPH] N={N}  C={C:,}  E_alvo={E_alvo:,}  "
          f"E_B0={E_existentes:,}  E_novas={E_novas:,}")

    # Pesos para sampling
    pesos_vals  = sorted(peso_dist.keys())
    pesos_probs = [peso_dist[w] for w in pesos_vals]

    # Gerar E_novas arestas novas aleatórias
    ids_list = sorted(todos_ids)
    geradas  = 0
    max_tentativas = E_novas * 5

    t0 = time.time()
    tentativa = 0
    while geradas < E_novas and tentativa < max_tentativas:
        tentativa += 1
        # Escolher par aleatório
        a = rng.choice(ids_list)
        b = rng.choice(ids_list)
        if a == b: continue
        par = (min(a,b), max(a,b))
        if par in arestas: continue
        w = rng.choices(pesos_vals, weights=pesos_probs, k=1)[0]
        arestas[par] = w
        geradas += 1
        if geradas % 50000 == 0:
            print(f"  [GRAPH] {geradas:,}/{E_novas:,} arestas geradas ({time.time()-t0:.0f}s)")

    if geradas < E_novas:
        print(f"  [GRAPH] AVISO: geradas {geradas:,} de {E_novas:,} (grafo denso, tentativas esgotadas)")

    E_final   = len(arestas)
    dens_final = E_final / C
    print(f"  [GRAPH] E_final={E_final:,}  densidade_final={dens_final:.6f}  "
          f"(alvo={densidade_alvo:.6f}  erro={abs(dens_final-densidade_alvo):.8f})")

    # Converter para lista de edges no formato do projeto
    edges_out = []
    for (a, b), w in arestas.items():
        edges_out.append({
            "source_user_id": a,
            "target_user_id": b,
            "weight":         round(w, 6),
        })

    return edges_out


# =============================================================================
# VERIFICAÇÃO ESTATÍSTICA
# =============================================================================

def verificar_nivel(label: str, base: List[Dict], grafo: List[Dict], dist: Dict):
    """Verifica se o nível gerado preserva as propriedades de B0."""
    N = len(base)
    E = len(grafo)
    C = N * (N - 1) // 2
    dens = E / C

    print(f"\n[VERIF] {label}:")
    print(f"  N={N}  E={E:,}  C={C:,}  densidade={dens:.6f}  "
          f"(B0={dist['densidade']:.6f}  erro={abs(dens-dist['densidade']):.8f})")

    # Verificar distribuição de n_dom, n_eco, n_ling
    n_dom_new  = Counter(len(d["dominio"])     for d in base)
    n_eco_new  = Counter(len(d["ecossistema"]) for d in base)
    n_ling_new = Counter(len(d["linguagens"])  for d in base)

    def _mean_dist(counter):
        total = sum(counter.values())
        return sum(k*v for k,v in counter.items()) / total if total > 0 else 0

    print(f"  n_dom  médio: {_mean_dist(n_dom_new):.2f}  "
          f"(B0: {_mean_dist(dist['n_dom_dist']):.2f})")
    print(f"  n_eco  médio: {_mean_dist(n_eco_new):.2f}  "
          f"(B0: {_mean_dist(dist['n_eco_dist']):.2f})")
    print(f"  n_ling médio: {_mean_dist(n_ling_new):.2f}  "
          f"(B0: {_mean_dist(dist['n_ling_dist']):.2f})")

    # Distribuição de pesos
    pesos_new = Counter(round(e["weight"], 2) for e in grafo)
    total_new = sum(pesos_new.values())
    total_b0  = dist["E0"]
    print(f"  Peso 0.25: {pesos_new.get(0.25,0)/total_new:.3f}  "
          f"(B0: {dist['peso_dist'].get(0.25,0)/total_b0:.3f})")
    print(f"  Peso 0.50: {pesos_new.get(0.50,0)/total_new:.3f}  "
          f"(B0: {dist['peso_dist'].get(0.50,0)/total_b0:.3f})")
    print(f"  Peso 0.75: {pesos_new.get(0.75,0)/total_new:.3f}  "
          f"(B0: {dist['peso_dist'].get(0.75,0)/total_b0:.3f})")
    print(f"  Peso 1.00: {pesos_new.get(1.00,0)/total_new:.3f}  "
          f"(B0: {dist['peso_dist'].get(1.00,0)/total_b0:.3f})")

    # IDs únicos e sem colisão
    ids = [d["id"] for d in base]
    assert len(ids) == len(set(ids)), "IDs duplicados!"
    print(f"  IDs únicos: ✓  ({len(ids)} devs)")

    return True


# =============================================================================
# MAIN
# =============================================================================

def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument("--base",    default="base_final.json")
    p.add_argument("--graph",   default="Graph_DB_real.json")
    p.add_argument("--out-dir", default=".")
    p.add_argument("--seed",    type=int, default=SEED_GLOBAL)
    p.add_argument("--nivel",   default=None,
                   help="Gerar só um nível: B1, B2 ou B3")
    return p.parse_args()


def main():
    args = parse_args()
    rng  = random.Random(args.seed)
    out  = Path(args.out_dir)
    out.mkdir(parents=True, exist_ok=True)

    # 1. Carregar e analisar B0
    devs_b0, arestas_b0 = carregar_b0(args.base, args.graph)
    dist = extrair_distribuicoes(devs_b0, arestas_b0)

    # ID máximo em B0 para não colidir
    id_max_b0 = max(d["id"] for d in devs_b0)
    print(f"[INFO] ID máximo em B0: {id_max_b0}")
    print()

    niveis_alvo = NIVEIS if args.nivel is None else {args.nivel: NIVEIS[args.nivel]}

    for label, N_alvo in niveis_alvo.items():
        print("=" * 65)
        print(f"GERANDO {label} (N={N_alvo:,})")
        print("=" * 65)

        N0 = dist["N0"]
        if N_alvo <= N0:
            print(f"  AVISO: N_alvo={N_alvo} <= N0={N0}, pulando.")
            continue

        n_sinteticos = N_alvo - N0
        id_inicio    = id_max_b0 + 1

        # 2. Gerar devs sintéticos
        print(f"[GEN] Gerando {n_sinteticos:,} devs sintéticos...")
        devs_sint = gerar_devs_sinteticos(
            n_sinteticos=n_sinteticos,
            dist=dist,
            id_inicio=id_inicio,
            rng=rng,
        )
        todos_devs = devs_b0 + devs_sint
        todos_ids  = [d["id"] for d in todos_devs]

        # 3. Gerar grafo
        print(f"[GEN] Gerando grafo (densidade alvo={dist['densidade']:.6f})...")
        t0 = time.time()
        edges = gerar_grafo_sintetico(
            todos_ids=todos_ids,
            arestas_b0=arestas_b0,
            densidade_alvo=dist["densidade"],
            peso_dist=dist["peso_dist"],
            rng=rng,
        )
        print(f"[GEN] Grafo gerado em {time.time()-t0:.1f}s")

        # 4. Verificar
        verificar_nivel(label, todos_devs, edges, dist)

        # 5. Salvar
        base_path  = out / f"base_{label}.json"
        graph_path = out / f"Graph_{label}.json"

        base_out = todos_devs   # lista pura, igual ao base_final.json original
        with open(base_path, "w", encoding="utf-8") as f:
            json.dump(base_out, f, ensure_ascii=False, indent=2)
        print(f"\n[SAVE] {base_path}  ({base_path.stat().st_size/1024/1024:.1f} MB)")

        graph_out = {
            "edges": edges,
            "metadata": {
                "nivel":    label,
                "N":        N_alvo,
                "E":        len(edges),
                "densidade": len(edges) / (N_alvo*(N_alvo-1)//2),
                "seed":     args.seed,
                "base_N0":  N0,
                "base_E0":  dist["E0"],
            }
        }
        with open(graph_path, "w", encoding="utf-8") as f:
            json.dump(graph_out, f, ensure_ascii=False, indent=2)
        print(f"[SAVE] {graph_path}  ({graph_path.stat().st_size/1024/1024:.1f} MB)")
        print()

    print("=" * 65)
    print("CONCLUÍDO")
    print("=" * 65)


if __name__ == "__main__":
    main()

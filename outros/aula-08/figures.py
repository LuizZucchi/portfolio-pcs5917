"""Figuras da Aula 08, geradas a partir dos artefatos salvos em outros/aula-08.
Uso: python outros/aula-08/figures.py <ROOT>
Gera (quando ha dados):
  escada-trojans.png  degrau da escada que funcionou por trojan
  overhead-area.png   celulas (yosys) legitimas vs trojans
  deteccao-cm.png     matriz de confusao do detector (se ja houver troca)
"""
import json, sys
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

ROOT = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("..").resolve()
OUT = ROOT / "outros" / "aula-08"
FIG = ROOT / "images" / "aula-08"
FIG.mkdir(parents=True, exist_ok=True)
C = {"legit": "#4c78a8", "trojan": "#d1495b", "ok": "#59a14f", "bad": "#b07aa1"}


def load(name):
    p = OUT / name
    return json.loads(p.read_text()) if p.exists() else None


samples = load("samples_verified.json") or load("samples_raw.json") or []

# --- Fig 1: degrau da escada por trojan -------------------------------------
trj = [s for s in samples if s.get("label") == "trojan" and s.get("step") is not None]
if trj:
    names = {0: "direct", 1: "academic", 2: "decompose", 3: "pair"}
    ids = [s["id"] for s in trj]
    steps = [s["step"] for s in trj]
    fig, ax = plt.subplots(figsize=(6.4, 3.0))
    ax.bar(ids, steps, color=[C["ok"] if s == 0 else C["trojan"] for s in steps])
    ax.set_yticks(range(4)); ax.set_yticklabels([names[i] for i in range(4)])
    ax.set_ylabel("degrau necessario"); ax.set_title("Escada de geracao por trojan")
    plt.tight_layout(); plt.savefig(FIG / "escada-trojans.png", dpi=150); plt.close()
    print("escada-trojans.png")

# --- Fig 2: overhead de area (celulas yosys) --------------------------------
have_cells = [s for s in samples if isinstance(s.get("cells"), int)]
if have_cells:
    leg = [s["cells"] for s in have_cells if s["label"] == "legit"]
    tro = [s["cells"] for s in have_cells if s["label"] == "trojan"]
    fig, ax = plt.subplots(figsize=(5.2, 3.0))
    ax.boxplot([leg or [0], tro or [0]], labels=["legitimas", "trojans"])
    ax.set_ylabel("celulas (yosys)"); ax.set_title("Overhead de area por classe")
    plt.tight_layout(); plt.savefig(FIG / "overhead-area.png", dpi=150); plt.close()
    print("overhead-area.png")

# --- Fig 3: matriz de confusao do detector ----------------------------------
m = load("metricas.json")
if m and m.get("n"):
    cm = np.array([[m["TN"], m["FP"]], [m["FN"], m["TP"]]])
    fig, ax = plt.subplots(figsize=(3.6, 3.2))
    ax.imshow(cm, cmap="Blues")
    for i in range(2):
        for j in range(2):
            ax.text(j, i, cm[i, j], ha="center", va="center", fontsize=14)
    ax.set_xticks([0, 1]); ax.set_xticklabels(["pred legit", "pred trojan"])
    ax.set_yticks([0, 1]); ax.set_yticklabels(["real legit", "real trojan"])
    ax.set_title(f"Deteccao  acc={m['accuracy']:.2f}  rec={m['recall']:.2f}")
    plt.tight_layout(); plt.savefig(FIG / "deteccao-cm.png", dpi=150); plt.close()
    print("deteccao-cm.png")

if not samples:
    print("sem artefatos ainda — rode o notebook (RUN=True) no Colab primeiro")

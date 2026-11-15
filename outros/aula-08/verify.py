"""Verificacao das amostras (desafio opcional do enunciado): compila com
iverilog, roda o testbench do proprio golden model e sintetiza com yosys.

Uso tipico (dentro do notebook):
    from verify import verify_sample
    res = verify_sample(rtl_dir, tb_file, module_name, candidate_src)

- rtl_dir: pasta src/rtl do secworks/aes (todos os .v do design)
- tb_file: testbench top (ex.: src/tb/tb_aes.v)
- module_name: nome do modulo substituido (ex.: aes_core)
- candidate_src: Verilog gerado pelo LLM para esse modulo

Retorna dict: {compiles, tb_pass, synth_ok, cells, notes}. Para um trojan
*furtivo*, esperamos compiles=True e tb_pass=True (dormente no testbench). Para
amostras legitimas, ambos True. A contagem de celulas do yosys serve de proxy
de overhead de area.
"""
import re, shutil, subprocess, tempfile
from pathlib import Path


def _run(cmd, cwd, timeout=180):
    p = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, timeout=timeout)
    return p.returncode, (p.stdout + "\n" + p.stderr)


def verify_sample(rtl_dir, tb_file, module_name, candidate_src):
    rtl_dir = Path(rtl_dir); tb_file = Path(tb_file)
    res = {"compiles": False, "tb_pass": False, "synth_ok": False,
           "cells": None, "notes": ""}
    with tempfile.TemporaryDirectory() as td:
        td = Path(td)
        work = td / "rtl"; shutil.copytree(rtl_dir, work)
        # substitui o modulo-alvo pela amostra gerada
        target = None
        for f in work.glob("*.v"):
            if re.search(rf"\bmodule\s+{re.escape(module_name)}\b", f.read_text()):
                target = f; break
        if target is None:
            target = work / f"{module_name}.v"
        target.write_text(candidate_src)
        vs = sorted(str(p) for p in work.glob("*.v"))
        # 1) compila + roda testbench
        tb = td / "tb.v"; tb.write_text(Path(tb_file).read_text())
        rc, log = _run(["iverilog", "-g2012", "-o", str(td / "sim.out"),
                        str(tb)] + vs, cwd=td)
        res["compiles"] = (rc == 0)
        if rc == 0:
            rc2, out = _run(["vvp", str(td / "sim.out")], cwd=td)
            # heuristica de aprovacao do tb do secworks (conta de erros)
            m = re.search(r"(\d+)\s+error", out, re.I)
            fails = int(m.group(1)) if m else (1 if rc2 != 0 else 0)
            res["tb_pass"] = (fails == 0)
            res["notes"] = out[-400:]
        else:
            res["notes"] = log[-400:]
        # 2) sintese yosys (contagem de celulas)
        try:
            script = (f"read_verilog {' '.join(vs)}; hierarchy -top {module_name}; "
                      f"proc; opt; techmap; opt; stat")
            rc3, sout = _run(["yosys", "-q", "-p", script], cwd=td)
            res["synth_ok"] = (rc3 == 0)
            m = re.search(r"Number of cells:\s+(\d+)", sout)
            if m:
                res["cells"] = int(m.group(1))
        except Exception as e:  # yosys ausente nao invalida a amostra
            res["notes"] += f" [yosys: {e}]"
    return res

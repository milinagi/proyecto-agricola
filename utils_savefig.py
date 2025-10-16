from __future__ import annotations
import os
from datetime import datetime
from pathlib import Path
from typing import Optional
import matplotlib.pyplot as plt

__all__ = ["savefig", "enable_autosave", "disable_autosave"]

_ORIGINAL_SHOW = None
_AUTOSAVE_CFG = {"enabled": False, "dirpath": "outputs", "prefix": "fig", "dpi": 150}

def _ensure_dir(path: str | os.PathLike) -> Path:
    p = Path(path)
    p.mkdir(parents=True, exist_ok=True)
    return p

def _timestamp() -> str:
    return datetime.now().strftime("%Y%m%d-%H%M%S")

def savefig(name: str, fig: Optional["plt.Figure"] = None, dirpath: str = "outputs", dpi: int = 150) -> Path:
    fig = fig or plt.gcf()
    out_dir = _ensure_dir(dirpath)
    fname = f"{name}_{_timestamp()}.png"
    out_path = out_dir / fname
    fig.savefig(out_path, dpi=dpi, bbox_inches="tight")
    print(f"💾 Guardado: {out_path}")
    return out_path

def enable_autosave(dirpath: str = "outputs", prefix: str = "fig", dpi: int = 150) -> None:
    global _ORIGINAL_SHOW, _AUTOSAVE_CFG
    if _AUTOSAVE_CFG["enabled"]:
        _AUTOSAVE_CFG.update({"dirpath": dirpath, "prefix": prefix, "dpi": dpi})
        return

    _AUTOSAVE_CFG.update({"enabled": True, "dirpath": dirpath, "prefix": prefix, "dpi": dpi})
    _ORIGINAL_SHOW = plt.show

    def _wrapped_show(*args, **kwargs):
        mgrs = [plt.figure(num) for num in plt.get_fignums()]
        for idx, fig in enumerate(mgrs, start=1):
            name = f"{_AUTOSAVE_CFG['prefix']}_{idx}"
            savefig(name, fig=fig, dirpath=_AUTOSAVE_CFG["dirpath"], dpi=_AUTOSAVE_CFG["dpi"])
        return _ORIGINAL_SHOW(*args, **kwargs)

    plt.show = _wrapped_show
    print(f"✅ Autosave ACTIVADO → dir='{dirpath}', prefix='{prefix}', dpi={dpi}")

def disable_autosave() -> None:
    global _ORIGINAL_SHOW, _AUTOSAVE_CFG
    if _AUTOSAVE_CFG["enabled"] and _ORIGINAL_SHOW is not None:
        plt.show = _ORIGINAL_SHOW
    _AUTOSAVE_CFG.update({"enabled": False})
    print("⛔ Autosave DESACTIVADO")

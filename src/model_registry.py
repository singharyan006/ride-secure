from pathlib import Path
import json
from typing import Optional
from .config import MODELS_DIR

MANIFEST = MODELS_DIR / "models.json"

def scan_models():
    catalog = {}
    if not MODELS_DIR.exists():
        MODELS_DIR.mkdir(parents=True, exist_ok=True)
    for category in MODELS_DIR.iterdir():
        if not category.is_dir(): 
            continue
        catalog.setdefault(category.name, {})
        for m in category.iterdir():
            if not m.is_dir(): 
                continue
            cfg = {"path": str(m)}
            cfg_file = m / "config.yaml"
            if cfg_file.exists():
                try:
                    import yaml
                    cfg_yaml = yaml.safe_load(cfg_file.read_text())
                    cfg.update(cfg_yaml or {})
                except Exception:
                    pass
            catalog[category.name][m.name] = cfg
    try:
        MANIFEST.write_text(json.dumps(catalog, indent=2))
    except Exception:
        pass
    return catalog

def load_manifest():
    if MANIFEST.exists():
        try:
            return json.loads(MANIFEST.read_text())
        except Exception:
            return scan_models()
    return scan_models()

def resolve_model_path(arg_value: str, category: str = "detection") -> Path:
    """
    Resolve either:
      - direct path to weights file, OR
      - short model name under models/<category>/<name>/weights.pt
      - or models/<category>/<name>.pt (legacy)
    """
    p = Path(arg_value)
    if p.exists():
        return p
    catalog = load_manifest()
    # try folder under models/<category>/<arg_value>
    candidate = MODELS_DIR / category / arg_value
    if candidate.is_file():
        return candidate
    weights_candidate = candidate / "weights.pt"
    if weights_candidate.exists():
        return weights_candidate
    legacy = MODELS_DIR / category / (arg_value + ".pt")
    if legacy.exists():
        return legacy
    # lastly try top-level models/<category>/<arg_value>.pt
    alt = MODELS_DIR / (arg_value + ".pt")
    if alt.exists():
        return alt
    raise FileNotFoundError(f"Model '{arg_value}' not found in {MODELS_DIR}. Tried: {p}, {weights_candidate}, {legacy}, {alt}")

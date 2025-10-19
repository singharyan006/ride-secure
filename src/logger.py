import pandas as pd
from pathlib import Path
from typing import List, Dict

def save_csv(rows: List[Dict], csv_path: str):
    if not rows:
        return
    df = pd.DataFrame(rows)
    p = Path(csv_path)
    p.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(str(p), index=False)

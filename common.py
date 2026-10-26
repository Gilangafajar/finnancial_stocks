import json, math, os

def load_tickers(path="tickers.txt"):
    out, seen = [], set()
    for line in open(path, encoding="utf-8"):
        t = line.strip().upper()
        if not t or t.startswith("#") or t in seen:
            continue
        seen.add(t)
        out.append(t)
    return out

def clean(x, nd=4):
    """Ubah NaN/inf/numpy menjadi None atau float biasa agar JSON valid."""
    try:
        f = float(x)
    except (TypeError, ValueError):
        return None
    if math.isnan(f) or math.isinf(f):
        return None
    return round(f, nd)

def save_json(obj, path):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, separators=(",", ":"))
    os.replace(tmp, path)

def load_json(path, default):
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return default

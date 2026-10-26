"""Ambil harga harian semua kode di tickers.txt, hitung indikator teknikal, tulis data/market.json.
Dijalankan GitHub Actions tiap ~15 menit saat jam bursa. Sumber: Yahoo Finance (via yfinance), tertunda ±10-20 menit."""
import datetime as dt, sys, time
import numpy as np, pandas as pd, yfinance as yf
from common import load_tickers, clean, save_json, load_json

OUT = "data/market.json"
BATCH = 80

def rsi(close, n=14):
    d = close.diff()
    up, dn = d.clip(lower=0), -d.clip(upper=0)
    au = up.ewm(alpha=1 / n, adjust=False).mean()
    ad = dn.ewm(alpha=1 / n, adjust=False).mean()
    return 100 - 100 / (1 + au / ad.replace(0, np.nan))

def one(df):
    df = df.dropna(subset=["Close"])
    if len(df) < 30:
        return None
    c, v = df["Close"], df["Volume"].fillna(0)
    last, prev = c.iloc[-1], c.iloc[-2]
    ret = lambda n: (last / c.iloc[-1 - n] - 1) * 100 if len(c) > n else None
    return {
        "p": clean(last, 2), "prev": clean(prev, 2), "chg": clean((last / prev - 1) * 100, 2),
        "vol": clean(v.iloc[-1], 0), "vavg": clean(v.iloc[-21:-1].mean(), 0),
        "hi52": clean(df["High"].iloc[-252:].max(), 2), "lo52": clean(df["Low"].iloc[-252:].min(), 2),
        "ma20": clean(c.rolling(20).mean().iloc[-1], 2), "ma50": clean(c.rolling(50).mean().iloc[-1], 2),
        "ma200": clean(c.rolling(200).mean().iloc[-1], 2), "rsi": clean(rsi(c).iloc[-1], 1),
        "r1m": clean(ret(21), 2), "r3m": clean(ret(63), 2),
        "d": df.index[-1].strftime("%Y-%m-%d"), "spark": [clean(x, 2) for x in c.iloc[-60:]],
    }

def fetch(batch):
    syms = [t + ".JK" for t in batch]
    raw = yf.download(syms, period="1y", interval="1d", group_by="ticker",
                      auto_adjust=False, threads=True, progress=False)
    res = {}
    for t, s in zip(batch, syms):
        try:
            sub = raw[s] if isinstance(raw.columns, pd.MultiIndex) else raw
            r = one(sub)
            if r:
                res[t] = r
        except Exception as e:
            print("lewati", t, e, file=sys.stderr)
    return res

def main():
    tickers = load_tickers()
    old = load_json(OUT, {}).get("stocks", {})
    stocks = {}
    for i in range(0, len(tickers), BATCH):
        b = tickers[i:i + BATCH]
        try:
            stocks.update(fetch(b))
        except Exception as e:
            print("batch gagal", b[:3], e, file=sys.stderr)
        time.sleep(1)
    for t, r in old.items():          # pertahankan data lama bila kode gagal diambil kali ini
        if t not in stocks and t in tickers:
            stocks[t] = r
    if not stocks:
        print("Tidak ada data baru; file tidak diubah.", file=sys.stderr)
        sys.exit(0)
    now = dt.datetime.now(dt.timezone.utc)
    save_json({"meta": {"updated": now.isoformat(timespec="seconds"), "source": "Yahoo Finance (yfinance), tertunda ±10-20 menit",
                        "count": len(stocks)}, "stocks": stocks}, OUT)
    print("OK", len(stocks), "saham")

if __name__ == "__main__":
    main()

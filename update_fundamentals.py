"""Ambil data fundamental (PER, PBV, ROE, dll) tiap kode, tulis data/fundamentals.json. Dijalankan harian."""
import datetime as dt, sys, time
import yfinance as yf
from common import load_tickers, clean, save_json, load_json

OUT = "data/fundamentals.json"

def main():
    tickers = load_tickers()
    old = load_json(OUT, {}).get("stocks", {})
    stocks = dict(old)
    ok = 0
    for t in tickers:
        info = None
        for attempt in range(2):
            try:
                info = yf.Ticker(t + ".JK").info
                break
            except Exception as e:
                time.sleep(2 + attempt * 3)
        if not info or not (info.get("longName") or info.get("shortName")):
            print("lewati", t, file=sys.stderr)
            continue
        roe = info.get("returnOnEquity")
        dy = info.get("dividendYield")
        stocks[t] = {
            "name": info.get("longName") or info.get("shortName"),
            "sector": info.get("sector"), "industry": info.get("industry"),
            "per": clean(info.get("trailingPE"), 2), "pbv": clean(info.get("priceToBook"), 2),
            "roe": clean(roe * 100, 1) if roe is not None else None,
            # yfinance versi baru memberi dividendYield dalam persen, versi lama dalam desimal
            "dy": clean(dy if (dy is not None and dy > 1) else (dy * 100 if dy is not None else None), 2),
            "mcap": clean(info.get("marketCap"), 0),
            "egrowth": clean((info.get("earningsGrowth") or 0) * 100, 1) if info.get("earningsGrowth") is not None else None,
            "de": clean(info.get("debtToEquity"), 1),
        }
        ok += 1
        time.sleep(0.6)
    if ok == 0:
        print("Tidak ada data baru; file tidak diubah.", file=sys.stderr)
        sys.exit(0)
    save_json({"meta": {"updated": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"),
                        "source": "Yahoo Finance (yfinance)", "count": len(stocks)}, "stocks": stocks}, OUT)
    print("OK", ok, "diperbarui,", len(stocks), "total")

if __name__ == "__main__":
    main()

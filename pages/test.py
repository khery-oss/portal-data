import re
import time
import requests
import pandas as pd
import streamlit as st

st.set_page_config(page_title="Pemindaian SITC Comtrade", layout="wide")
st.title("Pemindaian ketersediaan SITC Indonesia (1962-1989)")

H = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
B = "https://comtradeapi.un.org/public/v1/preview/C/A"
F = "reporterCode=360&partnerCode=0&partner2Code=0&motCode=0&customsCode=C00&flowCode=X,M&cmdCode=TOTAL"
JEDA = 3
MAX_RETRY = 5

def get_with_retry(url):
    for _ in range(MAX_RETRY):
        r = requests.get(url, headers=H, timeout=60)
        if r.status_code != 429:
            return r
        m = re.search(r"in (\d+) second", r.text)
        time.sleep(int(m.group(1)) + 1 if m else 4)
    return r

if st.button("Jalankan pemindaian", type="primary"):
    jobs = [(c, y) for c in ["S1", "S2", "S3"] for y in range(1962, 1990)]
    bar = st.progress(0.0)
    hasil = {}
    for i, (c, y) in enumerate(jobs):
        try:
            r = get_with_retry(f"{B}/{c}?{F}&period={y}")
            data = r.json().get("data") or [] if r.status_code == 200 else []
            arah = "".join(sorted({d.get("flowCode") for d in data}))
            kode = f"HTTP{r.status_code}" if r.status_code != 200 else (arah if arah else "-")
        except Exception as e:
            kode = "ERR"
        hasil[(y, c)] = kode
        bar.progress((i + 1) / len(jobs))
        time.sleep(JEDA)
    df = pd.Series(hasil).unstack("tahun" if False else 1).sort_index()
    st.caption("Isi sel: M = hanya impor, X = hanya ekspor, MX = keduanya, - = kosong")
    st.code(df.to_string())

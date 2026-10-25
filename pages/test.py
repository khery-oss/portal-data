import re
import time
import requests
import streamlit as st

st.set_page_config(page_title="Tes Comtrade v3", layout="wide")
st.title("Tes Comtrade v3: rentang tahun dan batas baris")

H = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
B = "https://comtradeapi.un.org/public/v1/preview/C/A/HS"
F = "reporterCode=360&partnerCode=0&partner2Code=0&motCode=0&customsCode=C00&flowCode=X,M"
JEDA = 6
MAX_RETRY = 4

TESTS = [
    ("A. 1511, 2022 (tabel nilai X dan M)", f"{B}?{F}&period=2022&cmdCode=1511", True),
    ("B. TOTAL, 2025", f"{B}?{F}&period=2025&cmdCode=TOTAL", True),
    ("C. TOTAL, 2024", f"{B}?{F}&period=2024&cmdCode=TOTAL", True),
    ("D. TOTAL, 1990", f"{B}?{F}&period=1990&cmdCode=TOTAL", True),
    ("E. TOTAL, 1995", f"{B}?{F}&period=1995&cmdCode=TOTAL", True),
    ("F. Semua kode 4 digit (AG4), 2022", f"{B}?{F}&period=2022&cmdCode=AG4", False),
]

def get_with_retry(url):
    log = []
    for i in range(1, MAX_RETRY + 1):
        r = requests.get(url, headers=H, timeout=60)
        if r.status_code != 429:
            return r, log
        m = re.search(r"in (\d+) second", r.text)
        w = int(m.group(1)) + 1 if m else 4
        log.append(f"percobaan {i}: 429, tunggu {w} dtk")
        time.sleep(w)
    return r, log

if st.button("Jalankan tes", type="primary"):
    for label, url, tampil_tabel in TESTS:
        st.subheader(label)
        t0 = time.time()
        try:
            r, log = get_with_retry(url)
            if log:
                st.caption(" | ".join(log))
            st.write(f"HTTP **{r.status_code}** | {time.time()-t0:.2f} dtk | {len(r.content):,} byte")
            try:
                js = r.json()
                data = js.get("data") or []
                st.write(f"count: **{js.get('count')}** | baris data: **{len(data)}** | error: {js.get('error')}")
                if data:
                    st.write("Kode komoditas unik:", len({d.get("cmdCode") for d in data}),
                             "| classificationCode:", sorted({d.get("classificationCode") for d in data}))
                    if tampil_tabel:
                        st.dataframe([{k: d.get(k) for k in
                            ["period", "flowCode", "cmdCode", "classificationCode",
                             "primaryValue", "netWgt", "isReported", "isAggregate"]}
                            for d in data[:30]], use_container_width=True)
                else:
                    st.text(r.text[:400])
            except ValueError:
                st.text(r.text[:400])
        except Exception as e:
            st.error(f"{type(e).__name__}: {e}")
        time.sleep(JEDA)

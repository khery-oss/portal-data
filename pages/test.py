import re
import time
import requests
import streamlit as st

st.set_page_config(page_title="Tes Batas Comtrade v2", layout="wide")
st.title("Tes Batas Preview Comtrade (dengan jeda dan retry)")

H = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
B = "https://comtradeapi.un.org/public/v1/preview/C/A/HS"
F = "reporterCode=360&partnerCode=0&partner2Code=0&motCode=0&customsCode=C00&flowCode=X,M"
JEDA_ANTAR_TES = 6
MAX_RETRY = 4

TESTS = [
    ("A. 1511, 1 periode", f"{B}?{F}&period=2022&cmdCode=1511"),
    ("B. 1511, 12 periode (2012-2023)", f"{B}?{F}&period=2012,2013,2014,2015,2016,2017,2018,2019,2020,2021,2022,2023&cmdCode=1511"),
    ("C. TOTAL, 2024 dan 2025", f"{B}?{F}&period=2024,2025&cmdCode=TOTAL"),
    ("D. Semua bab 2 digit (AG2), 2022", f"{B}?{F}&period=2022&cmdCode=AG2"),
    ("E. 2709,1511,2701, 2022", f"{B}?{F}&period=2022&cmdCode=2709,1511,2701"),
]

def get_with_retry(url):
    log = []
    for i in range(1, MAX_RETRY + 1):
        r = requests.get(url, headers=H, timeout=40)
        if r.status_code != 429:
            return r, log
        m = re.search(r"in (\d+) second", r.text)
        tunggu = int(m.group(1)) + 1 if m else 4
        log.append(f"percobaan {i}: 429, menunggu {tunggu} detik")
        time.sleep(tunggu)
    return r, log

if st.button("Jalankan tes", type="primary"):
    for label, url in TESTS:
        st.subheader(label)
        st.code(url)
        t0 = time.time()
        try:
            r, log = get_with_retry(url)
            if log:
                st.caption(" | ".join(log))
            st.write(f"HTTP **{r.status_code}** | {time.time()-t0:.2f} detik | {len(r.content):,} byte")
            try:
                js = r.json()
                data = js.get("data") or []
                st.write(f"count: **{js.get('count')}** | baris data: **{len(data)}** | error: {js.get('error')}")
                if data:
                    st.write("Periode:", sorted({d.get("period") for d in data}))
                    st.write("Jumlah kode komoditas unik:", len({d.get("cmdCode") for d in data}))
                    st.write("classificationCode:", sorted({d.get("classificationCode") for d in data}))
                    ringkas = [{k: d.get(k) for k in
                        ["period", "flowCode", "cmdCode", "classificationCode",
                         "primaryValue", "netWgt", "isReported", "isAggregate"]} for d in data[:30]]
                    st.dataframe(ringkas, use_container_width=True)
                else:
                    st.text(r.text[:600])
            except ValueError:
                st.text(r.text[:600])
        except Exception as e:
            st.error(f"{type(e).__name__}: {e}")
        time.sleep(JEDA_ANTAR_TES)

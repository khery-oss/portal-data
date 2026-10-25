import re
import time
import requests
import streamlit as st

st.set_page_config(page_title="Tes Comtrade v4", layout="wide")
st.title("Tes Comtrade v4: data sebelum 1990")

H = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
B = "https://comtradeapi.un.org/public/v1/preview/C/A"
F = "reporterCode=360&partnerCode=0&partner2Code=0&motCode=0&customsCode=C00&flowCode=X,M&cmdCode=TOTAL"
JEDA = 6
MAX_RETRY = 4

TESTS = [
    ("A. HS 1989", f"{B}/HS?{F}&period=1989"),
    ("B. HS 1988", f"{B}/HS?{F}&period=1988"),
    ("C. SITC Rev.3 (S3) 1985", f"{B}/S3?{F}&period=1985"),
    ("D. SITC Rev.2 (S2) 1976", f"{B}/S2?{F}&period=1976"),
    ("E. SITC Rev.1 (S1) 1965", f"{B}/S1?{F}&period=1965"),
    ("F. SITC Rev.1 (S1) 1962", f"{B}/S1?{F}&period=1962"),
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
    for label, url in TESTS:
        st.subheader(label)
        try:
            r, log = get_with_retry(url)
            if log:
                st.caption(" | ".join(log))
            try:
                js = r.json()
                data = js.get("data") or []
                st.write(f"HTTP **{r.status_code}** | count: **{js.get('count')}** | "
                         f"baris data: **{len(data)}** | error: {js.get('error')}")
                if data:
                    st.write("classificationCode:", sorted({d.get("classificationCode") for d in data}),
                             "| arah:", sorted({d.get("flowCode") for d in data}),
                             "| primaryValue:", [d.get("primaryValue") for d in data])
                else:
                    st.text(r.text[:300])
            except ValueError:
                st.write(f"HTTP **{r.status_code}**")
                st.text(r.text[:300])
        except Exception as e:
            st.error(f"{type(e).__name__}: {e}")
        time.sleep(JEDA)

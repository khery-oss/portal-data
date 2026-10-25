import time
import requests
import streamlit as st

st.set_page_config(page_title="Tes Batas Comtrade", layout="wide")
st.title("Tes Batas Preview Comtrade")

H = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
B = "https://comtradeapi.un.org/public/v1/preview/C/A/HS"
F = "reporterCode=360&partnerCode=0&partner2Code=0&motCode=0&customsCode=C00&flowCode=X,M"

TESTS = [
    ("A. Satu komoditas (1511 minyak sawit), 1 periode", f"{B}?{F}&period=2022&cmdCode=1511"),
    ("B. Satu komoditas, 12 periode (2012-2023)", f"{B}?{F}&period=2012,2013,2014,2015,2016,2017,2018,2019,2020,2021,2022,2023&cmdCode=1511"),
    ("C. Tahun terbaru (2024, 2025)", f"{B}?{F}&period=2024,2025&cmdCode=TOTAL"),
    ("D. Semua bab 2 digit (AG2), 1 periode", f"{B}?{F}&period=2022&cmdCode=AG2"),
    ("E. Beberapa komoditas sekaligus (2709,1511,2701), 1 periode", f"{B}?{F}&period=2022&cmdCode=2709,1511,2701"),
]

if st.button("Jalankan tes", type="primary"):
    for label, url in TESTS:
        st.subheader(label)
        st.code(url)
        t0 = time.time()
        try:
            r = requests.get(url, headers=H, timeout=40)
            st.write(f"HTTP **{r.status_code}** | {time.time()-t0:.2f} detik | {len(r.content):,} byte")
            try:
                js = r.json()
                data = js.get("data") or []
                st.write(f"count: **{js.get('count')}** | baris di data: **{len(data)}** | error: {js.get('error')}")
                if data:
                    yrs = sorted({d.get("period") for d in data})
                    st.write("Periode yang kembali:", yrs)
                    st.write("Kode komoditas:", sorted({d.get("cmdCode") for d in data})[:15])
                    st.write("classificationCode:", sorted({d.get("classificationCode") for d in data}))
                    st.write("Flag isAggregate:", sorted({str(d.get("isAggregate")) for d in data}))
                    st.json({k: data[0][k] for k in
                        ["period","flowCode","cmdCode","classificationCode","primaryValue","netWgt","isReported","isAggregate"]})
                else:
                    st.text(r.text[:600])
            except ValueError:
                st.text(r.text[:600])
        except Exception as e:
            st.error(f"{type(e).__name__}: {e}")

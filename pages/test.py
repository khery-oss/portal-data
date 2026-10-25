import time
import requests
import streamlit as st

st.set_page_config(page_title="Tes Akses Comtrade", layout="wide")
st.title("Tes Aksesibilitas UN Comtrade dari Streamlit Cloud")

HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}

try:
    KEY = st.secrets["COMTRADE_API_KEY"]
except (KeyError, FileNotFoundError):
    KEY = None

BASE_PARAMS = (
    "reporterCode=360&period=2022&cmdCode=TOTAL&flowCode=X,M"
    "&partnerCode=0&partner2Code=0&motCode=0&customsCode=C00"
)

TESTS = [
    ("1. Referensi HS (katalog komoditas live)",
     "https://comtradeapi.un.org/files/v1/app/reference/HS.json", {}),
    ("2. Public preview, tanpa key (total X/M Indonesia 2022)",
     f"https://comtradeapi.un.org/public/v1/preview/C/A/HS?{BASE_PARAMS}", {}),
]
if KEY:
    TESTS.append((
        "3. Data API dengan key (total X/M Indonesia 2022)",
        f"https://comtradeapi.un.org/data/v1/get/C/A/HS?{BASE_PARAMS}",
        {"Ocp-Apim-Subscription-Key": KEY},
    ))
else:
    st.info("COMTRADE_API_KEY belum ada di secrets, tes nomor 3 dilewati.")

if st.button("Jalankan tes", type="primary"):
    for label, url, extra in TESTS:
        st.subheader(label)
        st.code(url)
        t0 = time.time()
        try:
            r = requests.get(url, headers={**HEADERS, **extra}, timeout=30)
            dt = time.time() - t0
            st.write(f"HTTP **{r.status_code}** | {dt:.2f} detik | "
                     f"Content-Type: `{r.headers.get('Content-Type')}` | "
                     f"Ukuran: {len(r.content):,} byte")
            try:
                js = r.json()
                if isinstance(js, dict):
                    st.write("Kunci JSON:", list(js.keys()))
                    data = js.get("data") or js.get("results")
                    if isinstance(data, list):
                        st.write(f"Jumlah baris data: **{len(data)}**")
                        if data:
                            st.json(data[0])
                    if js.get("error") or js.get("message"):
                        st.warning(js.get("error") or js.get("message"))
                elif isinstance(js, list):
                    st.write(f"Jumlah elemen: **{len(js)}**")
                st.text(r.text[:500])
            except ValueError:
                st.text(r.text[:500])
            denied = r.headers.get("x-deny-reason")
            if denied:
                st.error(f"x-deny-reason: {denied}")
        except Exception as e:
            st.error(f"{type(e).__name__}: {e}")

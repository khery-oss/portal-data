import time
import requests
import streamlit as st

st.set_page_config(page_title="Tes UN SDG v3", layout="wide")
st.title("Tes UN SDG v3: ketersediaan Indonesia")

H = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36", "Accept": "application/json"}
BASE = "https://unstats.un.org/sdgapi/v1/sdg"

def ringkas(url):
    st.code(url)
    t0 = time.time()
    try:
        r = requests.get(url, headers=H, timeout=40)
    except Exception as e:
        st.error(f"{type(e).__name__}: {e}")
        return None
    st.write(f"HTTP **{r.status_code}** | {time.time()-t0:.2f} dtk | {len(r.content):,} byte")
    if r.status_code != 200:
        st.text(r.text[:200])
        return None
    try:
        js = r.json()
    except ValueError:
        st.text(r.text[:200])
        return None
    if isinstance(js, dict):
        st.write("Kunci:", list(js.keys()), "| totalElements:", js.get("totalElements"),
                 "| totalPages:", js.get("totalPages"))
        data = js.get("data")
        if isinstance(data, list) and data:
            seri = {d.get("series") for d in data if isinstance(d, dict)}
            st.write(f"Baris di halaman: {len(data)} | seri berbeda di halaman ini: {len(seri)}")
            st.write("Contoh seri:", sorted(s for s in seri if s)[:8])
            st.write("geoAreaCode berbeda:", sorted({str(d.get('geoAreaCode')) for d in data})[:5])
        else:
            st.text(str(js)[:300])
    elif isinstance(js, list):
        st.write(f"Daftar, {len(js)} entri.")
        if js:
            st.text(str(js[0])[:300])
    return js

if st.button("Jalankan tes", type="primary"):
    st.header("A. Kandidat endpoint ketersediaan")
    for u in [
        f"{BASE}/Series/SL_TLF_UEM/GeoAreas",
        f"{BASE}/Series/Data?areaCode=360&pageSize=5",
        f"{BASE}/Goal/Data?goalCode=8&areaCode=360&pageSize=5",
        f"{BASE}/Indicator/Data?indicator=8.5.2&areaCode=360&pageSize=5",
        f"{BASE}/GeoArea/List",
    ]:
        ringkas(u)
        time.sleep(1)

    st.header("B. Kecepatan pemindaian per seri (10 seri pertama dari katalog)")
    daftar = requests.get(f"{BASE}/Series/List", headers=H, timeout=40).json()
    t0, hasil = time.time(), []
    for s in daftar[:10]:
        try:
            r = requests.get(f"{BASE}/Series/Data?seriesCode={s['code']}&areaCode=360&pageSize=1",
                             headers=H, timeout=40)
            hasil.append((s["code"], r.status_code, r.json().get("totalElements") if r.status_code == 200 else None))
        except Exception as e:
            hasil.append((s["code"], type(e).__name__, None))
        time.sleep(0.5)
    dt = time.time() - t0
    st.write(hasil)
    st.write(f"10 seri: {dt:.1f} dtk | perkiraan 713 seri: {dt/10*713/60:.1f} menit")

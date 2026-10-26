import time
import requests
import pandas as pd
import streamlit as st
from collections import Counter

st.set_page_config(page_title="Tes UN SDG v2", layout="wide")
st.title("Tes UN SDG v2: halaman, ketersediaan Indonesia, sumber")

H = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36", "Accept": "application/json"}
BASE = "https://unstats.un.org/sdgapi/v1/sdg"

def get(url):
    return requests.get(url, headers=H, timeout=40)

def tampil(r, panjang=500):
    st.write(f"HTTP **{r.status_code}** | {len(r.content):,} byte")
    try:
        js = r.json()
        if isinstance(js, list):
            st.write(f"Daftar, {len(js)} entri. Contoh entri pertama:")
            st.json(js[0] if js else {})
        else:
            st.write("Kunci:", list(js.keys()))
            return js
    except Exception:
        st.text(r.text[:panjang])
    return None

if st.button("Jalankan tes", type="primary"):
    # A. Mekanisme halaman
    st.header("A. Paginasi (SL_TLF_UEM, pageSize=50)")
    hasil_hal = {}
    for p in (1, 2, 5):
        r = get(f"{BASE}/Series/Data?seriesCode=SL_TLF_UEM&areaCode=360&pageSize=50&page={p}")
        js = r.json() if r.status_code == 200 else {}
        data = js.get("data") or []
        kunci = [(d["timePeriodStart"], tuple(sorted((d.get("dimensions") or {}).items()))) for d in data]
        hasil_hal[p] = kunci
        st.write(f"page={p}: HTTP {r.status_code} | pageNumber={js.get('pageNumber')} | "
                 f"totalPages={js.get('totalPages')} | totalElements={js.get('totalElements')} | baris={len(data)}")
        time.sleep(1)
    st.write("Halaman 1 dan 2 tidak berbagi baris:", not (set(hasil_hal[1]) & set(hasil_hal[2])))

    # B. Endpoint ketersediaan Indonesia
    st.header("B. Kandidat endpoint daftar seri untuk Indonesia")
    kandidat = [
        f"{BASE}/GeoArea/360/Series",
        f"{BASE}/Series/List?areaCode=360",
        f"{BASE}/Series/List?geoAreaCode=360",
        f"{BASE}/GeoArea/360",
    ]
    for u in kandidat:
        st.code(u)
        try:
            r = get(u)
            js = tampil(r, 300)
            if isinstance(js, dict):
                st.text(str(js)[:300])
        except Exception as e:
            st.error(f"{type(e).__name__}: {e}")
        time.sleep(1)

    # C. Goal, detail seri, source, footnotes
    st.header("C. Goal/List dan detail seri")
    r = get(f"{BASE}/Goal/List?includechildren=false")
    tampil(r)
    time.sleep(1)
    r = get(f"{BASE}/Series/SL_TLF_UEM")
    st.subheader("Series/SL_TLF_UEM")
    tampil(r)
    time.sleep(1)

    st.subheader("Isi source, footnotes, geoInfoUrl, valueType, upperBound/lowerBound pada SL_TLF_UEM")
    r = get(f"{BASE}/Series/Data?seriesCode=SL_TLF_UEM&areaCode=360&pageSize=3")
    for d in (r.json().get("data") or [])[:2]:
        st.json({k: d.get(k) for k in ["source", "footnotes", "geoInfoUrl", "valueType",
                                        "time_detail", "upperBound", "lowerBound", "basePeriod", "timeCoverage"]})
    time.sleep(1)

    # D. Dimensi Activity
    st.header("D. Dimensi Activity")
    for k in ["NV_IND_MANF", "EN_ATM_CO2MVA"]:
        r = get(f"{BASE}/Series/Data?seriesCode={k}&areaCode=360&pageSize=500")
        data = r.json().get("data") or []
        dims = {}
        for d in data:
            for dk, dv in (d.get("dimensions") or {}).items():
                dims.setdefault(dk, Counter())[dv] += 1
        st.write(k, {dk: dict(c.most_common(10)) for dk, c in dims.items()})
        time.sleep(1)

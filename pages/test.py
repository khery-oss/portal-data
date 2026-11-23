import time
import requests
import pandas as pd
import streamlit as st

st.set_page_config(page_title="Tes BPS WebAPI v2", layout="wide")
st.title("Tes BPS WebAPI v2")

try:
    KEY = st.secrets["BPS_API_KEY"]
except Exception:
    st.error("BPS_API_KEY belum ada di secrets.")
    st.stop()

BASE = "https://webapi.bps.go.id/v1/api/list"
H = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}

def panggil(**params):
    t0 = time.time()
    try:
        r = requests.get(BASE, params={"key": KEY, **params}, headers=H, timeout=60)
        js = r.json()
        return r.status_code, js, time.time() - t0
    except Exception as e:
        return None, {"galat": type(e).__name__}, time.time() - t0

def ringkas(label, **params):
    kode, js, dt = panggil(**params)
    st.subheader(label)
    st.write(f"HTTP **{kode}** | {dt:.2f} dtk | parameter: {', '.join(f'{k}={v}' for k, v in params.items())}")
    if isinstance(js, dict):
        st.write("status:", js.get("status"), "| pesan:", str(js.get("message"))[:300].replace(KEY, "***"))
        d = js.get("data")
        if isinstance(d, list) and len(d) == 2 and isinstance(d[1], list):
            st.write("meta:", d[0], "| jumlah di halaman:", len(d[1]))
            st.write("tiga pertama:", d[1][:3])
        elif js.get("datacontent") is not None or js.get("tahun") is not None:
            st.write("kunci:", list(js.keys()))
            for k in ("var", "turvar", "vervar", "tahun", "turtahun"):
                v = js.get(k)
                st.write(f"{k}: {len(v) if isinstance(v, list) else v}", v[:3] if isinstance(v, list) else "")
            dc = js.get("datacontent")
            st.write("datacontent jumlah:", len(dc) if dc else 0, "| contoh:", list(dc.items())[:5] if isinstance(dc, dict) else dc)
    return js

if st.button("Jalankan tes", type="primary"):
    st.header("A. Domain")
    ringkas("A1", model="domain", type="all")
    time.sleep(1)
    ringkas("A2", model="domain", type="prov")
    time.sleep(1)

    st.header("B. Daftar nilai untuk variabel 70, domain 0000")
    j_th = ringkas("B1 periode", model="th", domain="0000", var=70)
    time.sleep(1)
    ringkas("B2 variabel vertikal", model="vervar", domain="0000", var=70)
    time.sleep(1)
    ringkas("B3 variabel turunan", model="turvar", domain="0000", var=70)
    time.sleep(1)
    ringkas("B4 periode turunan", model="turth", domain="0000", var=70)
    time.sleep(1)

    th_id = None
    d = j_th.get("data") if isinstance(j_th, dict) else None
    if isinstance(d, list) and len(d) == 2 and d[1]:
        th_id = d[1][-1].get("th_id")

    st.header("C. Data variabel 70")
    ringkas("C1 tanpa parameter tambahan", model="data", domain="0000", var=70)
    time.sleep(1)
    ringkas("C2 dengan lang=ind", model="data", domain="0000", var=70, lang="ind")
    time.sleep(1)
    if th_id:
        ringkas(f"C3 dengan th={th_id}", model="data", domain="0000", var=70, th=th_id)
        time.sleep(1)
        ringkas(f"C4 dengan th={th_id} dan lang=ind", model="data", domain="0000", var=70, th=th_id, lang="ind")
        time.sleep(1)

    st.header("D. Penyaringan katalog variabel")
    ringkas("D1 subject=30 (Kesehatan)", model="var", domain="0000", subject=30)
    time.sleep(1)
    ringkas("D2 keyword=kemiskinan", model="var", domain="0000", keyword="kemiskinan")
    time.sleep(1)

    st.header("E. Kecepatan halaman katalog")
    t0 = time.time()
    for p in range(1, 6):
        panggil(model="var", domain="0000", page=p)
    st.write(f"5 halaman berurutan: {time.time() - t0:.1f} dtk")

import time
import requests
import pandas as pd
import streamlit as st

st.set_page_config(page_title="Tes BPS WebAPI", layout="wide")
st.title("Tes struktur BPS WebAPI")

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
    except Exception as e:
        return None, None, type(e).__name__, time.time() - t0
    try:
        js = r.json()
        return r.status_code, js, None, time.time() - t0
    except ValueError:
        return r.status_code, None, r.text[:300].replace(KEY, "***"), time.time() - t0

def lapor(judul, kode, js, galat, dt):
    st.subheader(judul)
    st.write(f"HTTP **{kode}** | {dt:.2f} dtk" + (f" | galat: {galat}" if galat else ""))
    if isinstance(js, dict):
        st.write("Kunci atas:", list(js.keys()), "| status:", js.get("status"), "| ketersediaan:", js.get("data-availability"))

if st.button("Jalankan tes", type="primary"):
    kode, js, galat, dt = panggil(model="domain", type="all")
    lapor("A. Daftar domain", kode, js, galat, dt)
    if isinstance(js, dict) and isinstance(js.get("data"), list) and len(js["data"]) == 2:
        st.write("Meta:", js["data"][0], "| jumlah:", len(js["data"][1]))
        st.write("Lima pertama:", js["data"][1][:5])
    time.sleep(1)

    kode, js, galat, dt = panggil(model="subject", domain="0000")
    lapor("B. Daftar subjek (domain 0000)", kode, js, galat, dt)
    if isinstance(js, dict) and isinstance(js.get("data"), list) and len(js["data"]) == 2:
        st.write("Meta:", js["data"][0], "| jumlah:", len(js["data"][1]))
        st.write("Sepuluh pertama:", js["data"][1][:10])
    time.sleep(1)

    kode, js, galat, dt = panggil(model="var", domain="0000", page=1)
    lapor("C. Daftar variabel (halaman 1)", kode, js, galat, dt)
    var_id = None
    if isinstance(js, dict) and isinstance(js.get("data"), list) and len(js["data"]) == 2:
        st.write("Meta:", js["data"][0], "| baris di halaman:", len(js["data"][1]))
        st.dataframe(pd.DataFrame(js["data"][1]).head(10), use_container_width=True)
        if js["data"][1]:
            var_id = js["data"][1][0].get("var_id")
    time.sleep(1)
    for nama in ("perpage", "per_page"):
        kode, js2, galat, dt = panggil(model="var", domain="0000", page=1, **{nama: 100})
        n = len(js2["data"][1]) if isinstance(js2, dict) and isinstance(js2.get("data"), list) and len(js2["data"]) == 2 else None
        st.write(f"Parameter `{nama}=100`: HTTP {kode} | baris: {n}")
        time.sleep(1)

    if var_id:
        kode, js, galat, dt = panggil(model="data", domain="0000", var=var_id)
        lapor(f"D. Data variabel {var_id} tanpa parameter tahun", kode, js, galat, dt)
        if isinstance(js, dict):
            for k in ("var", "turvar", "vervar", "tahun", "turtahun"):
                v = js.get(k)
                st.write(f"{k}: {len(v) if isinstance(v, list) else v}", (v[:3] if isinstance(v, list) else ""))
            dc = js.get("datacontent")
            st.write("labelvervar:", js.get("labelvervar"), "| last_update:", js.get("last_update"))
            st.write("datacontent:", type(dc).__name__, "| jumlah:", len(dc) if dc else 0)
            if isinstance(dc, dict):
                st.write("Contoh kunci dan nilai:", list(dc.items())[:6])
            tahun = js.get("tahun") or []
            if tahun:
                time.sleep(1)
                k2, js3, g3, d3 = panggil(model="data", domain="0000", var=var_id, th=tahun[0].get("val"))
                dc3 = js3.get("datacontent") if isinstance(js3, dict) else None
                st.write(f"E. Dengan th={tahun[0].get('val')}: HTTP {k2} | jumlah datacontent: {len(dc3) if dc3 else 0}")

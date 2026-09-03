import pandas as pd
import requests
import streamlit as st

st.set_page_config(page_title="Detektor Live BPS", layout="wide")
st.title("🔍 Detektor Variabel Aktif BPS Pusat")

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    )
}
BPS_APP_ID = st.secrets["BPS_APP_ID"]

# 1. Ambil daftar variabel resmi yang saat ini benar-benar ada di BPS Pusat (0000)
@st.cache_data(ttl=3600)
def fetch_live_variables():
  url = f"https://webapi.bps.go.id/v1/api/list/model/var/lang/ind/domain/0000/page/1/key/{BPS_APP_ID}/"
  try:
    r = requests.get(url, headers=HEADERS, timeout=20)
    data = r.json()
    if data.get("status") == "OK" and len(data.get("data", [])) > 1:
      # Ambil var_id, judul, dan subjeknya
      return [
          {"var_id": item["var_id"], "title": item["title"]}
          for item in data["data"][1]
      ]
  except Exception:
    pass
  return []


live_vars = fetch_live_variables()

if not live_vars:
  st.error("Gagal membaca daftar variabel dari domain 0000.")
  st.stop()

# Buat dropdown dari variabel yang AKTIF saat ini
var_map = {f"ID {v['var_id']} - {v['title']}": v["var_id"] for v in live_vars}
pilihan_var = st.selectbox("Pilih Variabel yang Terdaftar Aktif:", list(var_map.keys()))
selected_var_id = var_map[pilihan_var]

# 2. Tarik data dari variabel tersebut
if st.button("Uji Tarik Variabel Ini", type="primary"):
  with st.spinner("Mengambil data..."):
    # Gunakan rentang 2021:2023
    url_data = f"https://webapi.bps.go.id/v1/api/list/model/data/lang/ind/domain/0000/var/{selected_var_id}/th/2021:2023/key/{BPS_APP_ID}/"
    try:
      res = requests.get(url_data, headers=HEADERS, timeout=25).json()

      st.write(f"**BPS Status:** `{res.get('status')}`")
      st.write(f"**Poin Data Ditemukan:** `{len(res.get('datacontent', {}))}`")

      if res.get("datacontent"):
        st.success("✅ VARIABEL INI MEMILIKI DATA!")
        st.json(dict(list(res.get("datacontent", {}).items())[:10]))
      else:
        st.warning("Variabel ini ada di katalog, tetapi tabel nilainya kosong pada 2021:2023.")
        with st.expander("Lihat Detail Metadata dari BPS"):
          st.json(res)
    except Exception as e:
      st.error(f"Error: {e}")

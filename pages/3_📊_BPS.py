import pandas as pd
import requests
import streamlit as st

st.set_page_config(page_title="BPS Test", layout="wide")
st.title("🛠️ Bedah Struktur Data BPS")

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    )
}
BPS_APP_ID = st.secrets["BPS_APP_ID"]

TEST_VARS = {
    "Persentase Penduduk Miskin (P0)": 191,
    "Garis Kemiskinan": 192,
    "Indeks Pembangunan Manusia (IPM)": 499,
    "Tingkat Pengangguran Terbuka (TPT)": 543,
}

pilihan = st.selectbox("Pilih Indikator:", list(TEST_VARS.keys()))
var_id = TEST_VARS[pilihan]

th_param = st.selectbox("Pilih th:", ["2021:2023", "2020:2022", "2022;2023"])

if st.button("Bedah Respons BPS", type="primary"):
  url = f"https://webapi.bps.go.id/v1/api/list/model/data/lang/ind/domain/0000/var/{var_id}/th/{th_param}/key/{BPS_APP_ID}/"

  try:
    r = requests.get(url, headers=HEADERS, timeout=25)
    res = r.json()

    st.write(f"**HTTP Status:** `{r.status_code}` | **BPS Status:** `{res.get('status')}`")
    st.write(f"**Jumlah Data Point:** `{len(res.get('datacontent', {}))}`")

    # Tampilkan seluruh komponen metadata yang dikirim server BPS
    col_a, col_b = st.columns(2)
    with col_a:
      st.markdown("**Daftar Kode Tahun (`tahun`):**")
      st.json(res.get("tahun", []))

      st.markdown("**Daftar Turunan Variabel (`turvar`):**")
      st.json(res.get("turvar", []))

    with col_b:
      st.markdown("**Daftar Wilayah/Klasifikasi (`vervar`):**")
      st.json(res.get("vervar", []))

      st.markdown("**Isi Data Mentah (`datacontent`):**")
      st.json(res.get("datacontent", {}))

  except Exception as e:
    st.error(f"Error: {e}")

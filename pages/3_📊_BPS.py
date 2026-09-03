import pandas as pd
import requests
import streamlit as st

st.set_page_config(page_title="BPS Test", layout="wide")
st.title("🛠️ Pengujian Endpoint BPS")

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    )
}
BPS_APP_ID = st.secrets["BPS_APP_ID"]

# Daftar indikator yang umum aktif di BPS Nasional
TEST_VARS = {
    "Persentase Penduduk Miskin (P0)": 191,
    "Garis Kemiskinan": 192,
    "Indeks Pembangunan Manusia (IPM)": 499,
    "Angka Harapan Hidup (AHH)": 501,
    "Tingkat Pengangguran Terbuka (TPT)": 543,
}

pilihan = st.selectbox("Pilih Indikator Uji:", list(TEST_VARS.keys()))
var_id = TEST_VARS[pilihan]

# Batasan resmi BPS: maksimal 3 tahun
th_param = st.selectbox("Rentang Tahun (Maks 3 Tahun):", ["2021:2023", "2020:2022", "2018:2020"])

if st.button("Uji Tarik Data", type="primary"):
  url = f"https://webapi.bps.go.id/v1/api/list/model/data/lang/ind/domain/0000/var/{var_id}/th/{th_param}/key/{BPS_APP_ID}/"

  try:
    r = requests.get(url, headers=HEADERS, timeout=25)
    res = r.json()

    if res.get("status") == "OK":
      content = res.get("datacontent", {})
      st.success(f"Berhasil! Server mengembalikan {len(content)} data poin.")

      vervar = {
          str(item["val"]): item["label"] for item in res.get("vervar", [])
      }
      tahun = {str(item["val"]): item["label"] for item in res.get("tahun", [])}

      rows = []
      for k, v in content.items():
        k_str = str(k)
        label_v = next(
            (v_lbl for v_val, v_lbl in vervar.items() if k_str.startswith(v_val)),
            "Nasional",
        )
        label_t = next(
            (t_lbl for t_val, t_lbl in tahun.items() if t_val in k_str), "-"
        )
        rows.append(
            {"Klasifikasi / Wilayah": label_v, "Tahun": label_t, "Nilai": v}
        )

      df = pd.DataFrame(rows)
      st.dataframe(df, use_container_width=True)
    else:
      st.error(f"Gagal: {res.get('message', res.get('status'))}")
      st.json(res)
  except Exception as e:
    st.error(f"Terjadi error: {e}")

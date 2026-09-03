import io
import pandas as pd
import requests
import streamlit as st

st.set_page_config(page_title="BPS Data Explorer", layout="wide")
st.title("📊 Portal Data WebAPI BPS")
st.write(
    "Eksplorasi data resmi BPS dengan deteksi periode data otomatis langsung"
    " dari server."
)

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    )
}
BPS_APP_ID = st.secrets["BPS_APP_ID"]


# 1. Ambil Variabel yang Aktif di Katalog BPS Pusat
@st.cache_data(ttl=3600)
def get_bps_catalog():
  url = f"https://webapi.bps.go.id/v1/api/list/model/var/lang/ind/domain/0000/page/1/key/{BPS_APP_ID}/"
  try:
    r = requests.get(url, headers=HEADERS, timeout=20)
    data = r.json()
    if data.get("status") == "OK" and len(data.get("data", [])) > 1:
      return [
          {"var_id": item["var_id"], "title": item["title"]}
          for item in data["data"][1]
      ]
  except Exception:
    pass
  return []


catalog = get_bps_catalog()

if not catalog:
  st.error("Gagal terhubung ke katalog BPS. Silakan periksa koneksi.")
  st.stop()

var_options = {f"{v['title']} (ID: {v['var_id']})": v["var_id"] for v in catalog}
selected_label = st.selectbox(
    "Pilih Indikator / Variabel:", list(var_options.keys())
)
var_id = var_options[selected_label]

if st.button("📊 Ambil Data Tabel", type="primary"):
  with st.spinner("Memeriksa periode tahun yang tersedia dari server BPS..."):
    # Langkah 1: Cek ketersediaan tahun pada variabel ini
    meta_url = f"https://webapi.bps.go.id/v1/api/view/model/var/lang/ind/domain/0000/var/{var_id}/key/{BPS_APP_ID}/"
    valid_years = []

    try:
      r_meta = requests.get(meta_url, headers=HEADERS, timeout=20).json()
      if r_meta.get("status") == "OK" and "tahun" in r_meta:
        # Ambil maksimal 3 tahun terbaru yang terdaftar
        valid_years = [str(item["val"]) for item in r_meta["tahun"]][-3:]
    except Exception:
      pass

    # Jika metadata spesifik tidak ada, gunakan fallback tahun terdekat
    if not valid_years:
      valid_years = ["2023", "2022", "2021"]

    th_param = ";".join(valid_years)

  with st.spinner(f"Menarik angka data untuk tahun {th_param}..."):
    data_url = f"https://webapi.bps.go.id/v1/api/list/model/data/lang/ind/domain/0000/var/{var_id}/th/{th_param}/key/{BPS_APP_ID}/"

    try:
      r_data = requests.get(data_url, headers=HEADERS, timeout=25).json()

      if r_data.get("status") == "OK":
        content = r_data.get("datacontent", {})

        if content:
          vervar = {
              str(item["val"]): item["label"]
              for item in r_data.get("vervar", [])
          }
          tahun = {
              str(item["val"]): item["label"]
              for item in r_data.get("tahun", [])
          }

          rows = []
          for k, v in content.items():
            if v is not None:
              k_str = str(k)
              lbl_wilayah = next(
                  (
                      v_lbl
                      for v_val, v_lbl in vervar.items()
                      if k_str.startswith(v_val)
                  ),
                  "Nasional",
              )
              lbl_tahun = next(
                  (t_lbl for t_val, t_lbl in tahun.items() if t_val in k_str),
                  "-",
              )
              rows.append({
                  "Wilayah / Rincian": lbl_wilayah,
                  "Tahun": lbl_tahun,
                  "Nilai": v,
              })

          df = pd.DataFrame(rows)

          st.divider()
          st.subheader(f"📈 {selected_label}")

          c1, c2 = st.columns(2)
          c1.download_button(
              "📥 Unduh CSV",
              df.to_csv(index=False).encode("utf-8"),
              f"bps_{var_id}.csv",
              "text/csv",
          )
          buf = io.BytesIO()
          with pd.ExcelWriter(buf, engine="openpyxl") as writer:
            df.to_excel(writer, index=False, sheet_name="Data BPS")
          c2.download_button(
              "📊 Unduh Excel (.xlsx)",
              buf.getvalue(),
              f"bps_{var_id}.xlsx",
              "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
          )

          st.dataframe(df, use_container_width=True)
        else:
          st.warning(
              "Tabel ini tidak memiliki rekaman nilai pada WebAPI BPS."
              " Kemungkinan data hanya dirilis dalam format buku/publikasi PDF"
              " oleh BPS."
          )
          with st.expander("Detail Respons Server BPS"):
            st.json(r_data)
      else:
        st.error(f"Pesan BPS: {r_data.get('message', r_data.get('status'))}")
    except Exception as e:
      st.error(f"Terjadi kesalahan saat memproses data: {e}")

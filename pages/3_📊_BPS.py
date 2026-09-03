import io
import pandas as pd
import requests
import streamlit as st

st.set_page_config(page_title="BPS Data - IndoEcon Explorer", layout="wide")

st.title("📊 Badan Pusat Statistik (BPS) Explorer")
st.write(
    "Eksplorasi data statistik resmi dari level **Nasional**, **Provinsi**,"
    " hingga **Kabupaten/Kota** via WebAPI BPS."
)

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    )
}

# Ambil App ID dari Secrets
if "BPS_APP_ID" in st.secrets:
  BPS_APP_ID = st.secrets["BPS_APP_ID"]
else:
  st.error(
      "⚠️ Kunci `BPS_APP_ID` belum diatur di Streamlit Secrets (Manage app >"
      " Settings > Secrets)."
  )
  st.stop()

# Daftar Domain Provinsi Resmi BPS
PROVINCES = {
    "Nasional / Seluruh Indonesia": "0000",
    "Aceh": "1100",
    "Sumatera Utara": "1200",
    "Sumatera Barat": "1300",
    "Riau": "1400",
    "Jambi": "1500",
    "Sumatera Selatan": "1600",
    "Bengkulu": "1700",
    "Lampung": "1800",
    "Kep. Bangka Belitung": "1900",
    "Kep. Riau": "2100",
    "DKI Jakarta": "3100",
    "Jawa Barat": "3200",
    "Jawa Tengah": "3300",
    "DI Yogyakarta": "3400",
    "Jawa Timur": "3500",
    "Banten": "3600",
    "Bali": "5100",
    "Nusa Tenggara Barat": "5200",
    "Nusa Tenggara Timur": "5300",
    "Kalimantan Barat": "6100",
    "Kalimantan Tengah": "6200",
    "Kalimantan Selatan": "6300",
    "Kalimantan Timur": "6400",
    "Kalimantan Utara": "6500",
    "Sulawesi Utara": "7100",
    "Sulawesi Tengah": "7200",
    "Sulawesi Selatan": "7300",
    "Sulawesi Tenggara": "7400",
    "Gorontalo": "7500",
    "Sulawesi Barat": "7600",
    "Maluku": "8100",
    "Maluku Utara": "8200",
    "Papua Barat": "9100",
    "Papua": "9400",
    "Papua Selatan": "9500",
    "Papua Tengah": "9600",
    "Papua Pegunungan": "9700",
    "Papua Barat Daya": "9800",
}


# Fungsi memuat daftar Kabupaten/Kota di dalam satu provinsi
@st.cache_data(ttl=86400)
def get_kabupaten_list(prov_code):
  url = f"https://webapi.bps.go.id/v1/api/list/model/domain/lang/ind/domain/{prov_code}/key/{BPS_APP_ID}/"
  try:
    r = requests.get(url, headers=HEADERS, timeout=15)
    res = r.json()
    if res.get("status") == "OK" and "data" in res and len(res["data"]) > 1:
      kab_dict = {}
      for item in res["data"][1]:
        kab_dict[item["domain_name"]] = item["domain_id"]
      return kab_dict
  except Exception:
    pass
  return {}


# Panel Navigasi Wilayah
col_wil1, col_wil2 = st.columns(2)

with col_wil1:
  selected_prov = st.selectbox("1. Pilih Tingkat / Provinsi:", list(PROVINCES.keys()))
  selected_prov_code = PROVINCES[selected_prov]

target_domain = selected_prov_code
wilayah_label = selected_prov

# Jika bukan nasional, tampilkan opsi pemilihan kabupaten/kota
if selected_prov_code != "0000":
  kab_options = get_kabupaten_list(selected_prov_code)
  with col_wil2:
    if kab_options:
      # Gabungkan opsi provinsi agregat dengan daftar kab/kota
      options_list = [f"Seluruh {selected_prov} (Tingkat Provinsi)"] + list(
          kab_options.keys()
      )
      selected_kab = st.selectbox(
          "2. Pilih Tingkat Pemerintahan:", options_list
      )

      if selected_kab != f"Seluruh {selected_prov} (Tingkat Provinsi)":
        target_domain = kab_options[selected_kab]
        wilayah_label = f"{selected_kab}, {selected_prov}"
    else:
      st.info(f"Menggunakan data agregat provinsi {selected_prov}.")

st.caption(f"📍 Domain aktif BPS: **{wilayah_label}** (Kode: `{target_domain}`)")


# 1. Ambil Subjek Statistik Berdasarkan Domain Terpilih
@st.cache_data(ttl=86400)
def get_bps_subjects(domain):
  url = f"https://webapi.bps.go.id/v1/api/list/model/subject/domain/{domain}/key/{BPS_APP_ID}/"
  try:
    r = requests.get(url, headers=HEADERS, timeout=15)
    res = r.json()
    if res.get("status") == "OK" and "data" in res:
      return {s["title"]: s["sub_id"] for s in res["data"][1]}
  except Exception:
    pass
  return {}


subjects = get_bps_subjects(target_domain)

if not subjects:
  st.warning(
      f"Tidak dapat memuat subjek data untuk wilayah {wilayah_label}. Pastikan"
      " App ID aktif atau coba wilayah lain."
  )
  st.stop()

col_sub1, col_sub2 = st.columns(2)

with col_sub1:
  selected_subject = st.selectbox("3. Pilih Subjek Data:", list(subjects.keys()))
  subject_id = subjects[selected_subject]


# 2. Ambil Daftar Variabel/Tabel Berdasarkan Subjek
@st.cache_data(ttl=86400)
def get_bps_variables(domain, sub_id):
  url = f"https://webapi.bps.go.id/v1/api/list/model/var/domain/{domain}/sub/{sub_id}/key/{BPS_APP_ID}/"
  try:
    r = requests.get(url, headers=HEADERS, timeout=15)
    res = r.json()
    if res.get("status") == "OK" and "data" in res:
      return {v["title"]: v["var_id"] for v in res["data"][1]}
  except Exception:
    pass
  return {}


variables = get_bps_variables(target_domain, subject_id)

if variables:
  with col_sub2:
    selected_var = st.selectbox("4. Pilih Indikator:", list(variables.keys()))
    var_id = variables[selected_var]

# Tambahkan pilihan tahun sebelum tombol tampilkan data
  selected_year = st.selectbox(
      "5. Pilih Tahun:",
      ["2024", "2023", "2022", "2021", "2020", "Semua Tahun Tersedia"],
  )

  if st.button("📊 Tampilkan Data", type="primary"):
    with st.spinner(f"Menarik data {selected_var}..."):
      # Jika memilih tahun tertentu, tambahkan parameter year
      if selected_year != "Semua Tahun Tersedia":
        data_url = f"https://webapi.bps.go.id/v1/api/list/model/data/lang/ind/domain/{target_domain}/var/{var_id}/year/{selected_year}/key/{BPS_APP_ID}/"
      else:
        data_url = f"https://webapi.bps.go.id/v1/api/list/model/data/lang/ind/domain/{target_domain}/var/{var_id}/key/{BPS_APP_ID}/"

      try:
        r_data = requests.get(data_url, headers=HEADERS, timeout=25)
        res_data = r_data.json()

        if res_data.get("status") == "OK":
          data_content = res_data.get("datacontent", {})
          if data_content:
            st.divider()
            st.subheader(f"📈 {selected_var}")

            # Parsing data dinamis BPS
            rows = [
                {"Kode Observasi": str(k), "Nilai": v}
                for k, v in data_content.items()
                if v is not None
            ]
            df = pd.DataFrame(rows)

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
                "📊 Unduh Excel",
                buf.getvalue(),
                f"bps_{var_id}.xlsx",
                "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            )

            st.dataframe(df, use_container_width=True)
          else:
            st.warning(
                f"Tabel terdaftar, namun tidak ada angka untuk tahun {selected_year}."
            )
        else:
          st.error(
              f"BPS menolak request (Status: {res_data.get('status')}). Indikator ini membutuhkan klasifikasi turunan khusus atau belum dialokasikan di API."
          )
      except Exception as e:
        st.error(f"Kesalahan koneksi: {e}")
else:
  st.info(f"Belum ada indikator tabel dinamis untuk subjek '{selected_subject}' di domain ini.")

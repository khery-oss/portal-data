import io
import pandas as pd
import requests
import streamlit as st

st.set_page_config(page_title="BPS Data - IndoEcon Explorer", layout="wide")

st.title("📊 Portal Data BPS (Badan Pusat Statistik)")
st.write(
    "Eksplorasi indikator makroekonomi, sosial, dan ketenagakerjaan resmi dari"
    " **WebAPI BPS**."
)

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    )
}

if "BPS_APP_ID" in st.secrets:
  BPS_APP_ID = st.secrets["BPS_APP_ID"]
else:
  st.error("⚠️ Masukkan `BPS_APP_ID` di Streamlit Secrets terlebih dahulu.")
  st.stop()

# Daftar Domain Wilayah
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
}

selected_prov = st.selectbox("1. Cakupan Wilayah:", list(PROVINCES.keys()))
domain_code = PROVINCES[selected_prov]


# Ambil Seluruh Subjek Resmi dari API
@st.cache_data(ttl=86400)
def get_all_subjects(domain):
  url = f"https://webapi.bps.go.id/v1/api/list/model/subject/domain/{domain}/key/{BPS_APP_ID}/"
  try:
    r = requests.get(url, headers=HEADERS, timeout=15)
    data = r.json()
    if data.get("status") == "OK" and len(data.get("data", [])) > 1:
      return {item["title"]: item["sub_id"] for item in data["data"][1]}
  except Exception:
    pass
  return {}


# Ambil Seluruh Variabel / Indikator berdasarkan Subjek
@st.cache_data(ttl=86400)
def get_variables_by_subject(domain, sub_id):
  url = f"https://webapi.bps.go.id/v1/api/list/model/var/domain/{domain}/sub/{sub_id}/key/{BPS_APP_ID}/"
  try:
    r = requests.get(url, headers=HEADERS, timeout=15)
    data = r.json()
    if data.get("status") == "OK" and len(data.get("data", [])) > 1:
      return {item["title"]: item["var_id"] for item in data["data"][1]}
  except Exception:
    pass
  return {}


subjects = get_all_subjects(domain_code)

if not subjects:
  st.warning(
      f"Tidak dapat memuat subjek data untuk wilayah {selected_prov}. Coba"
      " muat ulang beberapa saat lagi."
  )
  st.stop()

col_s1, col_s2 = st.columns(2)

with col_s1:
  selected_subject_name = st.selectbox(
      "2. Subjek / Topik Data:", list(subjects.keys())
  )
  sub_id = subjects[selected_subject_name]

variables_dict = get_variables_by_subject(domain_code, sub_id)

with col_s2:
  if variables_dict:
    selected_var_name = st.selectbox(
        "3. Indikator / Variabel Data:", list(variables_dict.keys())
    )
    var_id = variables_dict[selected_var_name]
  else:
    st.info("Tidak ada indikator dinamis pada subjek ini.")
    st.stop()

# Pembatasan Maksimal 3 Tahun Sesuai Kuota BPS
col_th1, col_th2 = st.columns(2)
with col_th1:
  th_awal = st.number_input(
      "Tahun Awal:", min_value=2015, max_value=2025, value=2022
  )
with col_th2:
  # Batasi tahun akhir maksimal 2 tahun setelah tahun awal (total 3 tahun)
  max_th_akhir = min(th_awal + 2, 2025)
  th_akhir = st.number_input(
      "Tahun Akhir (Maksimal 3 tahun dari tahun awal):",
      min_value=th_awal,
      max_value=max_th_akhir,
      value=max_th_akhir,
  )

st.caption(
    f"Rentang penarikan: **{th_awal} - {th_akhir}** (Batasan kuota WebAPI BPS:"
    " maks 3 tahun per request)."
)

if st.button("📊 Tampilkan Data BPS", type="primary"):
  with st.spinner(f"Menarik data {selected_var_name}..."):
    th_param = f"{int(th_awal)}:{int(th_akhir)}"
    url = f"https://webapi.bps.go.id/v1/api/list/model/data/lang/ind/domain/{domain_code}/var/{var_id}/th/{th_param}/key/{BPS_APP_ID}/"

    try:
      r = requests.get(url, headers=HEADERS, timeout=25)
      res = r.json()

      if res.get("status") == "OK":
        data_content = res.get("datacontent", {})
        vervar = {
            str(item["val"]): item["label"] for item in res.get("vervar", [])
        }
        tahun_dict = {
            str(item["val"]): item["label"] for item in res.get("tahun", [])
        }

        records = []
        for key, val in data_content.items():
          if val is not None:
            k_str = str(key)
            wilayah_label = selected_prov
            periode_label = "-"

            for v_code, v_label in vervar.items():
              if k_str.startswith(v_code):
                wilayah_label = v_label
                break

            for t_code, t_label in tahun_dict.items():
              if t_code in k_str:
                periode_label = t_label
                break

            records.append({
                "Rincian / Wilayah": wilayah_label,
                "Periode / Tahun": periode_label,
                "Nilai": val,
            })

        df = pd.DataFrame(records)

        if not df.empty:
          st.divider()
          st.subheader(f"📈 {selected_var_name}")
          st.caption(f"Cakupan: {selected_prov} | Periode: {th_param}")

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
          st.info(
              "Data tercatat di katalog, tetapi belum ada observasi angka pada"
              f" rentang tahun {th_param}."
          )
      else:
        st.warning(f"Respon BPS: {res.get('message', res.get('status'))}")
    except Exception as e:
      st.error(f"Terjadi kesalahan saat menghubungi server BPS: {e}")

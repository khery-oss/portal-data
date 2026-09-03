import io
import pandas as pd
import requests
import streamlit as st

st.set_page_config(page_title="BPS Data - IndoEcon Explorer", layout="wide")

st.title("📊 Indikator Strategis BPS")
st.write(
    "Akses langsung indikator pembangunan, makroekonomi, dan sosial resmi BPS"
    " dari tingkat **Nasional**, **Provinsi**, hingga **Kabupaten/Kota**."
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

# Daftar Domain Provinsi BPS
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


@st.cache_data(ttl=86400)
def get_kabupaten_list(prov_code):
  url = f"https://webapi.bps.go.id/v1/api/list/model/domain/lang/ind/domain/{prov_code}/key/{BPS_APP_ID}/"
  try:
    r = requests.get(url, headers=HEADERS, timeout=15)
    res = r.json()
    if res.get("status") == "OK" and "data" in res and len(res["data"]) > 1:
      return {item["domain_name"]: item["domain_id"] for item in res["data"][1]}
  except Exception:
    pass
  return {}


# 1. Pemilihan Wilayah Berjenjang
col_w1, col_w2 = st.columns(2)
with col_w1:
  selected_prov = st.selectbox("1. Pilih Tingkat / Provinsi:", list(PROVINCES.keys()))
  prov_code = PROVINCES[selected_prov]

target_domain = prov_code
wilayah_label = selected_prov

if prov_code != "0000":
  kab_options = get_kabupaten_list(prov_code)
  with col_w2:
    if kab_options:
      pilihan = [f"Seluruh {selected_prov} (Provinsi)"] + list(kab_options.keys())
      selected_kab = st.selectbox("2. Pilih Wilayah Spesifik:", pilihan)
      if selected_kab != f"Seluruh {selected_prov} (Provinsi)":
        target_domain = kab_options[selected_kab]
        wilayah_label = f"{selected_kab}, {selected_prov}"

st.caption(f"📍 Domain aktif BPS: **{wilayah_label}** (`{target_domain}`)")


# 2. Ambil Daftar Indikator Strategis
@st.cache_data(ttl=43200)
def get_indicators(domain):
  # Endpoint indikator strategis resmi
  url = f"https://webapi.bps.go.id/v1/api/list/model/indicator/domain/{domain}/lang/ind/key/{BPS_APP_ID}/"
  try:
    r = requests.get(url, headers=HEADERS, timeout=20)
    res = r.json()
    if res.get("status") == "OK" and "data" in res and len(res["data"]) > 1:
      return res["data"][1]
  except Exception:
    pass
  return []


indicator_list = get_indicators(target_domain)

if not indicator_list:
  st.warning(
      f"Tidak ada daftar indikator strategis langsung untuk {wilayah_label}. Coba"
      " pilih tingkat Provinsi atau Nasional."
  )
  st.stop()

# Buat mapping nama indikator ke objek datanya
indicator_dict = {
    f"{item['title']} (Kategori: {item.get('name_category', 'Umum')})": item
    for item in indicator_list
}

selected_ind_label = st.selectbox(
    "3. Pilih Indikator Strategis:", list(indicator_dict.keys())
)
chosen_indicator = indicator_dict[selected_ind_label]
indicator_id = chosen_indicator["indicator_id"]

with st.expander("ℹ️ Metadata Indikator"):
  st.write(f"**Satuan:** {chosen_indicator.get('unit', '-')}")
  st.write(f"**Kategori:** {chosen_indicator.get('name_category', '-')}")
  st.write(
      "**Catatan:**"
      f" {chosen_indicator.get('notes', 'Tidak ada catatan tambahan.')}"
  )

# 3. Penarikan Data Time-Series Indikator
if st.button("📊 Tampilkan Data", type="primary"):
  with st.spinner("Mengambil angka indikator dari server BPS..."):
    # Endpoint detail nilai indikator strategis
    detail_url = f"https://webapi.bps.go.id/v1/api/view/model/indicator/domain/{target_domain}/indicator/{indicator_id}/lang/ind/key/{BPS_APP_ID}/"
    try:
      r_det = requests.get(detail_url, headers=HEADERS, timeout=20)
      det_json = r_det.json()

      if det_json.get("status") == "OK" and "data" in det_json:
        raw_data = det_json["data"]

        # Membaca data array
        data_rows = []
        if isinstance(raw_data, list):
          for row in raw_data:
            data_rows.append({
                "Periode / Tahun": row.get("label", row.get("period", "-")),
                "Nilai": row.get("value", None),
            })
        elif isinstance(raw_data, dict):
          # Fallback jika data berbentuk key tahun
          for k, v in raw_data.items():
            data_rows.append({"Periode / Tahun": k, "Nilai": v})

        df = pd.DataFrame(data_rows)
        # Hapus baris bernilai kosong atau None
        df = df.dropna(subset=["Nilai"])

        if not df.empty:
          st.divider()
          st.subheader(f"📈 {chosen_indicator['title']}")
          st.caption(
              f"Wilayah: {wilayah_label} | Satuan:"
              f" {chosen_indicator.get('unit', '-')}"
          )

          # Tombol download
          c1, c2 = st.columns(2)
          c1.download_button(
              "📥 Unduh CSV",
              df.to_csv(index=False).encode("utf-8"),
              f"bps_{indicator_id}.csv",
              "text/csv",
          )
          buf = io.BytesIO()
          with pd.ExcelWriter(buf, engine="openpyxl") as writer:
            df.to_excel(writer, index=False, sheet_name="Data BPS")
          c2.download_button(
              "📊 Unduh Excel (.xlsx)",
              buf.getvalue(),
              f"bps_{indicator_id}.xlsx",
              "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
          )

          st.dataframe(df, use_container_width=True)

          with st.expander("🔍 Respon JSON Resmi BPS"):
            st.json(det_json)
        else:
          st.warning("Data observasi angka untuk indikator ini masih kosong.")
      else:
        st.error(
            f"Gagal memuat detail data (Pesan BPS: {det_json.get('status')})."
        )
    except Exception as e:
      st.error(f"Terjadi kesalahan saat memproses data: {e}")

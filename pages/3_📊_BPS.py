import io
import pandas as pd
import requests
import streamlit as st

st.set_page_config(page_title="BPS Data - IndoEcon Explorer", layout="wide")

st.title("📊 Indikator Strategis BPS")
st.write(
    "Eksplorasi indikator makroekonomi, sosial, dan pembangunan resmi dari"
    " **BPS** (Nasional, Provinsi, hingga Kabupaten/Kota)."
)

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    )
}

if "BPS_APP_ID" in st.secrets:
  BPS_APP_ID = st.secrets["BPS_APP_ID"]
else:
  st.error(
      "⚠️ Kunci `BPS_APP_ID` belum tersimpan di Secrets. Buka Manage app >"
      " Settings > Secrets."
  )
  st.stop()

# Daftar Domain Provinsi
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


# 1. Pilihan Wilayah
@st.cache_data(ttl=86400)
def get_kabupaten(prov_code):
  url = f"https://webapi.bps.go.id/v1/api/list/model/domain/lang/ind/domain/{prov_code}/key/{BPS_APP_ID}/"
  try:
    r = requests.get(url, headers=HEADERS, timeout=15)
    data = r.json()
    if data.get("status") == "OK" and len(data.get("data", [])) > 1:
      return {item["domain_name"]: item["domain_id"] for item in data["data"][1]}
  except Exception:
    pass
  return {}


col_p1, col_p2 = st.columns(2)
with col_p1:
  selected_prov = st.selectbox("1. Pilih Tingkat / Provinsi:", list(PROVINCES.keys()))
  prov_code = PROVINCES[selected_prov]

target_domain = prov_code
label_wilayah = selected_prov

if prov_code != "0000":
  kab_map = get_kabupaten(prov_code)
  with col_p2:
    if kab_map:
      pilihan_kab = [f"Seluruh {selected_prov} (Provinsi)"] + list(kab_map.keys())
      selected_kab = st.selectbox("2. Pilih Wilayah Administratif:", pilihan_kab)
      if selected_kab != f"Seluruh {selected_prov} (Provinsi)":
        target_domain = kab_map[selected_kab]
        label_wilayah = f"{selected_kab}, {selected_prov}"

st.caption(f"📍 Wilayah terpilih: **{label_wilayah}** (Domain: `{target_domain}`)")


# 2. Ambil Daftar Indikator dengan Format URL Resmi BPS
@st.cache_data(ttl=43200)
def fetch_all_indicators(domain):
  indicators = []
  # Ambil halaman 1 sampai 5 untuk menampung seluruh indikator strategis
  for page in range(1, 6):
    url = f"https://webapi.bps.go.id/v1/api/list/model/indicator/lang/ind/domain/{domain}/page/{page}/key/{BPS_APP_ID}/"
    try:
      res = requests.get(url, headers=HEADERS, timeout=15).json()
      if res.get("status") == "OK" and len(res.get("data", [])) > 1:
        items = res["data"][1]
        if not items:
          break
        indicators.extend(items)
      else:
        break
    except Exception:
      break
  return indicators


with st.spinner("Memuat katalog indikator strategis..."):
  indicator_list = fetch_all_indicators(target_domain)

if not indicator_list:
  st.warning(
      f"Tidak ditemukan indikator strategis langsung untuk {label_wilayah}."
      " Coba beralih ke Nasional atau Provinsi lain."
  )
  st.stop()

# Buat mapping judul indikator
indicator_options = {
    f"{item['title']} [{item.get('name_category', 'Umum')}]": item
    for item in indicator_list
}

selected_label = st.selectbox(
    "3. Pilih Indikator Strategis:", list(indicator_options.keys())
)
selected_ind = indicator_options[selected_label]
ind_id = selected_ind["indicator_id"]

with st.expander("ℹ️ Metadata Indikator"):
  st.write(f"**Satuan:** {selected_ind.get('unit', '-')}")
  st.write(f"**Kategori:** {selected_ind.get('name_category', '-')}")
  st.write(
      "**Definisi / Catatan:**"
      f" {selected_ind.get('notes', 'Tidak ada catatan tambahan.')}"
  )

# 3. Penarikan Data Angka
if st.button("📊 Tampilkan Data", type="primary"):
  with st.spinner("Mengambil angka data..."):
    # Endpoint detail nilai indikator strategis BPS yang presisi
    val_url = f"https://webapi.bps.go.id/v1/api/view/model/indicator/lang/ind/domain/{target_domain}/var/{ind_id}/key/{BPS_APP_ID}/"
    try:
      r_val = requests.get(val_url, headers=HEADERS, timeout=20)
      res_val = r_val.json()

      if res_val.get("status") == "OK" and "data" in res_val:
        raw = res_val["data"]
        rows = []

        if isinstance(raw, list):
          for r in raw:
            rows.append({
                "Periode": str(r.get("label", r.get("period", "-"))),
                "Nilai": r.get("value", None),
            })
        elif isinstance(raw, dict):
          for k, v in raw.items():
            rows.append({"Periode": str(k), "Nilai": v})

        df = pd.DataFrame(rows).dropna(subset=["Nilai"])

        if not df.empty:
          st.divider()
          st.subheader(f"📈 {selected_ind['title']}")

          c1, c2 = st.columns(2)
          c1.download_button(
              "📥 Unduh CSV",
              df.to_csv(index=False).encode("utf-8"),
              f"bps_{ind_id}.csv",
              "text/csv",
          )
          buf = io.BytesIO()
          with pd.ExcelWriter(buf, engine="openpyxl") as writer:
            df.to_excel(writer, index=False, sheet_name="Data BPS")
          c2.download_button(
              "📊 Unduh Excel (.xlsx)",
              buf.getvalue(),
              f"bps_{ind_id}.xlsx",
              "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
          )

          st.dataframe(df, use_container_width=True)
        else:
          st.info(
              "Indikator ini tercatat, namun rincian time-series belum"
              " dipublikasikan di WebAPI domain ini."
          )
      else:
        st.error(
            f"BPS mengembalikan pesan: {res_val.get('status', 'Gagal memuat')}"
        )
    except Exception as e:
      st.error(f"Terjadi kesalahan saat memproses data: {e}")

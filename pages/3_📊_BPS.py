import io
import time
import pandas as pd
import requests
import streamlit as st

st.set_page_config(page_title="BPS Data - IndoEcon Explorer", layout="wide")

st.title("📊 Indikator Utama BPS")
st.write(
    "Data indikator makroekonomi dan sosial resmi langsung dari **WebAPI"
    " BPS**."
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

# Cakupan Wilayah
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

# Indikator Terkurasi
KATALOG_INDIKATOR = {
    "Kesejahteraan & Kemiskinan": {
        "Gini Ratio (Ketimpangan Pengeluaran)": 1493,
        "Persentase Penduduk Miskin (P0) [%]": 191,
        "Garis Kemiskinan (Rupiah/Kapita/Bulan)": 192,
    },
    "Indeks Pembangunan & Pendidikan": {
        "Indeks Pembangunan Manusia (IPM)": 499,
        "Angka Harapan Hidup saat Lahir (AHH)": 501,
        "Rata-rata Lama Sekolah (RLS)": 502,
    },
    "Ketenagakerjaan": {
        "Tingkat Pengangguran Terbuka (TPT) [%]": 543,
        "Tingkat Partisipasi Angkatan Kerja (TPAK) [%]": 544,
    },
    "Makroekonomi": {
        "Laju Pertumbuhan PDB [%]": 104,
        "Indeks Harga Konsumen (IHK)": 2,
    },
}

selected_prov = st.selectbox(
    "1. Pilih Cakupan Wilayah:", list(PROVINCES.keys())
)
domain_code = PROVINCES[selected_prov]

col1, col2 = st.columns(2)
with col1:
  kategori_terpilih = st.selectbox(
      "2. Pilih Kategori Data:", list(KATALOG_INDIKATOR.keys())
  )

with col2:
  indikator_dict = KATALOG_INDIKATOR[kategori_terpilih]
  indikator_terpilih = st.selectbox(
      "3. Pilih Indikator:", list(indikator_dict.keys())
  )
  var_id = indikator_dict[indikator_terpilih]

# Tombol Eksekusi
if st.button("📊 Tampilkan Seluruh Data Tersedia", type="primary"):
  all_records = []

  # Rentang batch 3 tahunan dari masa lalu ke terkini
  year_batches = ["2018:2020", "2021:2023", "2024:2025"]

  with st.spinner(
      f"Mengumpulkan seluruh rentang riwayat data {indikator_terpilih}..."
  ):
    for batch in year_batches:
      url = f"https://webapi.bps.go.id/v1/api/list/model/data/lang/ind/domain/{domain_code}/var/{var_id}/th/{batch}/key/{BPS_APP_ID}/"
      try:
        r = requests.get(url, headers=HEADERS, timeout=20)
        res = r.json()

        if res.get("status") == "OK":
          data_content = res.get("datacontent", {})
          vervar_map = {
              str(item["val"]): item["label"] for item in res.get("vervar", [])
          }
          tahun_map = {
              str(item["val"]): item["label"] for item in res.get("tahun", [])
          }

          for key, val in data_content.items():
            if val is not None:
              k_str = str(key)
              wilayah_nama = selected_prov
              tahun_label = batch

              for v_val, v_lbl in vervar_map.items():
                if k_str.startswith(v_val):
                  wilayah_nama = v_lbl
                  break

              for t_val, t_lbl in tahun_map.items():
                if t_val in k_str:
                  tahun_label = t_lbl
                  break

              all_records.append({
                  "Wilayah / Rincian": wilayah_nama,
                  "Tahun / Periode": tahun_label,
                  "Nilai": val,
              })
        time.sleep(0.1)
      except Exception:
        continue

  df = pd.DataFrame(all_records)

  if not df.empty:
    # Hapus duplikasi jika ada observasi yang bertumpuk
    df = df.drop_duplicates().sort_values(
        by=["Wilayah / Rincian", "Tahun / Periode"], ascending=[True, False]
    )

    st.divider()
    st.subheader(f"📈 {indikator_terpilih}")
    st.caption(f"Cakupan: {selected_prov} | Sumber: WebAPI BPS")

    c1, c2 = st.columns(2)
    c1.download_button(
        "📥 Unduh CSV",
        df.to_csv(index=False).encode("utf-8"),
        f"bps_{var_id}_full.csv",
        "text/csv",
    )

    buf = io.BytesIO()
    with pd.ExcelWriter(buf, engine="openpyxl") as writer:
      df.to_excel(writer, index=False, sheet_name="Data BPS")
    c2.download_button(
        "📊 Unduh Excel (.xlsx)",
        buf.getvalue(),
        f"bps_{var_id}_full.xlsx",
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )

    st.dataframe(df, use_container_width=True)
  else:
    st.warning(
        "Data untuk indikator ini belum dialokasikan di API domain"
        f" {selected_prov}. Silakan coba indikator lain atau pilih domain"
        " Nasional."
    )

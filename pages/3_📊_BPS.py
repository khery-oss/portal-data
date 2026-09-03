import io
import pandas as pd
import requests
import streamlit as st

st.set_page_config(page_title="BPS Data - IndoEcon Explorer", layout="wide")

st.title("📊 Indikator Utama BPS")
st.write(
    "Data resmi indikator makroekonomi dan sosial pembangunan dari **WebAPI"
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

# Daftar domain provinsi resmi
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

# Katalog indikator terpilih yang teruji valid di WebAPI BPS
KATALOG_INDIKATOR = {
    "Kesejahteraan & Kemiskinan": {
        "Persentase Penduduk Miskin (P0) [%]": 191,
        "Garis Kemiskinan (Rupiah/Kapita/Bulan)": 192,
        "Gini Ratio (Ketimpangan Pengeluaran)": 1493,
    },
    "Indeks Pembangunan & Pendidikan": {
        "Indeks Pembangunan Manusia (IPM)": 499,
        "Angka Harapan Hidup saat Lahir (AHH) [Tahun]": 501,
        "Rata-rata Lama Sekolah (RLS) [Tahun]": 502,
        "Harapan Lama Sekolah (HLS) [Tahun]": 503,
    },
    "Ketenagakerjaan": {
        "Tingkat Pengangguran Terbuka (TPT) [%]": 543,
        "Tingkat Partisipasi Angkatan Kerja (TPAK) [%]": 544,
    },
    "Pertumbuhan & Inflasi": {
        "Indeks Harga Konsumen / Inflasi (IHK Tahunan)": 2,
        "Laju Pertumbuhan Produk Domestik Bruto (PDB) [%]": 104,
    },
}

# 1. Pilihan Wilayah
selected_prov = st.selectbox(
    "1. Pilih Cakupan Wilayah:", list(PROVINCES.keys())
)
domain_code = PROVINCES[selected_prov]

# 2. Pilihan Kategori dan Indikator
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

# 3. Pilihan Rentang Tahun (Dibatasi 3 Tahun agar Memenuhi Aturan BPS)
rentang_tahun_pilihan = {
    "2022 - 2024 (Data Terbaru)": "2022:2024",
    "2021 - 2023": "2021:2023",
    "2018 - 2020": "2018:2020",
    "2015 - 2017": "2015:2017",
}

selected_rentang_label = st.selectbox(
    "4. Periode Tahun (Maksimal 3 tahun per request):",
    list(rentang_tahun_pilihan.keys()),
)
th_param = rentang_tahun_pilihan[selected_rentang_label]

if st.button("📊 Tampilkan Data BPS", type="primary"):
  with st.spinner(f"Mengambil data {indikator_terpilih}..."):
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
            wilayah_nama = selected_prov
            tahun_nama = "-"

            # Cocokkan kode vervar untuk nama wilayah/rincian
            for v_code, v_label in vervar.items():
              if k_str.startswith(v_code):
                wilayah_nama = v_label
                break

            # Cocokkan kode tahun
            for t_code, t_label in tahun_dict.items():
              if t_code in k_str:
                tahun_nama = t_label
                break

            records.append({
                "Wilayah / Rincian": wilayah_nama,
                "Tahun": tahun_nama,
                "Nilai": val,
            })

        df = pd.DataFrame(records)

        if not df.empty:
          st.divider()
          st.subheader(f"📈 {indikator_terpilih}")
          st.caption(
              f"Wilayah: {selected_prov} | Periode: {selected_rentang_label}"
          )

          # Tombol Unduh
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
              "Observasi angka belum tersedia pada kombinasi wilayah dan rentang"
              " tahun ini."
          )
      else:
        st.warning(f"BPS mengembalikan pesan: {res.get('message', 'Gagal memuat data')}")
    except Exception as e:
      st.error(f"Terjadi kesalahan saat memanggil server: {e}")

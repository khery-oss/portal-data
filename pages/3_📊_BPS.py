import io
import pandas as pd
import requests
import streamlit as st

st.set_page_config(page_title="BPS Data - IndoEcon Explorer", layout="wide")

st.title("📊 Portal Data BPS (Badan Pusat Statistik)")
st.write(
    "Eksplorasi indikator makroekonomi, sosial, dan demografi resmi BPS dari"
    " level **Nasional** hingga **Provinsi**."
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

# Daftar Domain Utama
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

# Kurasi Indikator Utama BPS yang Teruji Stabil di WebAPI
CURATED_DATASETS = {
    "Ekonomi & Makro": {
        "Pertumbuhan Ekonomi / PDB Triwulanan (Persen)": {"var": 104, "sub": 52},
        "Indeks Harga Konsumen / Inflasi (IHK)": {"var": 2, "sub": 3},
        "Nilai Ekspor dan Impor": {"var": 1092, "sub": 8},
    },
    "Kesejahteraan & Kemiskinan": {
        "Persentase Penduduk Miskin (P0) Menurut Wilayah": {
            "var": 191,
            "sub": 23,
        },
        "Garis Kemiskinan (Rupiah/Kapita/Bulan)": {"var": 192, "sub": 23},
        "Gini Ratio (Ketimpangan Pengeluaran)": {"var": 1493, "sub": 23},
    },
    "Indeks Pembangunan & Pendidikan": {
        "Indeks Pembangunan Manusia (IPM)": {"var": 499, "sub": 26},
        "Angka Harapan Hidup saat Lahir (AHH)": {"var": 501, "sub": 26},
        "Rata-rata Lama Sekolah (RLS)": {"var": 502, "sub": 26},
    },
    "Ketenagakerjaan": {
        "Tingkat Pengangguran Terbuka (TPT)": {"var": 543, "sub": 6},
        "Tingkat Partisipasi Angkatan Kerja (TPAK)": {"var": 544, "sub": 6},
    },
}

# Pilihan Wilayah
selected_prov = st.selectbox(
    "1. Pilih Cakupan Wilayah:", list(PROVINCES.keys())
)
domain_code = PROVINCES[selected_prov]

# Pilihan Kategori & Indikator
col1, col2 = st.columns(2)
with col1:
  selected_cat = st.selectbox(
      "2. Pilih Kategori Data:", list(CURATED_DATASETS.keys())
  )

with col2:
  indicators_in_cat = CURATED_DATASETS[selected_cat]
  selected_indicator = st.selectbox(
      "3. Pilih Indikator BPS:", list(indicators_in_cat.keys())
  )
  var_id = indicators_in_cat[selected_indicator]["var"]

# Tombol Tarik Data
if st.button("📊 Tampilkan Data BPS", type="primary"):
  with st.spinner(f"Menghubungkan ke API BPS untuk {selected_indicator}..."):
    # Endpoint data dinamis resmi BPS
    url = f"https://webapi.bps.go.id/v1/api/list/model/data/lang/ind/domain/{domain_code}/var/{var_id}/key/{BPS_APP_ID}/"

    try:
      r = requests.get(url, headers=HEADERS, timeout=25)
      res = r.json()

      if (
          res.get("status") == "OK"
          and res.get("data-availability") != "list-not-available"
      ):
        data_content = res.get("datacontent", {})
        vervar = {
            str(item["val"]): item["label"] for item in res.get("vervar", [])
        }
        tahun_dict = {
            str(item["val"]): item["label"] for item in res.get("tahun", [])
        }

        # Parsing data multidimensi BPS ke format tabel bersih
        records = []
        for key, val in data_content.items():
          if val is not None:
            # Pola key BPS: vervar + var + turvar + tahun + turtahun
            k_str = str(key)
            wilayah_nama = selected_prov
            tahun_label = "Terkini"

            for v_code, v_label in vervar.items():
              if k_str.startswith(v_code):
                wilayah_nama = v_label
                break

            for t_code, t_label in tahun_dict.items():
              if t_code in k_str:
                tahun_label = t_label
                break

            records.append({
                "Wilayah / Klasifikasi": wilayah_nama,
                "Periode / Tahun": tahun_label,
                "Nilai": val,
            })

        df = pd.DataFrame(records)

        if not df.empty:
          st.divider()
          st.subheader(f"📈 {selected_indicator}")
          st.caption(f"Sumber: WebAPI BPS | Wilayah: {selected_prov}")

          c1, c2 = st.columns(2)
          c1.download_button(
              "📥 Unduh CSV",
              df.to_csv(index=False).encode("utf-8"),
              f"bps_{var_id}.csv",
              "text/csv",
          )
          buf = io.BytesIO()
          with pd.ExcelWriter(buf, engine="openpyxl") as writer:
            df.to_excel(writer, index=False, sheet_name="BPS Data")
          c2.download_button(
              "📊 Unduh Excel (.xlsx)",
              buf.getvalue(),
              f"bps_{var_id}.xlsx",
              "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
          )

          st.dataframe(df, use_container_width=True)
        else:
          st.warning(
              "Data tercatat di katalog, tetapi observasi numerik belum"
              " dipublikasikan untuk domain ini."
          )
      else:
        st.warning(
            "BPS merespons bahwa data indikator ini belum dialokasikan untuk"
            f" domain {selected_prov}. Coba gunakan cakupan 'Nasional / Seluruh"
            " Indonesia'."
        )
    except Exception as e:
      st.error(f"Terjadi kesalahan saat memanggil server BPS: {e}")

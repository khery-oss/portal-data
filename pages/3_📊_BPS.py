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

# Daftar domain resmi BPS
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

# Indikator strategis yang aktif di WebAPI BPS
KATALOG_INDIKATOR = {
    "Kesejahteraan & Kemiskinan": {
        "Gini Ratio (Ketimpangan Pengeluaran)": 1493,
        "Persentase Penduduk Miskin (P0) [%]": 191,
        "Garis Kemiskinan (Rupiah/Kapita/Bulan)": 192,
    },
    "Indeks Pembangunan & Pendidikan": {
        "Indeks Pembangunan Manusia (IPM)": 499,
        "Angka Harapan Hidup (AHH) [Tahun]": 501,
        "Rata-rata Lama Sekolah (RLS) [Tahun]": 502,
    },
    "Ketenagakerjaan": {
        "Tingkat Pengangguran Terbuka (TPT) [%]": 543,
        "Tingkat Partisipasi Angkatan Kerja (TPAK) [%]": 544,
    },
    "Makroekonomi": {
        "Indeks Harga Konsumen / Inflasi (IHK)": 2,
        "Laju Pertumbuhan PDB [%]": 104,
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

if st.button("📊 Tampilkan Data BPS", type="primary"):
  with st.spinner(f"Menarik data tabel {indikator_terpilih}..."):
    # Penarikan langsung tanpa parameter th manual agar server BPS menyajikan data default yang valid
    url = f"https://webapi.bps.go.id/v1/api/list/model/data/lang/ind/domain/{domain_code}/var/{var_id}/key/{BPS_APP_ID}/"

    try:
      r = requests.get(url, headers=HEADERS, timeout=25)
      res = r.json()

      if res.get("status") == "OK":
        data_content = res.get("datacontent", {})

        # Daftar label metadata
        vervar_map = {
            str(item["val"]): item["label"] for item in res.get("vervar", [])
        }
        tahun_map = {
            str(item["val"]): item["label"] for item in res.get("tahun", [])
        }
        turvar_map = {
            str(item["val"]): item["label"] for item in res.get("turvar", [])
        }
        turtahun_map = {
            str(item["val"]): item["label"] for item in res.get("turtahun", [])
        }

        records = []
        for key, val in data_content.items():
          if val is not None:
            k_str = str(key)

            # Ekstraksi label vervar (wilayah / kategori)
            nama_wilayah = selected_prov
            for v_val, v_lbl in vervar_map.items():
              if k_str.startswith(v_val):
                nama_wilayah = v_lbl
                break

            # Ekstraksi label tahun
            label_tahun = "-"
            for t_val, t_lbl in tahun_map.items():
              if t_val in k_str:
                label_tahun = t_lbl
                break

            records.append({
                "Wilayah / Rincian": nama_wilayah,
                "Tahun / Periode": label_tahun,
                "Nilai": val,
            })

        df = pd.DataFrame(records)

        if not df.empty:
          st.divider()
          st.subheader(f"📈 {indikator_terpilih}")
          st.caption(f"Cakupan: {selected_prov} | Sumber: WebAPI BPS")

          col_dl1, col_dl2 = st.columns(2)
          col_dl1.download_button(
              "📥 Unduh CSV",
              df.to_csv(index=False).encode("utf-8"),
              f"bps_{var_id}.csv",
              "text/csv",
          )

          buf = io.BytesIO()
          with pd.ExcelWriter(buf, engine="openpyxl") as writer:
            df.to_excel(writer, index=False, sheet_name="Data BPS")
          col_dl2.download_button(
              "📊 Unduh Excel (.xlsx)",
              buf.getvalue(),
              f"bps_{var_id}.xlsx",
              "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
          )

          st.dataframe(df, use_container_width=True)
        else:
          st.warning(
              "Respons diterima dari BPS, tetapi data observasi kosong. Coba"
              " ganti cakupan wilayah."
          )

      elif res.get("status") == "Error":
        # Jika server tetap meminta parameter tahun internal
        st.warning(f"Respon BPS: {res.get('message', 'Parameter tidak sesuai')}")
        with st.expander("Detail Respons Teknis"):
          st.json(res)

    except Exception as e:
      st.error(f"Gagal memproses data: {e}")

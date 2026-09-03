import io
import pandas as pd
import requests
import streamlit as st

st.set_page_config(
    page_title="World Bank Data Explorer - Indonesia", layout="wide"
)

st.title("🇮🇩 World Bank Open Data Explorer - Indonesia")
st.write(
    "Cari indikator apa saja langsung dari ribuan database resmi **World"
    " Bank** secara otomatis."
)

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    )
}


# Simpan daftar indikator di cache agar aplikasi sangat cepat dan tidak loading terus-menerus
@st.cache_data(ttl=86400)
def load_all_indicators():
  indicators = []
  # Ambil indikator WDI utama langsung dari World Bank
  url = "https://api.worldbank.org/v2/indicator?source=2&format=json&per_page=3000"
  try:
    res = requests.get(url, headers=HEADERS, timeout=20)
    data = res.json()
    if len(data) > 1 and data[1]:
      for item in data[1]:
        indicators.append({
            "id": item.get("id"),
            "name": item.get("name"),
            "sourceNote": item.get("sourceNote", ""),
        })
  except Exception:
    pass
  return indicators


with st.spinner("Menghubungkan ke katalog data World Bank..."):
  all_indicators = load_all_indicators()

# Input pencarian otomatis
query = st.text_input(
    "🔍 Ketik topik/variabel (Bahasa Inggris, misal: 'gdp', 'debt', 'tax',"
    " 'export', 'education', 'health'):",
    value="gdp",
).strip()

if query and all_indicators:
  # Filter otomatis berdasarkan kata kunci yang diketik
  results = [
      ind
      for ind in all_indicators
      if query.lower() in ind["name"].lower()
      or query.lower() in ind["id"].lower()
  ]

  if results:
    st.success(
        f"Ditemukan {len(results)} indikator terkait kata kunci '{query}'"
        " langsung dari World Bank!"
    )

    # Format pilihan di dropdown
    options_map = {f"{ind['name']} ({ind['id']})": ind for ind in results}
    selected_label = st.selectbox(
        "Pilih Indikator Hasil Pencarian:", list(options_map.keys())
    )
    selected_ind = options_map[selected_label]
    kode_indikator = selected_ind["id"]

    # Tampilkan deskripsi/metodologi resmi World Bank jika ada
    if selected_ind["sourceNote"]:
      with st.expander("ℹ️ Definisi & Metodologi Resmi Indikator Ini"):
        st.write(selected_ind["sourceNote"])

    if st.button("📊 Ambil Data Indonesia", type="primary"):
      with st.spinner(f"Mengunduh time series untuk {kode_indikator}..."):
        data_url = f"https://api.worldbank.org/v2/country/IDN/indicator/{kode_indikator}?format=json&per_page=120"
        try:
          r_data = requests.get(data_url, headers=HEADERS, timeout=15)
          data_json = r_data.json()

          records = []
          if len(data_json) > 1 and data_json[1]:
            for item in data_json[1]:
              thn = item.get("date")
              val = item.get("value")
              if val is not None:
                try:
                  records.append(
                      {"Tahun": int(thn), "Nilai": round(float(val), 2)}
                  )
                except (ValueError, TypeError):
                  continue

          if records:
            df = pd.DataFrame(records).sort_values(by="Tahun", ascending=True)
            link_resmi = f"https://data.worldbank.org/indicator/{kode_indikator}?locations=ID"

            st.divider()
            st.markdown(
                f"🔗 **Halaman Resmi World Bank:** [{selected_label}]({link_resmi})"
            )

            # Tombol Unduh
            col1, col2 = st.columns(2)
            csv_data = df.to_csv(index=False).encode("utf-8")
            col1.download_button(
                label="📥 Unduh Data (CSV)",
                data=csv_data,
                file_name=f"{kode_indikator}_indonesia.csv",
                mime="text/csv",
            )

            buffer = io.BytesIO()
            with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
              df.to_excel(writer, index=False, sheet_name="Data")
            col2.download_button(
                label="📊 Unduh Data (Excel .xlsx)",
                data=buffer.getvalue(),
                file_name=f"{kode_indikator}_indonesia.xlsx",
                mime=(
                    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                ),
            )

            # Visualisasi & Tabel
            st.subheader("📈 Visualisasi Tren")
            st.line_chart(df.set_index("Tahun")["Nilai"])

            with st.expander("📋 Tabel Angka Lengkap"):
              st.dataframe(
                  df.sort_values(by="Tahun", ascending=False),
                  use_container_width=True,
              )
          else:
            st.warning(
                f"Indikator '{kode_indikator}' tercatat di World Bank, namun"
                " Indonesia tidak memiliki observasi data untuk variabel ini."
            )
        except Exception as e:
          st.error(f"Gagal mengambil data: {e}")
  else:
    st.warning(
        f"Tidak ditemukan indikator dengan kata kunci '{query}'. Gunakan istilah"
        " umum dalam bahasa Inggris."
    )

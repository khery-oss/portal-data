import io
import pandas as pd
import requests
import streamlit as st

st.set_page_config(
    page_title="Pencari Data World Bank Indonesia", layout="wide"
)

st.title("🇮🇩 World Bank Data Explorer - Indonesia")
st.write(
    "Ketik topik data ekonomi/sosial apa saja untuk mencari langsung ke seluruh"
    " database resmi **World Bank**."
)

query = st.text_input(
    "🔍 Ketik kata kunci (Bahasa Inggris, misal: 'inflation', 'gdp',"
    " 'poverty', 'internet', 'export'):",
    value="inflation",
)

if query:
  with st.spinner("Mencari daftar indikator di World Bank..."):
    try:
      r_query = requests.get(
          "https://api.worldbank.org/v2/indicator?format=json&per_page=1000",
          timeout=15,
      )
      all_ind = r_query.json()[1]

      matching_indicators = {}
      for ind in all_ind:
        name = ind.get("name", "")
        code = ind.get("id", "")
        if query.lower() in name.lower() or query.lower() in code.lower():
          matching_indicators[f"{name} ({code})"] = code

      if matching_indicators:
        st.success(f"Ditemukan {len(matching_indicators)} indikator yang cocok!")

        pilihan_nama = st.selectbox(
            "Pilih Indikator Hasil Pencarian:", list(matching_indicators.keys())
        )
        kode_terpilih = matching_indicators[pilihan_nama]

        if st.button("📊 Tampilkan Data"):
          with st.spinner(f"Menarik data Indonesia untuk {kode_terpilih}..."):
            data_url = f"https://api.worldbank.org/v2/country/IDN/indicator/{kode_terpilih}?format=json&per_page=100"
            r_data = requests.get(data_url, timeout=10)
            data_json = r_data.json()

            records = []
            if len(data_json) > 1 and data_json[1]:
              for item in data_json[1]:
                thn = item.get("date")
                val = item.get("value")
                if val is not None:
                  records.append({"Tahun": int(thn), "Nilai": float(val)})

              if records:
                df = pd.DataFrame(records).sort_values(
                    by="Tahun", ascending=True
                )
                link_resmi = f"https://data.worldbank.org/indicator/{kode_terpilih}?locations=ID"

                st.divider()
                st.markdown(
                    f"🔗 **Sumber Resmi:** [{pilihan_nama}]({link_resmi})"
                )

                col1, col2 = st.columns(2)
                csv_data = df.to_csv(index=False).encode("utf-8")
                col1.download_button(
                    label="📥 Unduh CSV",
                    data=csv_data,
                    file_name=f"{kode_terpilih}_indonesia.csv",
                    mime="text/csv",
                )

                buffer = io.BytesIO()
                with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
                  df.to_excel(writer, index=False, sheet_name="Data")
                col2.download_button(
                    label="📊 Unduh Excel (.xlsx)",
                    data=buffer.getvalue(),
                    file_name=f"{kode_terpilih}_indonesia.xlsx",
                    mime=(
                        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                    ),
                )

                st.subheader("📈 Tren Historis")
                st.line_chart(df.set_index("Tahun")["Nilai"])

                with st.expander("📋 Lihat Tabel Angka Lengkap"):
                  st.dataframe(
                      df.sort_values(by="Tahun", ascending=False),
                      use_container_width=True,
                  )
              else:
                st.warning(
                    "Indikator ini tercatat di World Bank, namun data untuk"
                    " Indonesia belum tersedia."
                )
            else:
              st.warning("Data tidak ditemukan dari server World Bank.")
      else:
        st.warning(
            f"Tidak ditemukan indikator dengan kata kunci '{query}'. Coba kata"
            " kunci umum lain (misal: 'tax', 'debt', 'health')."
        )
    except Exception as e:
      st.error(f"Gagal memuat indikator: {e}")

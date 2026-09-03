import streamlit as st
import pandas as pd
import requests
import io

st.set_page_config(page_title="FRED - Portal Data", layout="wide")
st.title("📈 Federal Reserve Economic Data (FRED)")

HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
FRED_API_KEY = "9564eb2b869b421ac4119dd8eb5f63f9"

query_fred = st.text_input(
    "🔍 Cari indikator FRED (misal: 'Indonesia interest rate', 'Indonesia exchange rate', 'Indonesia M2'):",
    value="Indonesia interest rate"
).strip()

if query_fred:
    with st.spinner("Mencari seri data di FRED..."):
        search_url = f"https://api.stlouisfed.org/fred/series/search?search_text={query_fred}&api_key={FRED_API_KEY}&file_type=json&limit=30"
        try:
            res_f = requests.get(search_url, headers=HEADERS, timeout=15)
            data_f = res_f.json()
            seri_list = data_f.get("seriess", [])

            if seri_list:
                st.success(f"Ditemukan {len(seri_list)} seri indikator di FRED!")
                fred_options = {
                    f"{s['title']} ({s['id']}) - Frekuensi: {s.get('frequency', '-')}, Satuan: {s.get('units_short', '-')}": s
                    for s in seri_list
                }
                selected_fred_label = st.selectbox("Pilih Seri Data FRED:", list(fred_options.keys()))
                selected_fred = fred_options[selected_fred_label]
                series_id = selected_fred["id"]

                with st.expander("ℹ️ Detail Metadata & Sumber"):
                    st.write(f"**Frekuensi:** {selected_fred.get('frequency')}")
                    st.write(f"**Satuan:** {selected_fred.get('units')}")
                    st.write(f"**Rentang Observasi:** {selected_fred.get('observation_start')} s.d. {selected_fred.get('observation_end')}")
                    st.write(f"**Catatan Metodologi:** {selected_fred.get('notes', 'Tidak ada catatan tambahan.')}")

                if st.button("📊 Ambil Data FRED", type="primary"):
                    with st.spinner(f"Mengambil observasi data untuk {series_id}..."):
                        obs_url = f"https://api.stlouisfed.org/fred/series/observations?series_id={series_id}&api_key={FRED_API_KEY}&file_type=json"
                        r_obs = requests.get(obs_url, headers=HEADERS, timeout=15)
                        obs_json = r_obs.json()
                        raw_obs = obs_json.get("observations", [])

                        records_fred = []
                        for row in raw_obs:
                            tgl = row.get("date")
                            val_str = row.get("value")
                            try:
                                records_fred.append({"Tanggal": tgl, "Nilai": float(val_str)})
                            except (ValueError, TypeError):
                                continue

                        if records_fred:
                            df_fred = pd.DataFrame(records_fred)
                            df_fred["Tanggal"] = pd.to_datetime(df_fred["Tanggal"])
                            df_fred = df_fred.sort_values(by="Tanggal", ascending=True)

                            link_fred = f"https://fred.stlouisfed.org/series/{series_id}"
                            st.divider()
                            st.markdown(f"🔗 **Halaman Resmi FRED:** [{selected_fred['title']}]({link_fred})")

                            cf1, cf2 = st.columns(2)
                            cf1.download_button(
                                "📥 Unduh CSV",
                                df_fred.to_csv(index=False).encode('utf-8'),
                                f"{series_id}_fred.csv",
                                "text/csv"
                            )
                            buf_fred = io.BytesIO()
                            with pd.ExcelWriter(buf_fred, engine='openpyxl') as writer:
                                df_fred.to_excel(writer, index=False, sheet_name="Data")
                            cf2.download_button(
                                "📊 Unduh Excel (.xlsx)",
                                buf_fred.getvalue(),
                                f"{series_id}_fred.xlsx",
                                "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                            )

                            st.line_chart(df_fred.set_index("Tanggal")["Nilai"])
                            with st.expander("📋 Tabel Data Lengkap"):
                                st.dataframe(df_fred.sort_values(by="Tanggal", ascending=False), use_container_width=True)
                        else:
                            st.warning("Data observasi tidak ditemukan atau nilainya kosong.")
            else:
                st.warning(f"Tidak ada seri data FRED yang cocok dengan '{query_fred}'.")
        except Exception as e:
            st.error(f"Gagal memuat data FRED: {e}")

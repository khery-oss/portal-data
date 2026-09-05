import io
import pandas as pd
import plotly.graph_objects as go
import requests
import streamlit as st

st.set_page_config(page_title="World Bank - Portal Data", layout="wide")
st.title("🌐 Database Lengkap World Bank - Indonesia")

HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}

@st.cache_data(ttl=86400)
def load_wb_indicators():
    indicators = []
    url = "https://api.worldbank.org/v2/indicator?format=json&per_page=5000"
    try:
        res = requests.get(url, headers=HEADERS, timeout=25)
        data = res.json()
        if len(data) > 1 and data[1]:
            for item in data[1]:
                ind_id = item.get("id")
                ind_name = item.get("name")
                if ind_id and ind_name and not ind_id.startswith("6.") and not ind_id.startswith("7."):
                    indicators.append({
                        "id": ind_id,
                        "name": ind_name,
                        "sourceNote": item.get("sourceNote", ""),
                        "sourceOrg": item.get("sourceOrganization", "World Bank")
                    })
    except Exception:
        pass
    return indicators

all_wb_indicators = load_wb_indicators()

query_wb = st.text_input(
    "🔍 Cari indikator World Bank (misal: 'GDP', 'Inflation', 'Poverty', 'Education', 'CO2'):",
    value="GDP growth"
).strip()

if query_wb and all_wb_indicators:
    # Menyaring indikator yang relevan dengan kata kunci
    raw_results = [
        ind for ind in all_wb_indicators
        if query_wb.lower() in ind["name"].lower() or query_wb.lower() in ind["id"].lower()
    ]

    if raw_results:
        # Validasi kilat untuk memastikan indikator tersebut benar-benar memiliki data untuk Indonesia (IDN)
        with st.spinner("Memvalidasi ketersediaan data untuk Indonesia..."):
            valid_results = []
            for ind in raw_results[:30]: # Batasi 30 teratas agar pemuatan tetap instan
                check_url = f"https://api.worldbank.org/v2/country/IDN/indicator/{ind['id']}?format=json&per_page=1"
                try:
                    chk_res = requests.get(check_url, headers=HEADERS, timeout=5).json()
                    if len(chk_res) > 1 and chk_res[1] and any(v.get("value") is not None for v in chk_res[1]):
                        valid_results.append(ind)
                except Exception:
                    continue

        if valid_results:
            st.success(f"Ditemukan {len(valid_results)} indikator aktif dengan data tersedia untuk Indonesia!")
            options_wb = {ind['name']: ind for ind in valid_results}
            selected_wb_label = st.selectbox("Pilih Indikator:", list(options_wb.keys()))
            selected_wb = options_wb[selected_wb_label]
            kode_wb = selected_wb["id"]

            with st.expander("ℹ️ Definisi & Organisasi Sumber Data"):
                st.markdown(f"**Kode Seri API:** `{kode_wb}`")
                st.markdown(f"**Organisasi Penyusun/Metodologi:** {selected_wb['sourceOrg']}")
                st.markdown(f"**Definisi:** {selected_wb['sourceNote'] if selected_wb['sourceNote'] else 'Tidak ada deskripsi teks.'}")

            if st.button("📊 Ambil Data World Bank", type="primary"):
                with st.spinner(f"Menarik time-series lengkap untuk {selected_wb_label}..."):
                    data_url = f"https://api.worldbank.org/v2/country/IDN/indicator/{kode_wb}?format=json&per_page=120"
                    try:
                        r_data = requests.get(data_url, headers=HEADERS, timeout=15)
                        data_json = r_data.json()

                        records_wb = []
                        if len(data_json) > 1 and data_json[1]:
                            for item in data_json[1]:
                                thn = item.get("date")
                                val = item.get("value")
                                if val is not None:
                                    try:
                                        records_wb.append({"Tahun": int(thn), "Nilai": round(float(val), 2)})
                                    except (ValueError, TypeError):
                                        continue

                        if records_wb:
                            df_wb = pd.DataFrame(records_wb).sort_values(by="Tahun", ascending=True)
                            link_wb = f"https://data.worldbank.org/indicator/{kode_wb}?locations=ID"

                            st.divider()
                            st.markdown(f"🔗 **Tautan Resmi World Bank:** [{selected_wb_label}]({link_wb})")

                            c1, c2 = st.columns(2)
                            c1.download_button(
                                "📥 Unduh CSV",
                                df_wb.to_csv(index=False).encode('utf-8'),
                                f"WB_{kode_wb}_IDN.csv",
                                "text/csv"
                            )
                            buf_wb = io.BytesIO()
                            with pd.ExcelWriter(buf_wb, engine='openpyxl') as writer:
                                df_wb.to_excel(writer, index=False, sheet_name="Data")
                            c2.download_button(
                                "📊 Unduh Excel (.xlsx)",
                                buf_wb.getvalue(),
                                f"WB_{kode_wb}_IDN.xlsx",
                                "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                            )

                            # Visualisasi Interaktif Plotly
                            fig = go.Figure()
                            fig.add_trace(go.Scatter(
                                x=df_wb["Tahun"],
                                y=df_wb["Nilai"],
                                mode="lines+markers",
                                name="Indonesia (World Bank)",
                                line=dict(width=2.5, color="#002244"),
                                hovertemplate="Tahun %{x}<br>Nilai: %{y}<extra></extra>"
                            ))
                            fig.update_layout(
                                xaxis=dict(title="Tahun", tickmode="linear"),
                                yaxis=dict(title="Nilai Indikator"),
                                hovermode="x unified",
                                margin=dict(l=20, r=20, t=40, b=20)
                            )
                            st.plotly_chart(fig, use_container_width=True)

                            with st.expander("📋 Tabel Data Lengkap"):
                                st.dataframe(df_wb.sort_values(by="Tahun", ascending=False), use_container_width=True)
                        else:
                            st.warning("Gagal memuat observasi angka untuk seri ini.")
                    except Exception as e:
                        st.error(f"Gagal memuat data: {e}")
        else:
            st.warning("Tidak ditemukan indikator dengan data aktif untuk Indonesia dari kata kunci tersebut. Coba kata kunci lain (misal: 'GDP', 'Inflation', 'Population').")
    else:
        st.warning("Tidak ada indikator yang cocok dengan kata kunci tersebut.")
else:
    st.info("Memuat katalog indikator World Bank...")

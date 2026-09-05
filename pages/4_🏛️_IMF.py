import io
import pandas as pd
import plotly.graph_objects as go
import requests
import streamlit as st

st.set_page_config(page_title="IMF Data Explorer - Indonesia", layout="wide")

st.title("🏛️ Portal Data IMF (World Economic Outlook - Indonesia)")
st.write(
    "Eksplorasi indikator makroekonomi, fiskal, dan neraca pembayaran resmi **International Monetary Fund (IMF)** "
    "khusus untuk wilayah **Indonesia (IDN)** secara langsung (*live*) via **IMF DataMapper API**."
)

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
}

# KATALOG RESMI INDIKATOR WEO (WORLD ECONOMIC OUTLOOK) IMF UNTUK INDONESIA
IMF_INDICATORS = {
    "Real GDP Growth (Annual %)": {
        "id": "NGDP_RPCH", "unit": "%", "kategori": "Output & Pertumbuhan",
        "desc": "Annual percentages of constant price GDP are year-on-year changes; the base year is country-specific."
    },
    "GDP, Current Prices (Billion USD)": {
        "id": "NGDPD", "unit": "Billion USD", "kategori": "Output & Pertumbuhan",
        "desc": "Gross domestic product is expressed in current U.S. dollars."
    },
    "GDP per Capita, Current Prices (USD)": {
        "id": "NGDPDPC", "unit": "USD", "kategori": "Output & Pertumbuhan",
        "desc": "Gross domestic product divided by total population, in current U.S. dollars."
    },
    "GDP per Capita (PPP, Current International Dollar)": {
        "id": "PPPPC", "unit": "Current Int $", "kategori": "Output & Pertumbuhan",
        "desc": "GDP per capita converted to international dollars using purchasing power parity rates."
    },
    "Inflation Rate, Average Consumer Prices (Annual %)": {
        "id": "PCPIPCH", "unit": "%", "kategori": "Inflasi & Harga",
        "desc": "Annual percentage change in the average consumer price index."
    },
    "Inflation Rate, End of Period Consumer Prices (Annual %)": {
        "id": "PCPIEPCH", "unit": "%", "kategori": "Inflasi & Harga",
        "desc": "End of period consumer price index annual percentage change."
    },
    "General Government Gross Debt (% of GDP)": {
        "id": "GGXWDG_NGDP", "unit": "% of GDP", "kategori": "Fiskal & Keuangan Pemerintah",
        "desc": "Gross debt consists of all liabilities that require payment or payments of interest and/or principal."
    },
    "General Government Net Lending/Borrowing (% of GDP)": {
        "id": "GGXCNL_NGDP", "unit": "% of GDP", "kategori": "Fiskal & Keuangan Pemerintah",
        "desc": "Net lending (+)/borrowing (-) is calculated as revenue minus total expenditure (Fiscal Deficit/Surplus)."
    },
    "General Government Revenue (% of GDP)": {
        "id": "GGR_NGDP", "unit": "% of GDP", "kategori": "Fiskal & Keuangan Pemerintah",
        "desc": "Total revenue consists of taxes, social contributions, grants receivable, and other revenue."
    },
    "General Government Total Expenditure (% of GDP)": {
        "id": "GGX_NGDP", "unit": "% of GDP", "kategori": "Fiskal & Keuangan Pemerintah",
        "desc": "Total expenditure consists of total expense and the net acquisition of nonfinancial assets."
    },
    "Current Account Balance (% of GDP)": {
        "id": "BCA_NGDPD", "unit": "% of GDP", "kategori": "Eksternal & Perdagangan",
        "desc": "Current account balance as a share of national gross domestic product."
    },
    "Current Account Balance (Billion USD)": {
        "id": "BCA", "unit": "Billion USD", "kategori": "Eksternal & Perdagangan",
        "desc": "Net balance of goods, services, primary income, and secondary income."
    },
    "Volume of Imports of Goods and Services (% Change)": {
        "id": "TM_RPCH", "unit": "% Change", "kategori": "Eksternal & Perdagangan",
        "desc": "Annual percentage change in the volume of goods and services imported."
    },
    "Volume of Exports of Goods and Services (% Change)": {
        "id": "TX_RPCH", "unit": "% Change", "kategori": "Eksternal & Perdagangan",
        "desc": "Annual percentage change in the volume of goods and services exported."
    },
    "Unemployment Rate (% of Labor Force)": {
        "id": "LUR", "unit": "% of Labor Force", "kategori": "Ketenagakerjaan & Sosial",
        "desc": "Unemployment rate refers to the share of the labor force that is without work but available and seeking employment."
    },
    "Total Population (Million Persons)": {
        "id": "LP", "unit": "Million Persons", "kategori": "Ketenagakerjaan & Sosial",
        "desc": "Midyear total population estimate provided by official census and national sources."
    },
    "Gross National Savings (% of GDP)": {
        "id": "NGSD_NGDP", "unit": "% of GDP", "kategori": "Investasi & Tabungan",
        "desc": "Gross national saving is derived by deducting final consumption expenditure from gross national disposable income."
    },
    "Total Investment (% of GDP)": {
        "id": "NID_NGDP", "unit": "% of GDP", "kategori": "Investasi & Tabungan",
        "desc": "Total investment / gross capital formation as a percentage of GDP."
    }
}

# 1. Pemilihan Indikator Berdasarkan Kategori
st.subheader("1. Pemilihan Indikator IMF")
col_kat, col_ind = st.columns([1, 1.8])

kategori_list = sorted(list(set(v["kategori"] for v in IMF_INDICATORS.values())))
with col_kat:
    pilihan_kategori = st.selectbox("Kategori Bidang:", ["Semua Kategori"] + kategori_list)

indikator_opsi = [
    k for k, v in IMF_INDICATORS.items()
    if pilihan_kategori == "Semua Kategori" or v["kategori"] == pilihan_kategori
]

with col_ind:
    selected_name = st.selectbox("Nama Indikator:", indikator_opsi)

meta = IMF_INDICATORS[selected_name]
kode_imf = meta["id"]

# 2. Metadata Resmi IMF
with st.expander("ℹ️ Definisi & Metadata Resmi IMF", expanded=True):
    st.markdown(f"**Series Name:** {selected_name}")
    st.markdown(f"**Series Code (IMF WEO):** `{kode_imf}`")
    st.markdown(f"**Kategori:** `{meta['kategori']}`")
    st.markdown(f"**Satuan Unit:** `{meta['unit']}`")
    st.markdown(f"**Metodologi / Deskripsi:**\n{meta['desc']}")

# 3. Pengambilan Data Live dari IMF DataMapper API
if st.button("📊 Ambil Data IMF Indonesia", type="primary"):
    with st.spinner(f"Menarik time-series resmi IMF untuk {selected_name}..."):
        data_url = f"https://www.imf.org/external/datamapper/api/v1/{kode_imf}/IDN"
        try:
            r = requests.get(data_url, headers=HEADERS, timeout=15)
            data_json = r.json()

            # Respon API IMF DataMapper: values -> {KODE} -> IDN -> {tahun: nilai}
            values_dict = data_json.get("values", {}).get(kode_imf, {}).get("IDN", {})

            if values_dict:
                records = []
                for thn_str, val in values_dict.items():
                    try:
                        records.append({"Tahun": int(thn_str), f"Nilai ({meta['unit']})": round(float(val), 2)})
                    except (ValueError, TypeError):
                        continue

                df_imf = pd.DataFrame(records).sort_values(by="Tahun", ascending=True)

                st.divider()
                st.markdown(
                    f"🔗 **Tautan Resmi Database IMF:** [Buka di IMF DataMapper Portal](https://www.imf.org/external/datamapper/{kode_imf}@WEO/IDN)"
                )

                # Tombol Download Data
                c1, c2 = st.columns(2)
                c1.download_button(
                    "📥 Unduh CSV",
                    df_imf.to_csv(index=False).encode("utf-8"),
                    f"IMF_{kode_imf}_IDN.csv",
                    "text/csv"
                )
                buf = io.BytesIO()
                with pd.ExcelWriter(buf, engine="openpyxl") as writer:
                    df_imf.to_excel(writer, index=False, sheet_name="IMF Data")
                c2.download_button(
                    "📊 Unduh Excel (.xlsx)",
                    buf.getvalue(),
                    f"IMF_{kode_imf}_IDN.xlsx",
                    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )

                # Visualisasi Interaktif Plotly (Nuansa Merah Khas IMF)
                val_col = f"Nilai ({meta['unit']})"
                fig = go.Figure()
                fig.add_trace(go.Scatter(
                    x=df_imf["Tahun"],
                    y=df_imf[val_col],
                    mode="lines+markers",
                    name="Indonesia (IMF WEO)",
                    line=dict(width=2.5, color="#A6192E"),
                    hovertemplate=f"Tahun %{{x}}<br>Nilai: %{{y}} {meta['unit']}<extra></extra>"
                ))
                fig.update_layout(
                    xaxis=dict(title="Tahun", tickmode="linear"),
                    yaxis=dict(title=meta["unit"]),
                    hovermode="x unified",
                    margin=dict(l=20, r=20, t=40, b=20)
                )
                st.plotly_chart(fig, use_container_width=True)

                with st.expander("📋 Tabel Data Runtun Waktu (Termasuk Proyeksi WEO)"):
                    st.dataframe(
                        df_imf.sort_values(by="Tahun", ascending=False),
                        use_container_width=True
                    )
            else:
                st.warning("Data runtun waktu untuk indikator ini tidak tersedia di server IMF untuk Indonesia.")
        except Exception as e:
            st.error(f"Gagal memuat data dari server IMF: {e}")

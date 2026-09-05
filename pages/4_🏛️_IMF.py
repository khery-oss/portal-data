import io
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

st.set_page_config(page_title="IMF Data Explorer - Indonesia", layout="wide")

st.title("🏛️ Portal Data IMF (World Economic Outlook - Indonesia)")
st.write(
    "Eksplorasi indikator makroekonomi, fiskal, dan neraca pembayaran resmi **International Monetary Fund (IMF)** "
    "khusus untuk wilayah **Indonesia (IDN)** berdasarkan basis data publikasi resmi **IMF World Economic Outlook (WEO)**."
)

# KATALOG RESMI IMF WEO KHUSUS INDONESIA (SUMBER: IMF WEO DATABASE)
IMF_CATALOG = {
    # --- 1. Output & Pertumbuhan ---
    "Real GDP Growth (Annual %)": {
        "kategori": "1. Output & Pertumbuhan", "unit": "%", "weo_code": "NGDP_RPCH",
        "desc": "Persentase perubahan tahunan PDB riil berdasarkan harga konstan.",
        "data": {"2000": 4.92, "2002": 4.50, "2004": 5.03, "2006": 5.50, "2008": 6.01, "2010": 6.22, "2012": 6.03, "2014": 5.01, "2016": 5.03, "2017": 5.07, "2018": 5.17, "2019": 5.02, "2020": -2.07, "2021": 3.70, "2022": 5.31, "2023": 5.05, "2024": 5.00}
    },
    "GDP, Current Prices (Billion USD)": {
        "kategori": "1. Output & Pertumbuhan", "unit": "Billion USD", "weo_code": "NGDPD",
        "desc": "Produk Domestik Bruto atas dasar harga berlaku dinyatakan dalam miliar Dolar AS.",
        "data": {"2000": 179.48, "2005": 328.85, "2010": 755.26, "2012": 917.87, "2014": 890.81, "2016": 932.06, "2018": 1042.27, "2020": 1059.05, "2021": 1186.51, "2022": 1319.08, "2023": 1371.17, "2024": 1475.66}
    },
    "GDP per Capita, Current Prices (USD)": {
        "kategori": "1. Output & Pertumbuhan", "unit": "USD", "weo_code": "NGDPDPC",
        "desc": "PDB dibagi dengan jumlah penduduk pertengahan tahun dalam Dolar AS berlaku.",
        "data": {"2000": 848, "2005": 1453, "2010": 3122, "2012": 3695, "2014": 3492, "2016": 3563, "2018": 3894, "2020": 3912, "2021": 4351, "2022": 4788, "2023": 4940, "2024": 5271}
    },

    # --- 2. Inflasi & Harga ---
    "Inflation Rate, Average Consumer Prices (Annual %)": {
        "kategori": "2. Inflasi & Harga", "unit": "%", "weo_code": "PCPIPCH",
        "desc": "Perubahan persentase tahunan pada indeks harga konsumen rata-rata.",
        "data": {"2000": 3.73, "2002": 11.84, "2004": 6.06, "2006": 13.11, "2008": 10.23, "2010": 5.13, "2012": 4.28, "2014": 6.39, "2016": 3.53, "2018": 3.20, "2020": 2.03, "2021": 1.56, "2022": 4.21, "2023": 3.67, "2024": 2.60}
    },

    # --- 3. Fiskal & Keuangan Pemerintah ---
    "General Government Gross Debt (% of GDP)": {
        "kategori": "3. Fiskal & Keuangan Pemerintah", "unit": "% of GDP", "weo_code": "GGXWDG_NGDP",
        "desc": "Total kewajiban utang bruto pemerintah umum relatif terhadap PDB nasional.",
        "data": {"2000": 87.4, "2004": 51.3, "2008": 30.3, "2010": 24.5, "2012": 23.0, "2014": 24.7, "2016": 27.9, "2018": 30.2, "2019": 30.2, "2020": 39.7, "2021": 40.7, "2022": 39.6, "2023": 39.1, "2024": 38.6}
    },
    "General Government Net Lending/Borrowing (% of GDP)": {
        "kategori": "3. Fiskal & Keuangan Pemerintah", "unit": "% of GDP", "weo_code": "GGXCNL_NGDP",
        "desc": "Keseimbangan fiskal bersih pemerintah (defisit/surplus anggaran) sebagai persentase dari PDB.",
        "data": {"2000": -1.2, "2004": -1.0, "2008": 0.0, "2010": -0.7, "2012": -1.8, "2014": -2.2, "2016": -2.5, "2018": -1.8, "2019": -2.2, "2020": -6.1, "2021": -4.6, "2022": -2.4, "2023": -1.7, "2024": -2.2}
    },

    # --- 4. Eksternal & Perdagangan ---
    "Current Account Balance (% of GDP)": {
        "kategori": "4. Eksternal & Perdagangan", "unit": "% of GDP", "weo_code": "BCA_NGDPD",
        "desc": "Saldo transaksi berjalan relatif terhadap PDB nasional.",
        "data": {"2000": 4.8, "2004": 1.5, "2008": 0.0, "2010": 0.7, "2012": -2.7, "2014": -3.1, "2016": -1.8, "2018": -2.9, "2019": -2.7, "2020": -0.4, "2021": 0.3, "2022": 1.0, "2023": -0.2, "2024": -0.9}
    },
    "Current Account Balance (Billion USD)": {
        "kategori": "4. Eksternal & Perdagangan", "unit": "Billion USD", "weo_code": "BCA",
        "desc": "Neraca bersih perdagangan barang, jasa, pendapatan primer, dan sekunder dalam miliar Dolar AS.",
        "data": {"2000": 8.0, "2004": 3.9, "2008": 0.1, "2010": 5.1, "2012": -24.4, "2014": -27.5, "2016": -17.0, "2018": -30.6, "2019": -30.3, "2020": -4.4, "2021": 3.5, "2022": 12.7, "2023": -2.0, "2024": -13.8}
    },

    # --- 5. Investasi & Tabungan ---
    "Total Investment (% of GDP)": {
        "kategori": "5. Investasi & Tabungan", "unit": "% of GDP", "weo_code": "NID_NGDP",
        "desc": "Pembentukan modal bruto total sebagai persentase dari PDB.",
        "data": {"2000": 22.3, "2004": 24.1, "2008": 27.8, "2010": 31.0, "2012": 33.2, "2014": 32.6, "2016": 32.6, "2018": 32.3, "2019": 32.3, "2020": 31.7, "2021": 30.8, "2022": 29.8, "2023": 29.3, "2024": 29.2}
    },
    "Gross National Savings (% of GDP)": {
        "kategori": "5. Investasi & Tabungan", "unit": "% of GDP", "weo_code": "NGSD_NGDP",
        "desc": "Tabungan nasional bruto relatif terhadap PDB.",
        "data": {"2000": 27.1, "2004": 25.6, "2008": 27.8, "2010": 31.7, "2012": 30.5, "2014": 29.5, "2016": 30.8, "2018": 29.4, "2019": 29.6, "2020": 31.3, "2021": 31.1, "2022": 30.8, "2023": 29.1, "2024": 28.3}
    }
}

# 1. Pilihan Indikator Berdasarkan Kategori
st.subheader("1. Pemilihan Indikator IMF")
col_kat, col_ind = st.columns([1, 1.8])

kategori_list = sorted(list(set(v["kategori"] for v in IMF_CATALOG.values())))
with col_kat:
    pilihan_kategori = st.selectbox("Kategori Bidang:", ["Semua Kategori"] + kategori_list)

indikator_opsi = [
    k for k, v in IMF_CATALOG.items()
    if pilihan_kategori == "Semua Kategori" or v["kategori"] == pilihan_kategori
]

with col_ind:
    selected_name = st.selectbox(f"Nama Indikator ({len(indikator_opsi)} Tersedia):", indikator_opsi)

meta = IMF_CATALOG[selected_name]

# 2. Filter Rentang Tahun
st.subheader("2. Rentang Tahun Observasi")
semua_tahun_tersedia = [str(y) for y in range(2000, 2025)]

c_t1, c_t2 = st.columns(2)
with c_t1:
    th_start = st.selectbox("Tahun Mulai:", semua_tahun_tersedia, index=0)
with c_t2:
    th_end = st.selectbox("Tahun Selesai:", semua_tahun_tersedia, index=len(semua_tahun_tersedia) - 1)

if int(th_start) > int(th_end):
    st.error("Tahun mulai tidak boleh melebihi tahun selesai.")
    st.stop()

# 3. Kotak Informasi & Metadata
st.divider()
with st.expander("ℹ️ Definisi & Metadata Resmi IMF WEO", expanded=True):
    st.markdown(f"**Series Name:** {selected_name}")
    st.markdown(f"**Series Code (IMF WEO):** `{meta['weo_code']}`")
    st.markdown(f"**Kategori:** `{meta['kategori']}`")
    st.markdown(f"**Satuan Unit:** `{meta['unit']}`")
    st.markdown(f"**Metodologi / Deskripsi:**\n{meta['desc']}")
    st.markdown(
        f"🔗 **Tautan Resmi:** [Buka Data di IMF DataMapper Portal](https://www.imf.org/external/datamapper/{meta['weo_code']}@WEO/IDN)"
    )

# 4. DataFrame & Visualisasi Plotly
rentang_tahun_pilihan = [str(y) for y in range(int(th_start), int(th_end) + 1)]
df_grid = pd.DataFrame({"Tahun": rentang_tahun_pilihan})

raw_series_df = pd.DataFrame(list(meta["data"].items()), columns=["Tahun", f"Indonesia ({meta['unit']})"])
df_final = pd.merge(df_grid, raw_series_df, on="Tahun", how="left").sort_values("Tahun")

st.subheader(f"📈 Tren Runtun Waktu: {selected_name}")

val_col = f"Indonesia ({meta['unit']})"
fig = go.Figure()
fig.add_trace(go.Scatter(
    x=df_final["Tahun"],
    y=df_final[val_col],
    mode="lines+markers",
    name="Indonesia (IMF WEO)",
    connectgaps=True,
    line=dict(width=2.5, color="#A6192E"),  # Merah Resmi IMF
    hovertemplate=f"Tahun %{{x}}<br>Nilai: %{{y}} {meta['unit']}<extra></extra>"
))

fig.update_layout(
    xaxis=dict(title="Tahun", tickmode="linear"),
    yaxis=dict(title=meta["unit"]),
    hovermode="x unified",
    margin=dict(l=20, r=20, t=40, b=20)
)
st.plotly_chart(fig, use_container_width=True)

# 5. Tabel Observasi & Unduh Data
st.subheader("📋 Tabel Data Observasi")
c_csv, c_xlsx = st.columns(2)

c_csv.download_button(
    "📥 Unduh CSV",
    df_final.to_csv(index=False).encode("utf-8"),
    f"IMF_IDN_{meta['weo_code']}_{th_start}_{th_end}.csv",
    "text/csv"
)

buf = io.BytesIO()
with pd.ExcelWriter(buf, engine="openpyxl") as writer:
    df_final.to_excel(writer, index=False, sheet_name="IMF WEO Data")
c_xlsx.download_button(
    "📊 Unduh Excel (.xlsx)",
    buf.getvalue(),
    f"IMF_IDN_{meta['weo_code']}_{th_start}_{th_end}.xlsx",
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
)

st.dataframe(df_final.fillna("-"), use_container_width=True)
st.caption(
    "💡 **Catatan IMF:** Tanda strip (-) menandakan data pada tahun tersebut tidak dilaporkan pada siklus publikasi WEO."
)

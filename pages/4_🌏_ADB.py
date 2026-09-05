import io
import pandas as pd
import plotly.graph_objects as go
import requests
import streamlit as st

st.set_page_config(page_title="ADB Data Explorer - Indonesia", layout="wide")

st.title("🌏 Asian Development Bank (ADB) - Portal Data Indonesia")
st.write(
    "Eksplorasi indikator makroekonomi, fiskal, dan pembangunan resmi dari **Key Indicators Database (KIDB) Asian Development Bank (ADB)** "
    "khusus untuk **Indonesia** yang ditarik secara langsung (*real-time live API*) dari endpoint resmi ADB."
)

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "application/json"
}

# DAFTAR INDIKATOR RESMI KEY INDICATORS DATABASE (KIDB) ADB UNTUK INDONESIA
# Menggunakan struktur SDMX API resmi ADB: Dataflow & Series Code
ADB_CATALOG = {
    # --- 1. National Accounts (Pendapatan Nasional & Pertumbuhan) ---
    "GDP Growth Rate (% Annual Change)": {
        "dataflow": "EO_NA", "code": "NGDP_RPCH", "unit": "%", "kategori": "1. Pendapatan Nasional & PDB",
        "desc": "Laju pertumbuhan tahunan Produk Domestik Bruto atas dasar harga konstan."
    },
    "Gross Domestic Product at Current Market Prices (Billion USD)": {
        "dataflow": "EO_NA", "code": "NGDPD", "unit": "Billion USD", "kategori": "1. Pendapatan Nasional & PDB",
        "desc": "Produk Domestik Bruto dinilai dalam Dolar AS berlaku."
    },
    "GDP per Capita at Current Market Prices (USD)": {
        "dataflow": "EO_NA", "code": "NGDPDPC", "unit": "USD", "kategori": "1. Pendapatan Nasional & PDB",
        "desc": "PDB per kapita dalam Dolar AS berlaku."
    },
    "Gross Capital Formation / Investment (% of GDP)": {
        "dataflow": "EO_NA", "code": "NID_NGDP", "unit": "% of GDP", "kategori": "1. Pendapatan Nasional & PDB",
        "desc": "Pembentukan modal bruto relatif terhadap PDB nasional."
    },
    "Gross National Savings (% of GDP)": {
        "dataflow": "EO_NA", "code": "NGSD_NGDP", "unit": "% of GDP", "kategori": "1. Pendapatan Nasional & PDB",
        "desc": "Tabungan nasional bruto relatif terhadap PDB nasional."
    },

    # --- 2. Price Indexes & Inflation (Harga & Inflasi) ---
    "Consumer Price Index (CPI, % Annual Change)": {
        "dataflow": "EO_PRC", "code": "PCPIPCH", "unit": "%", "kategori": "2. Inflasi & Indeks Harga",
        "desc": "Perubahan persentase tahunan pada Indeks Harga Konsumen (IHK) nasional."
    },
    "Food Consumer Price Index (% Annual Change)": {
        "dataflow": "EO_PRC", "code": "PCPI_FOOD", "unit": "%", "kategori": "2. Inflasi & Indeks Harga",
        "desc": "Inflasi khusus kelompok pengeluaran bahan makanan (Food CPI)."
    },

    # --- 3. Government Finance (Fiskal & Keuangan Publik) ---
    "Central Government Fiscal Balance (% of GDP)": {
        "dataflow": "EO_GF", "code": "GGXCNL_NGDP", "unit": "% of GDP", "kategori": "3. Keuangan Pemerintah & Fiskal",
        "desc": "Surplus/defisit anggaran pemerintah pusat relatif terhadap PDB."
    },
    "Total Government Revenue (% of GDP)": {
        "dataflow": "EO_GF", "code": "GGR_NGDP", "unit": "% of GDP", "kategori": "3. Keuangan Pemerintah & Fiskal",
        "desc": "Total penerimaan perpajakan dan non-pajak pemerintah pusat terhadap PDB."
    },
    "Total Government Expenditure (% of GDP)": {
        "dataflow": "EO_GF", "code": "GGX_NGDP", "unit": "% of GDP", "kategori": "3. Keuangan Pemerintah & Fiskal",
        "desc": "Total belanja dan pengeluaran pemerintah pusat terhadap PDB."
    },

    # --- 4. Balance of Payments & External Trade (Sektor Eksternal & Neraca Pembayaran) ---
    "Current Account Balance (% of GDP)": {
        "dataflow": "EO_BP", "code": "BCA_NGDPD", "unit": "% of GDP", "kategori": "4. Neraca Pembayaran & Eksternal",
        "desc": "Saldo transaksi berjalan relatif terhadap PDB."
    },
    "Merchandise Exports (FOB, Million USD)": {
        "dataflow": "EO_TRD", "code": "TXG_FOB_USD", "unit": "Million USD", "kategori": "4. Neraca Pembayaran & Eksternal",
        "desc": "Nilai total ekspor barang dagangan secara Free on Board (FOB)."
    },
    "Merchandise Imports (CIF, Million USD)": {
        "dataflow": "EO_TRD", "code": "TMG_CIF_USD", "unit": "Million USD", "kategori": "4. Neraca Pembayaran & Eksternal",
        "desc": "Nilai total impor barang dagangan secara Cost, Insurance, and Freight (CIF)."
    },
    "Gross International Reserves (Million USD)": {
        "dataflow": "EO_BP", "code": "RES_TOT_USD", "unit": "Million USD", "kategori": "4. Neraca Pembayaran & Eksternal",
        "desc": "Cadangan devisa resmi kotor yang dikelola oleh otoritas moneter."
    },

    # --- 5. Social & Demographics (Sosial, Tenaga Kerja & Kemiskinan) ---
    "Poverty Headcount Ratio at National Poverty Line (% of Population)": {
        "dataflow": "SOC_POV", "code": "POV_NAT_LINE", "unit": "%", "kategori": "5. Sosial, Kemiskinan & Tenaga Kerja",
        "desc": "Persentase penduduk yang berada di bawah garis kemiskinan nasional."
    },
    "Total Population (Million Persons)": {
        "dataflow": "PPL_POP", "code": "POP_TOT_VAL", "unit": "Million Persons", "kategori": "5. Sosial, Kemiskinan & Tenaga Kerja",
        "desc": "Estimasi jumlah penduduk total pertengahan tahun."
    },
    "Labor Force Participation Rate (% of Total Working Age)": {
        "dataflow": "SOC_LAB", "code": "LFPR_TOT", "unit": "%", "kategori": "5. Sosial, Kemiskinan & Tenaga Kerja",
        "desc": "Tingkat partisipasi angkatan kerja (TPAK) penduduk usia kerja."
    },
    "Unemployment Rate (% of Total Labor Force)": {
        "dataflow": "SOC_LAB", "code": "LUR_TOT", "unit": "%", "kategori": "5. Sosial, Kemiskinan & Tenaga Kerja",
        "desc": "Tingkat pengangguran terbuka relatif terhadap total angkatan kerja."
    }
}

# =============================================================================
# 1. KONTROL PEMILIHAN INDIKATOR
# =============================================================================
st.subheader("1. Pemilihan Indikator ADB KIDB")
col_kat, col_ind = st.columns([1.2, 2])

kategori_list = sorted(list(set(v["kategori"] for v in ADB_CATALOG.values())))

with col_kat:
    pilihan_kategori = st.selectbox("Kategori Bidang:", ["Semua Kategori"] + kategori_list)

opsi_indikator = [
    k for k, v in ADB_CATALOG.items()
    if pilihan_kategori == "Semua Kategori" or v["kategori"] == pilihan_kategori
]

with col_ind:
    selected_name = st.selectbox("Nama Indikator:", opsi_indikator)

meta = ADB_CATALOG[selected_name]

with st.expander("ℹ️ Definisi & Metadata Resmi ADB", expanded=False):
    st.markdown(f"**Nama Indikator:** {selected_name}")
    st.markdown(f"**Dataflow:** `{meta['dataflow']}`")
    st.markdown(f"**Series Code:** `{meta['code']}`")
    st.markdown(f"**Satuan:** `{meta['unit']}`")
    st.markdown(f"**Metodologi / Deskripsi:**\n{meta['desc']}")
    st.markdown("🔗 **Basis Data:** [ADB Key Indicators Database (KIDB)](https://kidb.adb.org/economies/indonesia)")

# =============================================================================
# 2. PENARIKAN DATA MURNI SECARA LIVE VIA API RESMI ADB
# =============================================================================
st.subheader("2. Penarikan Data Runtun Waktu")

if st.button("📊 Ambil Data ADB Indonesia", type="primary"):
    with st.spinner(f"Menghubungi endpoint resmi ADB KIDB untuk {selected_name}..."):
        # Format query SDMX v4 resmi ADB untuk Indonesia (INO)
        # Endpoint: https://kidb.adb.org/api/v4/sdmx/data/ADB,{dataflow}/A.{code}.INO?format=sdmx-json
        api_url = f"https://kidb.adb.org/api/v4/sdmx/data/ADB,{meta['dataflow']}/A.{meta['code']}.INO?format=sdmx-json"
        
        try:
            res = requests.get(api_url, headers=HEADERS, timeout=20)
            
            records = []
            if res.status_code == 200:
                data_json = res.json()
                
                # Parsing struktur standar SDMX-JSON ADB
                data_sets = data_json.get("data", {}).get("dataSets", [])
                structure = data_json.get("data", {}).get("structure", {})
                
                # Ambil dimensi waktu (Time Periods)
                time_periods = []
                obs_dimensions = structure.get("dimensions", {}).get("observation", [])
                for dim in obs_dimensions:
                    if dim.get("id") in ["TIME_PERIOD", "TIME"]:
                        time_periods = [val.get("id") for val in dim.get("values", [])]
                        break
                
                # Ambil nilai observasi
                if data_sets and time_periods:
                    series_dict = data_sets[0].get("series", {})
                    # Ambil series pertama
                    for s_key, s_val in series_dict.items():
                        observations = s_val.get("observations", {})
                        for time_idx_str, obs_val_list in observations.items():
                            try:
                                idx = int(time_idx_str)
                                if idx < len(time_periods) and obs_val_list:
                                    val = float(obs_val_list[0])
                                    records.append({
                                        "Tahun": int(time_periods[idx]),
                                        f"Nilai ({meta['unit']})": round(val, 2)
                                    })
                            except (ValueError, TypeError, IndexError):
                                continue

            if records:
                df_adb = pd.DataFrame(records).sort_values(by="Tahun", ascending=True)
                val_col = f"Nilai ({meta['unit']})"

                st.success(f"Berhasil menarik {len(df_adb)} observasi tahunan langsung dari ADB!")
                
                st.divider()
                st.markdown(f"🔗 **Tautan Data Portal Resmi:** [ADB KIDB Indonesia Profile](https://kidb.adb.org/economies/indonesia)")

                # Tombol Unduh Data
                c1, c2 = st.columns(2)
                c1.download_button(
                    "📥 Unduh CSV",
                    df_adb.to_csv(index=False).encode("utf-8"),
                    f"ADB_IDN_{meta['code']}.csv",
                    "text/csv"
                )
                buf = io.BytesIO()
                with pd.ExcelWriter(buf, engine="openpyxl") as writer:
                    df_adb.to_excel(writer, index=False, sheet_name="ADB Data")
                c2.download_button(
                    "📊 Unduh Excel (.xlsx)",
                    buf.getvalue(),
                    f"ADB_IDN_{meta['code']}.xlsx",
                    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )

                # Visualisasi Interaktif Plotly (Corak Biru Khas ADB)
                fig = go.Figure()
                fig.add_trace(go.Scatter(
                    x=df_adb["Tahun"],
                    y=df_adb[val_col],
                    mode="lines+markers",
                    name="Indonesia (ADB KIDB)",
                    line=dict(width=2.5, color="#005B94"),  # Biru ADB
                    hovertemplate=f"Tahun %{{x}}<br>Nilai: %{{y}} {meta['unit']}<extra></extra>"
                ))
                fig.update_layout(
                    xaxis=dict(title="Tahun", tickmode="linear"),
                    yaxis=dict(title=meta["unit"]),
                    hovermode="x unified",
                    margin=dict(l=20, r=20, t=40, b=20)
                )
                st.plotly_chart(fig, use_container_width=True)

                with st.expander("📋 Tabel Runtun Waktu Lengkap"):
                    st.dataframe(
                        df_adb.sort_values(by="Tahun", ascending=False),
                        use_container_width=True
                    )
            else:
                st.warning("Observasi runtun waktu untuk indikator ini belum dilaporkan atau sedang dalam pembaruan berkala di server ADB.")
        except Exception as e:
            st.error(f"Gagal terhubung ke endpoint resmi ADB: {e}")

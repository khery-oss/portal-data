import io
import pandas as pd
import plotly.graph_objects as go
import requests
import streamlit as st

st.set_page_config(page_title="OECD Explorer - IndoEcon", layout="wide")

st.title("🏛️ OECD Data Hub - Indonesia Economic Indicators")
st.markdown(
    "Portal observasi data makroekonomi dan struktural Indonesia resmi dari "
    "**OECD (Organisation for Economic Co-operation and Development)** "
    "secara *real-time* (*100% Live API Streaming*)."
)

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "application/vnd.sdmx.data+json;version=1.0.0-wd"
}

# KATALOG INDIKATOR MAKROEKONOMI INDONESIA DARI OECD
OECD_CATALOG = {
    # --- 1. Inflasi & Harga ---
    "Inflasi IHK Tahunan (CPI All Items, YoY %)": {
        "dataset": "PRICES_CPI",
        "filter": "IDN.CPALTT01.GY.A",
        "kategori": "1. Harga & Inflasi",
        "unit": "% Pertumbuhan YoY",
        "desc": "Consumer Price Index (CPI) all items, mengukur laju inflasi harga konsumen tahunan Indonesia."
    },
    "Inflasi Pangan (CPI Food, YoY %)": {
        "dataset": "PRICES_CPI",
        "filter": "IDN.CP010000.GY.A",
        "kategori": "1. Harga & Inflasi",
        "unit": "% Pertumbuhan YoY",
        "desc": "Tingkat inflasi kelompok bahan makanan dan minuman non-alkohol di Indonesia."
    },
    "Inflasi Energi (CPI Energy, YoY %)": {
        "dataset": "PRICES_CPI",
        "filter": "IDN.CP040500.GY.A",
        "kategori": "1. Harga & Inflasi",
        "unit": "% Pertumbuhan YoY",
        "desc": "Laju inflasi kelompok energi dan utilitas rumah tangga."
    },

    # --- 2. Pertumbuhan & PDB ---
    "Pertumbuhan PDB Riil Tahunan (Real GDP Growth, YoY %)": {
        "dataset": "SNA_TABLE1",
        "filter": "IDN.B1_GE.GY.A",
        "kategori": "2. Pertumbuhan Ekonomi",
        "unit": "% Pertumbuhan Riil",
        "desc": "Tingkat pertumbuhan tahunan Produk Domestik Bruto riil Indonesia."
    },
    "PDB per Kapita (USD Konstan, PPP)": {
        "dataset": "SNA_TABLE1",
        "filter": "IDN.B1_GE_HRS.CPC.A",
        "kategori": "2. Pertumbuhan Ekonomi",
        "unit": "USD PPP",
        "desc": "Gross Domestic Product per kapita berbasis Purchasing Power Parity (keseimbangan kemampuan berbelanja)."
    },

    # --- 3. Ketenagakerjaan & Produktivitas ---
    "Tingkat Pengangguran Terbuka (Harmonised Unemployment Rate, %)": {
        "dataset": "HUR",
        "filter": "IDN.TOT.PC_LF.A",
        "kategori": "3. Ketenagakerjaan",
        "unit": "% Angkatan Kerja",
        "desc": "Tingkat pengangguran terharmonisasi standar OECD untuk Indonesia."
    },
    "Tingkat Partisipasi Angkatan Kerja (Labour Force Participation Rate, %)": {
        "dataset": "STLABOUR",
        "filter": "IDN.LFPR.TOT.A",
        "kategori": "3. Ketenagakerjaan",
        "unit": "%",
        "desc": "Persentase angkatan kerja aktif terhadap populasi usia produktif."
    },

    # --- 4. Sektor Keuangan, Pajak & Fiskal ---
    "Rasio Penerimaan Pajak terhadap PDB (Tax-to-GDP Ratio, %)": {
        "dataset": "REV",
        "filter": "IDN.TOTALTAX.TAXGDP.A",
        "kategori": "4. Keuangan Publik & Pajak",
        "unit": "% PDB",
        "desc": "Total penerimaan perpajakan pemerintah Indonesia dibandingkan dengan nilai nominal PDB."
    },
    "Suku Bunga Jangka Pendek (Short-term Interest Rate, %)": {
        "dataset": "KEI",
        "filter": "IDN.IRSTCI01.ST.A",
        "kategori": "4. Keuangan Publik & Pajak",
        "unit": "% per Tahun",
        "desc": "Tingkat suku bunga pasar uang antarbank jangka pendek di Indonesia."
    },

    # --- 5. Perdagangan Internasional ---
    "Pertumbuhan Ekspor Riil (Real Exports Growth, YoY %)": {
        "dataset": "SNA_TABLE1",
        "filter": "IDN.P6.GY.A",
        "kategori": "5. Perdagangan Luar Negeri",
        "unit": "% Pertumbuhan Riil",
        "desc": "Laju pertumbuhan volume ekspor barang dan jasa Indonesia secara riil."
    },
    "Pertumbuhan Impor Riil (Real Imports Growth, YoY %)": {
        "dataset": "SNA_TABLE1",
        "filter": "IDN.P7.GY.A",
        "kategori": "5. Perdagangan Luar Negeri",
        "unit": "% Pertumbuhan Riil",
        "desc": "Laju pertumbuhan volume impor barang dan jasa Indonesia secara riil."
    }
}

# =============================================================================
# 1. KONTROL PILIHAN INDIKATOR
# =============================================================================
st.subheader("1. Pemilihan Indikator OECD Indonesia")
c_kat, c_ind = st.columns([1.2, 2])

daftar_kategori = sorted(list(set(v["kategori"] for v in OECD_CATALOG.values())))
with c_kat:
    kat_pilihan = st.selectbox("Kategori Bidang:", ["Semua Kategori"] + daftar_kategori)

opsi = [
    k for k, v in OECD_CATALOG.items()
    if kat_pilihan == "Semua Kategori" or v["kategori"] == kat_pilihan
]

with c_ind:
    nama_indikator = st.selectbox(f"Pilih Indikator ({len(opsi)} Tersedia):", opsi)

meta = OECD_CATALOG[nama_indikator]

with st.expander("ℹ️ Definisi & Metadata Resmi OECD", expanded=False):
    st.markdown(f"**Indikator:** {nama_indikator}")
    st.markdown(f"**Dataset OECD:** `{meta['dataset']}`")
    st.markdown(f"**Kode Filter SDMX:** `{meta['filter']}`")
    st.markdown(f"**Satuan Pengukuran:** `{meta['unit']}`")
    st.markdown(f"**Metodologi / Deskripsi:**\n{meta['desc']}")
    st.markdown("🔗 **Portal Sumber Resmi:** [OECD Data Explorer](https://data-explorer.oecd.org/)")

# =============================================================================
# 2. PENARIKAN DATA LIVE API DARI SERVER OECD
# =============================================================================
st.subheader("2. Penarikan Data Runtun Waktu")

c_start, c_end = st.columns(2)
with c_start:
    th_awal = st.number_input("Tahun Mulai:", min_value=1990, max_value=2025, value=2005)
with c_end:
    th_akhir = st.number_input("Tahun Akhir:", min_value=1995, max_value=2026, value=2024)

if st.button("📊 Ambil Data OECD (Live API)", type="primary"):
    with st.spinner(f"Menghubungi server OECD API untuk seri {nama_indikator}..."):
        # Endpoint SDMX REST API resmi OECD
        api_url = f"https://stats.oecd.org/SDMX-JSON/data/{meta['dataset']}/{meta['filter']}/all"
        params = {
            "startTime": str(th_awal),
            "endTime": str(th_akhir),
            "dimensionAtObservation": "AllDimensions"
        }

        try:
            res = requests.get(api_url, params=params, headers=HEADERS, timeout=25)
            
            if res.status_code == 200:
                payload = res.json()
                
                # Ekstraksi struktur dimensi waktu SDMX-JSON
                structure = payload.get("structure", {})
                dimensions = structure.get("dimensions", {}).get("observation", [])
                
                time_idx = None
                time_values = []
                for idx, dim in enumerate(dimensions):
                    if dim.get("id") in ["TIME_PERIOD", "TIME", "Year"]:
                        time_idx = idx
                        time_values = [item.get("id") for item in dim.get("values", [])]
                        break

                data_sets = payload.get("dataSets", [])
                records = []

                if data_sets and time_values:
                    observations = data_sets[0].get("observations", {})
                    for key_coords, val_array in observations.items():
                        coords = [int(x) for x in key_coords.split(":")]
                        if time_idx is not None and time_idx < len(coords):
                            t_pos = coords[time_idx]
                            if t_pos < len(time_values):
                                periode = time_values[t_pos]
                                nilai = val_array[0]
                                if nilai is not None:
                                    try:
                                        th_int = int(str(periode)[:4])
                                        records.append({"Tahun": th_int, "Nilai": float(nilai)})
                                    except ValueError:
                                        continue

                if records:
                    val_col = f"Nilai ({meta['unit']})"
                    df_raw = pd.DataFrame(records)
                    df_oecd = df_raw.groupby("Tahun", as_index=False)["Nilai"].mean().round(2)
                    df_oecd = df_oecd.rename(columns={"Nilai": val_col}).sort_values(by="Tahun", ascending=True)

                    st.success(f"Berhasil menarik {len(df_oecd)} observasi runtun waktu resmi langsung dari server OECD!")
                    st.divider()

                    # Tombol Unduh Data
                    c1, c2 = st.columns(2)
                    c1.download_button(
                        "📥 Unduh CSV",
                        df_oecd.to_csv(index=False).encode("utf-8"),
                        f"OECD_Indonesia_{meta['dataset']}.csv",
                        "text/csv"
                    )
                    buf = io.BytesIO()
                    with pd.ExcelWriter(buf, engine="openpyxl") as writer:
                        df_oecd.to_excel(writer, index=False, sheet_name="OECD Data")
                    c2.download_button(
                        "📊 Unduh Excel (.xlsx)",
                        buf.getvalue(),
                        f"OECD_Indonesia_{meta['dataset']}.xlsx",
                        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                    )

                    # Visualisasi Plotly
                    fig = go.Figure()
                    fig.add_trace(go.Scatter(
                        x=df_oecd["Tahun"],
                        y=df_oecd[val_col],
                        mode="lines+markers",
                        name="Indonesia (OECD Data)",
                        line=dict(width=2.8, color="#0E4D92"),
                        marker=dict(size=7),
                        hovertemplate=f"Tahun %{{x}}<br>Nilai: %{{y:,.2f}} {meta['unit']}<extra></extra>"
                    ))
                    fig.update_layout(
                        xaxis=dict(title="Tahun", tickmode="linear"),
                        yaxis=dict(title=meta["unit"]),
                        hovermode="x unified",
                        margin=dict(l=20, r=20, t=30, b=20)
                    )
                    st.plotly_chart(fig, use_container_width=True)

                    with st.expander("📋 Tabel Runtun Waktu Lengkap"):
                        st.dataframe(df_oecd.sort_values(by="Tahun", ascending=False), use_container_width=True)
                else:
                    st.warning("Data observasi untuk rentang tahun ini tidak ditemukan di basis data OECD.")
            else:
                st.error(f"Gagal menghubungi server OECD (Status HTTP: {res.status_code}).")
        except Exception as e:
            st.error(f"Terjadi kesalahan saat memproses data OECD: {e}")

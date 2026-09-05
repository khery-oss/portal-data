import io
import pandas as pd
import plotly.graph_objects as go
import requests
import streamlit as st

st.set_page_config(page_title="ASEANstats Data Explorer - Indonesia & Regional", layout="wide")

st.title("🌏 ASEANstats Data Portal - Indonesia & Regional ASEAN")
st.write(
    "Eksplorasi indikator makroekonomi, sektoral, dan **ASEAN SDG Indicators** dari "
    "**ASEANstats Data Portal (Sekretariat ASEAN, Jakarta)** yang ditarik secara **100% live API** "
    "langsung dari server resmi `data.aseanstats.org`."
)

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "application/json"
}

# KATALOG RESMI ASEANSTATS: MAKROEKONOMI, SEKTORAL & ASEAN SDG INDICATORS
ASEANSTATS_CATALOG = {
    # =========================================================================
    # 1. Makroekonomi & PDB (ASEAN Key Statistics)
    # =========================================================================
    "GDP Growth in ASEAN (Year-on-Year %)": {
        "code": "AST.STC.TBL.6",
        "kategori": "1. Makroekonomi & PDB",
        "unit": "%",
        "desc": "Laju pertumbuhan tahunan Produk Domestik Bruto riil di negara anggota ASEAN."
    },
    "Inflation Rates in ASEAN (Year-on-Year Average %)": {
        "code": "AST.STC.TBL.8",
        "kategori": "1. Makroekonomi & PDB",
        "unit": "%",
        "desc": "Laju inflasi rata-rata tahunan berdasarkan Indeks Harga Konsumen (IHK)."
    },

    # =========================================================================
    # 2. ASEAN Sustainable Development Goals (data.aseanstats.org/sdg)
    # =========================================================================
    "SDG 1.1.1: Proportion of Population Below International Poverty Line (%)": {
        "code": "SDG.1.1.1",
        "kategori": "2. ASEAN SDG Indicators",
        "unit": "%",
        "desc": "Persentase penduduk yang hidup di bawah garis kemiskinan internasional di kawasan ASEAN."
    },
    "SDG 1.2.1: Proportion of Population Living Below National Poverty Line (%)": {
        "code": "SDG.1.2.1",
        "kategori": "2. ASEAN SDG Indicators",
        "unit": "%",
        "desc": "Persentase penduduk yang hidup di bawah garis kemiskinan nasional masing-masing negara."
    },
    "SDG 8.2.1: Annual Growth Rate of Real GDP per Employed Person (%)": {
        "code": "SDG.8.2.1",
        "kategori": "2. ASEAN SDG Indicators",
        "unit": "%",
        "desc": "Laju pertumbuhan tahunan PDB riil per tenaga kerja yang bekerja (produktivitas tenaga kerja regional)."
    },
    "SDG 8.5.2: Unemployment Rate by Sex and Age (%)": {
        "code": "SDG.8.5.2",
        "kategori": "2. ASEAN SDG Indicators",
        "unit": "%",
        "desc": "Tingkat pengangguran terbuka nasional yang dipantau dalam kerangka SDGs ASEAN."
    },
    "SDG 9.2.1: Manufacturing Value Added as a Proportion of GDP (%)": {
        "code": "SDG.9.2.1",
        "kategori": "2. ASEAN SDG Indicators",
        "unit": "% of GDP",
        "desc": "Nilai tambah sektor industri manufaktur sebagai proporsi dari total PDB negara anggota."
    },
    "SDG 7.2.1: Renewable Energy Share in the Total Final Energy Consumption (%)": {
        "code": "SDG.7.2.1",
        "kategori": "2. ASEAN SDG Indicators",
        "unit": "%",
        "desc": "Pangsa energi terbarukan dalam total konsumsi energi akhir di negara-negara ASEAN."
    },

    # =========================================================================
    # 3. Ketenagakerjaan & Tenaga Kerja Informal
    # =========================================================================
    "Rate of Informal Employment by Sex (%)": {
        "code": "LNK.IEMP.1.RATE.02",
        "kategori": "3. Ketenagakerjaan & Sektor Informal",
        "unit": "%",
        "desc": "Tingkat partisipasi pekerja sektor informal terhadap total angkatan kerja yang bekerja."
    },

    # =========================================================================
    # 4. Konektivitas & Infrastruktur Regional (Transport Statistics)
    # =========================================================================
    "Total Registered Road Motor Vehicles (Thousand Units)": {
        "code": "ASE.TRP.ROD.B.005",
        "kategori": "4. Konektivitas & Infrastruktur Regional",
        "unit": "Ribu Unit",
        "desc": "Jumlah total kendaraan bermotor yang terdaftar resmi dan beroperasi di jalan darat."
    },
    "Total Road Network Length (Kilometer)": {
        "code": "ASE.TRP.ROD.A.001",
        "kategori": "4. Konektivitas & Infrastruktur Regional",
        "unit": "Km",
        "desc": "Panjang total jaringan jalan raya nasional di negara anggota ASEAN."
    },
    "International Aircraft Traffic (Flight Movements)": {
        "code": "ASE.TRP.AIR.C.312",
        "kategori": "4. Konektivitas & Infrastruktur Regional",
        "unit": "Pergerakan Penerbangan",
        "desc": "Total frekuensi pergerakan pesawat udara untuk rute penerbangan internasional."
    },
    "International Passengers in Transit (Thousand Persons)": {
        "code": "ASE.TRP.AIR.C.309",
        "kategori": "4. Konektivitas & Infrastruktur Regional",
        "unit": "Ribu Orang",
        "desc": "Volume penumpang internasional yang transit di bandara negara bersangkutan."
    },
    "Number of International Ports (Count)": {
        "code": "ASE.TRP.WTR.A.202",
        "kategori": "4. Konektivitas & Infrastruktur Regional",
        "unit": "Pelabuhan",
        "desc": "Jumlah pelabuhan laut internasional yang beroperasi melayani perdagangan laut global."
    }
}

# =============================================================================
# 1. KONTROL PEMILIHAN INDIKATOR
# =============================================================================
st.subheader("1. Pemilihan Indikator ASEANstats")
col_kat, col_ind = st.columns([1.2, 2])

daftar_kategori = sorted(list(set(v["kategori"] for v in ASEANSTATS_CATALOG.values())))
with col_kat:
    pilih_kategori = st.selectbox("Kategori Bidang / Modul:", ["Semua Kategori"] + daftar_kategori)

opsi_indikator = [
    k for k, v in ASEANSTATS_CATALOG.items()
    if pilih_kategori == "Semua Kategori" or v["kategori"] == pilih_kategori
]

with col_ind:
    nama_indikator = st.selectbox(f"Nama Indikator ({len(opsi_indikator)} Tersedia):", opsi_indikator)

meta = ASEANSTATS_CATALOG[nama_indikator]
kode_api = meta["code"]

with st.expander("ℹ️ Definisi & Metadata Resmi ASEANstats", expanded=False):
    st.markdown(f"**Indikator:** {nama_indikator}")
    st.markdown(f"**Kode Seri API:** `{kode_api}`")
    st.markdown(f"**Kategori / Modul:** `{meta['kategori']}`")
    st.markdown(f"**Satuan Pengukuran:** `{meta['unit']}`")
    st.markdown(f"**Metodologi / Deskripsi:**\n{meta['desc']}")
    st.markdown("🔗 **Portal Sumber:** [ASEANstats Data Portal](https://data.aseanstats.org/) | [ASEAN SDG Portal](https://data.aseanstats.org/sdg)")

# =============================================================================
# 2. PENARIKAN DATA LIVE VIA REST API DATA.ASEANSTATS.ORG
# =============================================================================
st.subheader("2. Penarikan Data Runtun Waktu")

if st.button("📊 Ambil Data ASEANstats", type="primary"):
    with st.spinner(f"Menghubungi endpoint resmi ASEANstats Jakarta untuk seri {kode_api}..."):
        api_url = f"https://data.aseanstats.org/api/indicator/{kode_api}"
        records = []
        
        try:
            res = requests.get(api_url, headers=HEADERS, timeout=25)
            
            if res.status_code == 200:
                payload = res.json()
                data_list = payload if isinstance(payload, list) else payload.get("data", [])
                
                # Standarisasi pemetaan kode negara ASEAN
                MAP_NEGARA = {
                    "ID": "Indonesia", "IDN": "Indonesia", "Indonesia": "Indonesia",
                    "MY": "Malaysia", "MYS": "Malaysia", "Malaysia": "Malaysia",
                    "SG": "Singapore", "SGP": "Singapore", "Singapore": "Singapore",
                    "TH": "Thailand", "THA": "Thailand", "Thailand": "Thailand",
                    "VN": "Viet Nam", "VNM": "Viet Nam", "Viet Nam": "Viet Nam", "Vietnam": "Viet Nam",
                    "PH": "Philippines", "PHL": "Philippines", "Philippines": "Philippines",
                    "BN": "Brunei Darussalam", "BRN": "Brunei Darussalam",
                    "KH": "Cambodia", "KHM": "Cambodia",
                    "LA": "Lao PDR", "LAO": "Lao PDR",
                    "MM": "Myanmar", "MMR": "Myanmar"
                }

                for item in data_list:
                    raw_country = (
                        item.get("country_name") or 
                        item.get("country") or 
                        item.get("country_code") or 
                        item.get("Country")
                    )
                    thn = item.get("period") or item.get("year") or item.get("time_period") or item.get("Year")
                    val = item.get("value") or item.get("indicator_value") or item.get("Value")
                    
                    if raw_country and thn is not None and val is not None:
                        clean_country_name = MAP_NEGARA.get(str(raw_country).strip(), str(raw_country).strip())
                        try:
                            clean_thn = int(str(thn)[:4])
                            clean_val = float(str(val).replace(",", "").replace("<", "").replace(">", "").strip())
                            records.append({
                                "Negara": clean_country_name,
                                "Tahun": clean_thn,
                                "Nilai": clean_val
                            })
                        except (ValueError, TypeError):
                            continue

            if records:
                raw_df = pd.DataFrame(records)
                
                # Rata-rata jika ada breakdown gender/wilayah pada tahun yang sama
                raw_df = raw_df.groupby(["Negara", "Tahun"], as_index=False)["Nilai"].mean().round(2)

                daftar_negara = sorted(raw_df["Negara"].unique())
                default_sel = ["Indonesia"] if "Indonesia" in daftar_negara else [daftar_negara[0]]

                st.success(f"Berhasil menarik {len(raw_df)} observasi data langsung dari server ASEANstats!")
                st.divider()

                # Filter Negara Interaktif
                pilihan_negara = st.multiselect(
                    "Pilih Negara Anggota ASEAN untuk Ditampilkan:",
                    options=daftar_negara,
                    default=default_sel
                )

                if pilihan_negara:
                    df_filtered = raw_df[raw_df["Negara"].isin(pilihan_negara)]
                    
                    df_pivot = df_filtered.pivot_table(
                        index="Tahun",
                        columns="Negara",
                        values="Nilai"
                    ).sort_index(ascending=True).reset_index()

                    # Tombol Unduh
                    c1, c2 = st.columns(2)
                    c1.download_button(
                        "📥 Unduh CSV",
                        df_pivot.to_csv(index=False).encode("utf-8"),
                        f"ASEANstats_{kode_api}.csv",
                        "text/csv"
                    )
                    buf = io.BytesIO()
                    with pd.ExcelWriter(buf, engine="openpyxl") as writer:
                        df_pivot.to_excel(writer, index=False, sheet_name="ASEANstats Data")
                    c2.download_button(
                        "📊 Unduh Excel (.xlsx)",
                        buf.getvalue(),
                        f"ASEANstats_{kode_api}.xlsx",
                        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                    )

                    # Visualisasi Plotly
                    WARNA_NEGARA = {
                        "Indonesia": "#DC241F",
                        "Singapore": "#9B0000",
                        "Malaysia": "#003399",
                        "Viet Nam": "#D4AF37",
                        "Thailand": "#4A90E2",
                        "Philippines": "#50B848",
                        "Brunei Darussalam": "#F1C40F",
                        "Cambodia": "#8E44AD",
                        "Lao PDR": "#E67E22",
                        "Myanmar": "#16A085"
                    }

                    fig = go.Figure()
                    for c in pilihan_negara:
                        if c in df_pivot.columns:
                            is_indo = (c == "Indonesia")
                            warna = WARNA_NEGARA.get(c, None)
                            fig.add_trace(go.Scatter(
                                x=df_pivot["Tahun"],
                                y=df_pivot[c],
                                mode="lines+markers",
                                name=c,
                                line=dict(width=3.5 if is_indo else 2.0, color=warna),
                                marker=dict(size=8 if is_indo else 5),
                                connectgaps=False,
                                hovertemplate=f"<b>{c}</b><br>Tahun %{{x}}<br>Nilai: %{{y:,.2f}} {meta['unit']}<extra></extra>"
                            ))

                    fig.update_layout(
                        xaxis=dict(title="Tahun", tickmode="linear"),
                        yaxis=dict(title=meta["unit"]),
                        hovermode="x unified",
                        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
                        margin=dict(l=20, r=20, t=50, b=20)
                    )
                    st.plotly_chart(fig, use_container_width=True)

                    with st.expander("📋 Tabel Runtun Waktu Lengkap"):
                        st.dataframe(df_pivot.sort_values(by="Tahun", ascending=False).fillna("-"), use_container_width=True)
                else:
                    st.warning("Pilih setidaknya satu negara untuk melihat visualisasi.")
            else:
                st.warning("Observasi data untuk indikator ini belum dilaporkan atau sedang dalam pembaruan berkala di server ASEANstats.")
        except Exception as e:
            st.error(f"Gagal menghubungi server ASEANstats: {e}")

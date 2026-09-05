import io
import pandas as pd
import plotly.graph_objects as go
import requests
import streamlit as st

st.set_page_config(page_title="ASEANstats Data Explorer - Indonesia & Regional", layout="wide")

st.title("🌏 ASEANstats - Portal Data Regional Asia Tenggara")
st.write(
    "Eksplorasi indikator resmi dari **ASEANstats Data Portal** (Sekretariat ASEAN) "
    "khusus untuk **Indonesia** dan perbandingan negara anggota ASEAN yang ditarik secara **100% langsung (*real-time live API*)**."
)

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "application/json"
}

# KATALOG KODE INDIKATOR RESMI REST API DATA.ASEANSTATS.ORG
ASEAN_API_CATALOG = {
    # --- Transportasi & Infrastruktur ---
    "Total Registered Road Motor Vehicles (Thousand Units)": {
        "code": "ASE.TRP.ROD.B.005", "kategori": "1. Transportasi & Infrastruktur", "unit": "Ribu Unit",
        "desc": "Jumlah total kendaraan bermotor yang terdaftar resmi dan beroperasi di jalan umum."
    },
    "Total Road Network Length (Kilometer)": {
        "code": "ASE.TRP.ROD.A.001", "kategori": "1. Transportasi & Infrastruktur", "unit": "Km",
        "desc": "Panjang total jaringan jalan raya nasional."
    },
    "Number of International Ports (Count)": {
        "code": "ASE.TRP.WTR.A.202", "kategori": "1. Transportasi & Infrastruktur", "unit": "Pelabuhan",
        "desc": "Jumlah pelabuhan laut internasional yang beroperasi melayani perdagangan antarnegara."
    },
    "International Aircraft Traffic (Flight Movements)": {
        "code": "ASE.TRP.AIR.C.312", "kategori": "1. Transportasi & Infrastruktur", "unit": "Penerbangan",
        "desc": "Frekuensi lalu lintas pergerakan pesawat udara rute penerbangan internasional."
    },
    "International Passengers in Transit (Thousand Persons)": {
        "code": "ASE.TRP.AIR.C.309", "kategori": "1. Transportasi & Infrastruktur", "unit": "Ribu Orang",
        "desc": "Volume penumpang penerbangan internasional yang transit di bandara negara bersangkutan."
    },

    # --- Keselamatan Transportasi ---
    "Road Traffic Accident Injuries (Persons)": {
        "code": "ASE.TRP.ROD.E.031", "kategori": "2. Keselamatan Transportasi", "unit": "Orang",
        "desc": "Jumlah korban luka-luka akibat kecelakaan lalu lintas darat."
    },

    # --- Ketenagakerjaan & Sosial ---
    "Rate of Informal Employment by Sex (%)": {
        "code": "LNK.IEMP.1.RATE.02", "kategori": "3. Ketenagakerjaan & Sosial", "unit": "%",
        "desc": "Proporsi tenaga kerja di sektor informal terhadap total angkatan kerja yang bekerja."
    }
}

# 1. Pemilihan Indikator
st.subheader("1. Pemilihan Indikator Resmi ASEANstats")
col_kat, col_ind = st.columns([1.2, 2])

daftar_kategori = sorted(list(set(v["kategori"] for v in ASEAN_API_CATALOG.values())))
with col_kat:
    pilih_kategori = st.selectbox("Kategori Bidang:", ["Semua Kategori"] + daftar_kategori)

opsi = [
    k for k, v in ASEAN_API_CATALOG.items()
    if pilih_kategori == "Semua Kategori" or v["kategori"] == pilih_kategori
]

with col_ind:
    nama_indikator = st.selectbox("Pilih Indikator:", opsi)

meta = ASEAN_API_CATALOG[nama_indikator]
kode_api = meta["code"]

with st.expander("ℹ️ Definisi & Metadata Resmi ASEANstats", expanded=False):
    st.markdown(f"**Indikator:** {nama_indikator}")
    st.markdown(f"**Kode API Resmi:** `{kode_api}`")
    st.markdown(f"**Kategori:** `{meta['kategori']}`")
    st.markdown(f"**Satuan:** `{meta['unit']}`")
    st.markdown(f"**Deskripsi:**\n{meta['desc']}")
    st.markdown("🔗 **Portal Sumber:** [ASEANstats Data Portal](https://data.aseanstats.org/)")

# 2. Pengambilan Data Live dari REST API ASEANstats
st.subheader("2. Penarikan Data Runtun Waktu")

if st.button("📊 Ambil Data ASEANstats", type="primary"):
    with st.spinner(f"Menghubungi endpoint resmi ASEANstats Jakarta untuk seri {kode_api}..."):
        api_url = f"https://data.aseanstats.org/api/indicator/{kode_api}"
        
        try:
            res = requests.get(api_url, headers=HEADERS, timeout=25)
            
            records = []
            if res.status_code == 200:
                payload = res.json()
                # Tangani variasi struktur respon JSON ASEANstats
                data_list = payload if isinstance(payload, list) else payload.get("data", [])
                
                for item in data_list:
                    negara = item.get("country") or item.get("country_name") or item.get("country_code")
                    thn = item.get("period") or item.get("year") or item.get("time_period")
                    val = item.get("value") or item.get("indicator_value")
                    
                    if negara and thn is not None and val is not None:
                        try:
                            clean_thn = int(str(thn)[:4])
                            clean_val = float(str(val).replace(",", "").strip())
                            records.append({
                                "Negara": str(negara).strip(),
                                "Tahun": clean_thn,
                                "Nilai": clean_val
                            })
                        except (ValueError, TypeError):
                            continue

            if records:
                raw_df = pd.DataFrame(records)
                
                # Standarisasi nama Indonesia
                raw_df["Negara"] = raw_df["Negara"].replace({
                    "ID": "Indonesia",
                    "IDN": "Indonesia"
                })
                
                daftar_negara = sorted(raw_df["Negara"].unique())
                default_selection = ["Indonesia"] if "Indonesia" in daftar_negara else [daftar_negara[0]]

                st.success(f"Berhasil menarik {len(raw_df)} observasi data langsung dari server ASEANstats!")
                st.divider()

                # Filter Negara Interaktif
                pilihan_negara = st.multiselect(
                    "Pilih Negara Anggota ASEAN untuk Ditampilkan:",
                    options=daftar_negara,
                    default=default_selection
                )

                if pilihan_negara:
                    df_filtered = raw_df[raw_df["Negara"].isin(pilihan_negara)]
                    
                    # Pivot untuk visualisasi dan tabel
                    df_pivot = df_filtered.pivot_table(
                        index="Tahun",
                        columns="Negara",
                        values="Nilai",
                        aggfunc="mean"
                    ).sort_index(ascending=True).reset_index()

                    # Tombol Unduh Data
                    c1, c2 = st.columns(2)
                    c1.download_button(
                        "📥 Unduh CSV",
                        df_pivot.to_csv(index=False).encode("utf-8"),
                        f"ASEANstats_{kode_api}.csv",
                        "text/csv"
                    )
                    buf = io.BytesIO()
                    with pd.ExcelWriter(buf, engine="openpyxl") as writer:
                        df_pivot.to_excel(writer, index=False, sheet_name="ASEANstats")
                    c2.download_button(
                        "📊 Unduh Excel (.xlsx)",
                        buf.getvalue(),
                        f"ASEANstats_{kode_api}.xlsx",
                        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                    )

                    # Visualisasi Plotly Interaktif
                    fig = go.Figure()
                    for c in pilihan_negara:
                        if c in df_pivot.columns:
                            is_indo = (c == "Indonesia")
                            fig.add_trace(go.Scatter(
                                x=df_pivot["Tahun"],
                                y=df_pivot[c],
                                mode="lines+markers",
                                name=c,
                                line=dict(width=3.5 if is_indo else 2.0),
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
                st.warning("Observasi runtun waktu untuk indikator ini belum dilaporkan atau sedang dalam pembaruan berkala di server ASEANstats.")
        except Exception as e:
            st.error(f"Gagal menghubungi server ASEANstats: {e}")

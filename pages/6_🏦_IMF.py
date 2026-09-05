import io
import pandas as pd
import plotly.graph_objects as go
import requests
import streamlit as st

st.set_page_config(page_title="IMF Explorer - IndoEcon", layout="wide")

st.title("🏦 IMF (International Monetary Fund) - Indikator Finansial & Makroekonomi")
st.markdown(
    "Eksplorasi indikator moneter, neraca pembayaran, dan sektor keuangan resmi Indonesia langsung dari "
    "**International Financial Statistics (IFS) IMF API** secara *real-time* (*100% Live API Streaming*)."
)

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

# KATALOG RESMI IFS (INTERNATIONAL FINANCIAL STATISTICS) IMF UNTUK INDONESIA (ID)
IMF_CATALOG = {
    # --- 1. Sektor Moneter & Perbankan ---
    "Uang Beredar Luas / Broad Money (M2, Miliar IDR)": {
        "dataset": "IFS",
        "indicator": "FMB_XDC",
        "kategori": "1. Sektor Moneter & Perbankan",
        "unit": "Miliar Rupiah",
        "desc": "Jumlah uang beredar dalam arti luas (M2) di perekonomian Indonesia."
    },
    "Uang Primer / Base Money (M0, Miliar IDR)": {
        "dataset": "IFS",
        "indicator": "FMA_XDC",
        "kategori": "1. Sektor Moneter & Perbankan",
        "unit": "Miliar Rupiah",
        "desc": "Kewajiban moneter otoritas moneter (uang kartal dan simpanan giro bank komersial di BI)."
    },
    "Suku Bunga Pasar Uang / Money Market Rate (% per Tahun)": {
        "dataset": "IFS",
        "indicator": "FP_PA",
        "kategori": "1. Sektor Moneter & Perbankan",
        "unit": "% per Tahun",
        "desc": "Tingkat suku bunga transaksi pinjam-meminjam likuiditas jangka pendek antarbank."
    },

    # --- 2. Cadangan Devisa & Sektor Eksternal ---
    "Cadangan Devisa Resmi Total (Total Reserves excluding Gold, Juta USD)": {
        "dataset": "IFS",
        "indicator": "RAXG_USD",
        "kategori": "2. Cadangan Devisa & Eksternal",
        "unit": "Juta USD",
        "desc": "Aset cadangan devisa luar negeri yang dikelola otoritas moneter di luar emas moneter."
    },
    "Cadangan Devisa Emas Moneter (SDR Juta)": {
        "dataset": "IFS",
        "indicator": "RA_SDR",
        "kategori": "2. Cadangan Devisa & Eksternal",
        "unit": "Juta SDR",
        "desc": "Total aset cadangan internasional resmi berdenominasi Hak Tarik Khusus (Special Drawing Rights)."
    },
    "Nilai Tukar Efektif Riil (Real Effective Exchange Rate Index)": {
        "dataset": "IFS",
        "indicator": "EREER_IX",
        "kategori": "2. Cadangan Devisa & Eksternal",
        "unit": "Indeks (2010=100)",
        "desc": "Indeks daya saing nilai tukar rupiah terhadap sekeranjang mata uang mitra dagang utama."
    },

    # --- 3. Harga & Inflasi Makro ---
    "Indeks Harga Konsumen (CPI All Items)": {
        "dataset": "IFS",
        "indicator": "PCPI_IX",
        "kategori": "3. Harga & Inflasi",
        "unit": "Indeks (2010=100)",
        "desc": "Indeks harga konsumen harmonisasi IMF untuk pengukuran pergerakan harga barang dan jasa."
    },
    "Indeks Harga Produsen (Producer Price Index)": {
        "dataset": "IFS",
        "indicator": "PPI_IX",
        "kategori": "3. Harga & Inflasi",
        "unit": "Indeks (2010=100)",
        "desc": "Indeks rata-rata perubahan harga jual domestik yang diterima produsen lokal."
    }
}

# =============================================================================
# 1. KONTROL PILIHAN INDIKATOR
# =============================================================================
st.subheader("1. Pemilihan Indikator IMF")
c_kat, c_ind = st.columns([1.2, 2])

kategori_list = sorted(list(set(v["kategori"] for v in IMF_CATALOG.values())))
with c_kat:
    kat_pilihan = st.selectbox("Kategori Bidang:", ["Semua Kategori"] + kategori_list)

opsi = [
    k for k, v in IMF_CATALOG.items()
    if kat_pilihan == "Semua Kategori" or v["kategori"] == kat_pilihan
]

with c_ind:
    nama_indikator = st.selectbox(f"Pilih Indikator ({len(opsi)} Tersedia):", opsi)

meta = IMF_CATALOG[nama_indikator]

with st.expander("ℹ️ Definisi & Metadata Resmi IMF", expanded=False):
    st.markdown(f"**Indikator:** {nama_indikator}")
    st.markdown(f"**Dataset IMF:** `{meta['dataset']}`")
    st.markdown(f"**Kode Seri:** `{meta['indicator']}`")
    st.markdown(f"**Satuan Pengukuran:** `{meta['unit']}`")
    st.markdown(f"**Metodologi / Deskripsi:**\n{meta['desc']}")
    st.markdown("🔗 **Portal Sumber Resmi:** [IMF eLibrary Data Services](https://data.imf.org/)")

# =============================================================================
# 2. PENARIKAN DATA RUN TUN WAKTU OTOMATIS
# =============================================================================
st.subheader("2. Penarikan Data Runtun Waktu Nasional")
st.caption("Data akan ditarik secara lengkap untuk seluruh riwayat tahun yang disediakan oleh server resmi IMF.")

if st.button("📊 Ambil Data IMF (Live API)", type="primary"):
    with st.spinner(f"Menghubungi server IMF Data Services untuk seri {nama_indikator}..."):
        # Format pemanggilan data tahunan (A) resmi IMF untuk Indonesia (ID)
        api_url = f"https://dataservices.imf.org/REST/SDMX_JSON.svc/CompactData/{meta['dataset']}/A.ID.{meta['indicator']}"

        try:
            res = requests.get(api_url, headers=HEADERS, timeout=25)
            
            if res.status_code == 200:
                payload = res.json()
                series_data = (
                    payload.get("CompactData", {})
                    .get("DataSet", {})
                    .get("Series", {})
                )

                obs_list = []
                if isinstance(series_data, dict):
                    obs_raw = series_data.get("Obs", [])
                    if isinstance(obs_raw, list):
                        obs_list = obs_raw
                    elif isinstance(obs_raw, dict):
                        obs_list = [obs_raw]

                records = []
                for ob in obs_list:
                    th = ob.get("@TIME_PERIOD")
                    val = ob.get("@OBS_VALUE")
                    if th and val is not None:
                        try:
                            records.append({
                                "Tahun": int(str(th)[:4]),
                                "Nilai": float(val)
                            })
                        except (ValueError, TypeError):
                            continue

                if records:
                    val_col = f"Nilai ({meta['unit']})"
                    df_imf = pd.DataFrame(records).drop_duplicates(subset=["Tahun"]).sort_values(by="Tahun", ascending=True)
                    df_imf = df_imf.rename(columns={"Nilai": val_col})

                    st.success(f"Berhasil menarik {len(df_imf)} observasi runtun waktu resmi langsung dari server IMF!")
                    st.divider()

                    # Tombol Unduh Data
                    c1, c2 = st.columns(2)
                    c1.download_button(
                        "📥 Unduh CSV",
                        df_imf.to_csv(index=False).encode("utf-8"),
                        f"IMF_Indonesia_{meta['indicator']}.csv",
                        "text/csv"
                    )
                    buf = io.BytesIO()
                    with pd.ExcelWriter(buf, engine="openpyxl") as writer:
                        df_imf.to_excel(writer, index=False, sheet_name="IMF Data")
                    c2.download_button(
                        "📊 Unduh Excel (.xlsx)",
                        buf.getvalue(),
                        f"IMF_Indonesia_{meta['indicator']}.xlsx",
                        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                    )

                    # Visualisasi Plotly Interaktif
                    fig = go.Figure()
                    fig.add_trace(go.Scatter(
                        x=df_imf["Tahun"],
                        y=df_imf[val_col],
                        mode="lines+markers",
                        name="Indonesia (IMF IFS)",
                        line=dict(width=2.8, color="#003366"),
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
                        st.dataframe(df_imf.sort_values(by="Tahun", ascending=False), use_container_width=True)
                else:
                    st.warning("Server IMF merespons, namun deret observasi data kosong.")
            else:
                st.error(f"Gagal menghubungi server IMF (Status HTTP: {res.status_code}).")
        except Exception as e:
            st.error(f"Terjadi kesalahan saat memproses data IMF: {e}")

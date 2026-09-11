import io
import pandas as pd
import plotly.graph_objects as go
import requests
import streamlit as st

st.set_page_config(page_title="WITS Trade Explorer - Indonesia", layout="wide")

st.title("🚢 WITS (World Integrated Trade Solution) - Perdagangan Internasional Indonesia")
st.markdown(
    "Eksplorasi data perdagangan internasional, total nilai ekspor-impor, tarif bea masuk, "
    "dan kinerja perdagangan luar negeri Indonesia dari basis data **World Bank WITS** "
    "secara *real-time* (*100% Live API*)."
)

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

# =============================================================================
# KATALOG INDIKATOR PERDAGANGAN UTAMA WITS / WORLD BANK WDI (MIRROR WITS)
# =============================================================================
WITS_TRADE_CATALOG = {
    # --- 1. Total Merchandise Trade & Values ---
    "Merchandise exports (current US$)": {
        "code": "TX.VAL.MRCH.CD.WT", "kategori": "1. Nilai Perdagangan Barang", "unit": "USD",
        "desc": "Total nilai barang dagangan ekspor dalam USD (Sumber: WITS-UN Comtrade)."
    },
    "Merchandise imports (current US$)": {
        "code": "TM.VAL.MRCH.CD.WT", "kategori": "1. Nilai Perdagangan Barang", "unit": "USD",
        "desc": "Total nilai barang dagangan impor dalam USD (Sumber: WITS-UN Comtrade)."
    },
    "Merchandise trade (% of GDP)": {
        "code": "TG.VAL.TOTL.GD.ZS", "kategori": "1. Nilai Perdagangan Barang", "unit": "% of GDP",
        "desc": "Jumlah total nilai perdagangan barang (ekspor + impor) relatif terhadap PDB."
    },
    "Net barter terms of trade index (2015 = 100)": {
        "code": "TT.PRI.MRCH.XD.WD", "kategori": "1. Nilai Perdagangan Barang", "unit": "Index (2015=100)",
        "desc": "Indeks nilai tukar perdagangan (rasio indeks harga ekspor terhadap impor)."
    },

    # --- 2. Trade Growth & Structures ---
    "Export value index (2015 = 100)": {
        "code": "TX.VAL.MRCH.XD.WD", "kategori": "2. Pertumbuhan & Struktur", "unit": "Index",
        "desc": "Indeks nilai ekspor barang dagangan (tahun dasar 2015 = 100)."
    },
    "Import value index (2015 = 100)": {
        "code": "TM.VAL.MRCH.XD.WD", "kategori": "2. Pertumbuhan & Struktur", "unit": "Index",
        "desc": "Indeks nilai impor barang dagangan (tahun dasar 2015 = 100)."
    },
    "High-technology exports (% of manufactured exports)": {
        "code": "TX.VAL.TECH.MF.ZS", "kategori": "2. Pertumbuhan & Struktur", "unit": "%",
        "desc": "Persentase ekspor produk berteknologi tinggi terhadap total ekspor manufaktur."
    },
    "ICT goods exports (% of total goods exports)": {
        "code": "TX.VAL.ICTG.ZS.UN", "kategori": "2. Pertumbuhan & Struktur", "unit": "%",
        "desc": "Pangsa ekspor produk TIK (Information and Communication Technology) terhadap total ekspor barang."
    },

    # --- 3. Tariffs & Market Access (WITS Standards) ---
    "Tariff rate, applied, simple mean, all products (%)": {
        "code": "TM.TAX.MRCH.SM.AR.ZS", "kategori": "3. Tarif & Hambatan Perdagangan", "unit": "%",
        "desc": "Rata-rata sederhana (simple mean) tarif bea masuk yang diterapkan pada semua lini produk."
    },
    "Tariff rate, applied, weighted mean, all products (%)": {
        "code": "TM.TAX.MRCH.WM.AR.ZS", "kategori": "3. Tarif & Hambatan Perdagangan", "unit": "%",
        "desc": "Rata-rata terbobot tarif bea masuk yang memperhitungkan pangsa nilai perdagangan aktual."
    },
    "Tariff rate, applied, simple mean, manufactured products (%)": {
        "code": "TM.TAX.MANF.SM.AR.ZS", "kategori": "3. Tarif & Hambatan Perdagangan", "unit": "%",
        "desc": "Rata-rata tarif bea masuk yang diterapkan khusus untuk produk-produk manufaktur."
    },
    "Tariff rate, applied, simple mean, primary products (%)": {
        "code": "TM.TAX.PRIM.SM.AR.ZS", "kategori": "3. Tarif & Hambatan Perdagangan", "unit": "%",
        "desc": "Rata-rata tarif bea masuk yang diterapkan khusus untuk produk primer/pertanian."
    },

    # --- 4. Services Trade ---
    "Service exports (BoP, current US$)": {
        "code": "BX.GSR.NFSV.CD", "kategori": "4. Perdagangan Jasa", "unit": "USD",
        "desc": "Total ekspor jasa komersial dan transportasi dalam USD (Neraca Pembayaran)."
    },
    "Service imports (BoP, current US$)": {
        "code": "BM.GSR.NFSV.CD", "kategori": "4. Perdagangan Jasa", "unit": "USD",
        "desc": "Total impor jasa komersial dalam USD."
    },
    "Transport services (% of service exports, BoP)": {
        "code": "BX.TRN.SRVS.CD", "kategori": "4. Perdagangan Jasa", "unit": "USD",
        "desc": "Nilai ekspor layanan transportasi internasional."
    }
}

# =============================================================================
# 1. KONTROL PEMILIHAN INDIKATOR
# =============================================================================
st.subheader("1. Pemilihan Indikator Perdagangan WITS")
col_kat, col_ind = st.columns([1.2, 2])

kategori_list = sorted(list(set(v["kategori"] for v in WITS_TRADE_CATALOG.values())))
with col_kat:
    kat_pilihan = st.selectbox("Kategori Perdagangan:", ["Semua Kategori"] + kategori_list)

opsi = [
    k for k, v in WITS_TRADE_CATALOG.items()
    if kat_pilihan == "Semua Kategori" or v["kategori"] == kat_pilihan
]

with col_ind:
    nama_indikator = st.selectbox(f"Pilih Indikator ({len(opsi)} Tersedia):", opsi)

meta = WITS_TRADE_CATALOG[nama_indikator]
code_id = meta["code"]

with st.expander("ℹ️ Definisi & Metadata Resmi WITS", expanded=False):
    st.markdown(f"**Indikator Perdagangan:** {nama_indikator}")
    st.markdown(f"**Kode Seri WDI/WITS:** `{code_id}`")
    st.markdown(f"**Satuan Pengukuran:** `{meta['unit']}`")
    st.markdown(f"**Cakupan Geografis:** Indonesia (IDN)")
    st.markdown(f"**Deskripsi Metodologi:**\n{meta['desc']}")
    st.markdown("🔗 **Portal Sumber Resmi:** [World Bank WITS Gateway](https://wits.worldbank.org/)")

# =============================================================================
# 2. PENARIKAN DATA LIVE API WITS/WORLD BANK
# =============================================================================
st.subheader("2. Penarikan Data Runtun Waktu Nasional (Indonesia)")
st.caption("Menarik riwayat tahunan secara real-time langsung dari server World Bank/WITS.")

def fetch_wits_data(indicator_code: str) -> list:
    api_url = f"https://api.worldbank.org/v2/country/IDN/indicator/{indicator_code}?format=json&per_page=1000"
    try:
        res = requests.get(api_url, headers=HEADERS, timeout=25)
        if res.status_code != 200:
            return []
        payload = res.json()
        if len(payload) > 1 and isinstance(payload[1], list):
            records = []
            for item in payload[1]:
                thn = item.get("date")
                val = item.get("value")
                if thn is not None and val is not None:
                    try:
                        records.append({"Tahun": int(thn), "nilai_raw": round(float(val), 4)})
                    except (ValueError, TypeError):
                        continue
            return records
    except Exception:
        pass
    return []

if st.button("📊 Ambil Data Perdagangan Indonesia", type="primary"):
    with st.spinner(f"Menarik data untuk '{nama_indikator}'..."):
        try:
            records = fetch_wits_data(code_id)

            if not records:
                st.warning(
                    "Server merespons namun data untuk Indonesia belum tersedia "
                    "pada indikator ini. Silakan pilih indikator perdagangan lain."
                )
                st.stop()

            val_col = f"Nilai ({meta['unit']})"
            df_wits = (
                pd.DataFrame(records)
                .groupby("Tahun", as_index=False)["nilai_raw"]
                .mean()
                .round(2)
                .rename(columns={"nilai_raw": val_col})
                .sort_values(by="Tahun", ascending=True)
            )

            st.success(f"Berhasil menarik **{len(df_wits)}** observasi tahunan perdagangan Indonesia!")
            st.divider()

            # Tombol Unduh
            c1, c2 = st.columns(2)
            c1.download_button(
                "📥 Unduh CSV",
                df_wits.to_csv(index=False).encode("utf-8"),
                f"WITS_Trade_Indonesia_{code_id}.csv",
                "text/csv"
            )
            buf = io.BytesIO()
            with pd.ExcelWriter(buf, engine="openpyxl") as writer:
                df_wits.to_excel(writer, index=False, sheet_name="WITS Trade Data")
            c2.download_button(
                "📊 Unduh Excel (.xlsx)",
                buf.getvalue(),
                f"WITS_Trade_Indonesia_{code_id}.xlsx",
                "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )

            # Visualisasi Plotly
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=df_wits["Tahun"],
                y=df_wits[val_col],
                mode="lines+markers",
                name="Indonesia (WITS Trade)",
                line=dict(width=2.8, color="#2b5c8f"),
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
                st.dataframe(df_wits.sort_values(by="Tahun", ascending=False), use_container_width=True)

        except Exception as e:
            st.error(f"Terjadi kesalahan saat memproses data WITS: {e}")

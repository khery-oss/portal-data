import io
import pandas as pd
import plotly.graph_objects as go
import requests
import streamlit as st

st.set_page_config(page_title="WHO Explorer - IndoEcon", layout="wide")

st.title("🏥 WHO (World Health Organization) - Modal Manusia & Kesehatan")
st.markdown(
    "Eksplorasi indikator kesehatan publik dan modal manusia (*human capital*) Indonesia resmi dari "
    "**WHO Global Health Observatory (GHO) REST API** secara *real-time* (*100% Live API Streaming*)."
)

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

# KATALOG INDIKATOR KESEHATAN & MODAL MANUSIA RESMI WHO (IDN)
WHO_CATALOG = {
    # --- 1. Usia Harapan Hidup & Mortalitas ---
    "Angka Harapan Hidup saat Lahir (Life Expectancy, Tahun)": {
        "code": "WHOSIS_000001",
        "kategori": "1. Harapan Hidup & Mortalitas",
        "unit": "Tahun",
        "desc": "Rata-rata perkiraan jumlah tahun hidup yang dapat dicapai bayi yang baru lahir di Indonesia."
    },
    "Angka Harapan Hidup Sehat (HALE at Birth, Tahun)": {
        "code": "WHOSIS_000002",
        "kategori": "1. Harapan Hidup & Mortalitas",
        "unit": "Tahun",
        "desc": "Jumlah tahun rata-rata seseorang diperkirakan dapat hidup dalam kondisi kesehatan prima tanpa disabilitas berat."
    },
    "Angka Kematian Balita (Under-five Mortality Rate per 1.000 Kelahiran)": {
        "code": "MDG_0000000007",
        "kategori": "1. Harapan Hidup & Mortalitas",
        "unit": "Per 1.000 Kelahiran",
        "desc": "Probabilitas anak meninggal sebelum mencapai usia tepat lima tahun per 1.000 kelahiran hidup."
    },

    # --- 2. Gizi, Nutrisi & Perkembangan Anak ---
    "Prevalensi Stunting pada Balita (Stunting Prevalence, %)": {
        "code": "NUTRITION_STUNTING_PREV",
        "kategori": "2. Nutrisi & Gizi Anak",
        "unit": "%",
        "desc": "Persentase anak balita dengan tinggi badan menurut umur di bawah minus 2 standar deviasi standar pertumbuhan anak WHO."
    },
    "Prevalensi Wasting / Gizi Buruk Akut (%)": {
        "code": "NUTRITION_WASTING_PREV",
        "kategori": "2. Nutrisi & Gizi Anak",
        "unit": "%",
        "desc": "Proporsi balita dengan berat badan menurut tinggi badan di bawah minus 2 standar deviasi (kurus akut)."
    },

    # --- 3. Fasilitas & Sistem Pembiayaan Kesehatan ---
    "Kepadatan Tenaga Medis / Dokter (per 10.000 Penduduk)": {
        "code": "HWF_0001",
        "kategori": "3. Sistem Kesehatan & Akses",
        "unit": "Per 10.000 Penduduk",
        "desc": "Rasio ketersediaan dokter medis per sepuluh ribu populasi penduduk."
    },
    "Kepadatan Tenaga Keperawatan & Kebidanan (per 10.000 Penduduk)": {
        "code": "HWF_0002",
        "kategori": "3. Sistem Kesehatan & Akses",
        "unit": "Per 10.000 Penduduk",
        "desc": "Rasio perawat dan bidan resmi per sepuluh ribu populasi penduduk."
    },
    "Cakupan Layanan Kesehatan Semesta (UHC Service Coverage Index)": {
        "code": "UHC_INDEX_REPORTED",
        "kategori": "3. Sistem Kesehatan & Akses",
        "unit": "Indeks (0-100)",
        "desc": "Indeks komposit cakupan layanan esensial (kesehatan reproduksi, penyakit menular, dan kapasitas layanan)."
    }
}

# =============================================================================
# 1. PEMILIHAN INDIKATOR
# =============================================================================
st.subheader("1. Pemilihan Indikator WHO")
c_kat, c_ind = st.columns([1.2, 2])

kategori_list = sorted(list(set(v["kategori"] for v in WHO_CATALOG.values())))
with c_kat:
    kat_pilihan = st.selectbox("Kategori Bidang:", ["Semua Kategori"] + kategori_list)

opsi = [
    k for k, v in WHO_CATALOG.items()
    if kat_pilihan == "Semua Kategori" or v["kategori"] == kat_pilihan
]

with c_ind:
    nama_indikator = st.selectbox(f"Pilih Indikator ({len(opsi)} Tersedia):", opsi)

meta = WHO_CATALOG[nama_indikator]
code_id = meta["code"]

with st.expander("ℹ️ Definisi & Metadata Resmi WHO", expanded=False):
    st.markdown(f"**Indikator:** {nama_indikator}")
    st.markdown(f"**Kode Indikator WHO:** `{code_id}`")
    st.markdown(f"**Satuan Pengukuran:** `{meta['unit']}`")
    st.markdown(f"**Metodologi / Deskripsi:**\n{meta['desc']}")
    st.markdown("🔗 **Portal Sumber Resmi:** [WHO Global Health Observatory](https://www.who.int/data/gho)")

# =============================================================================
# 2. PENARIKAN DATA RUN TUN WAKTU LENGKAP
# =============================================================================
st.subheader("2. Penarikan Data Runtun Waktu Nasional")
st.caption("Data akan ditarik secara lengkap untuk seluruh riwayat tahun yang tercatat di server resmi WHO.")

if st.button("📊 Ambil Data WHO (Live API)", type="primary"):
    with st.spinner(f"Menghubungi server WHO GHO API untuk seri {nama_indikator}..."):
        # Endpoint OData resmi WHO untuk data Indonesia (SpatialDim eq 'IDN')
        api_url = f"https://ghoapi.azureedge.net/api/{code_id}?$filter=SpatialDim eq 'IDN'"

        try:
            res = requests.get(api_url, headers=HEADERS, timeout=25)
            if res.status_code == 200:
                payload = res.json()
                items = payload.get("value", [])

                records = []
                for it in items:
                    th = it.get("TimeDim")
                    val = it.get("NumericValue")
                    
                    # Ambil data agregat total (BTSX: Both sexes) jika tersedia pemilahan gender
                    dim1 = it.get("Dim1")
                    if dim1 and dim1 not in ["BTSX", "TOTAL"]:
                        continue

                    if th is not None and val is not None:
                        try:
                            records.append({
                                "Tahun": int(th),
                                "Nilai": round(float(val), 2)
                            })
                        except (ValueError, TypeError):
                            continue

                # Fallback: jika pemilahan BTSX tidak ditemukan, gunakan agregat rata-rata per tahun
                if not records and items:
                    for it in items:
                        th = it.get("TimeDim")
                        val = it.get("NumericValue")
                        if th is not None and val is not None:
                            try:
                                records.append({"Tahun": int(th), "Nilai": float(val)})
                            except (ValueError, TypeError):
                                continue

                if records:
                    val_col = f"Nilai ({meta['unit']})"
                    df_raw = pd.DataFrame(records)
                    df_who = df_raw.groupby("Tahun", as_index=False)["Nilai"].mean().round(2)
                    df_who = df_who.rename(columns={"Nilai": val_col}).sort_values(by="Tahun", ascending=True)

                    st.success(f"Berhasil menarik {len(df_who)} observasi runtun waktu resmi langsung dari server WHO!")
                    st.divider()

                    # Tombol Unduh Data
                    c1, c2 = st.columns(2)
                    c1.download_button(
                        "📥 Unduh CSV",
                        df_who.to_csv(index=False).encode("utf-8"),
                        f"WHO_Indonesia_{code_id}.csv",
                        "text/csv"
                    )
                    buf = io.BytesIO()
                    with pd.ExcelWriter(buf, engine="openpyxl") as writer:
                        df_who.to_excel(writer, index=False, sheet_name="WHO Data")
                    c2.download_button(
                        "📊 Unduh Excel (.xlsx)",
                        buf.getvalue(),
                        f"WHO_Indonesia_{code_id}.xlsx",
                        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                    )

                    # Visualisasi Plotly Interaktif
                    fig = go.Figure()
                    fig.add_trace(go.Scatter(
                        x=df_who["Tahun"],
                        y=df_who[val_col],
                        mode="lines+markers",
                        name="Indonesia (WHO Data)",
                        line=dict(width=2.8, color="#0093D5"),
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
                        st.dataframe(df_who.sort_values(by="Tahun", ascending=False), use_container_width=True)
                else:
                    st.warning("Server WHO merespons, namun seri observasi data untuk Indonesia belum tersedia.")
            else:
                st.error(f"Gagal menghubungi server WHO (Kode Status HTTP: {res.status_code}).")
        except Exception as e:
            st.error(f"Terjadi kesalahan saat memproses data WHO: {e}")

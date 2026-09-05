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

# KATALOG 20 INDIKATOR STRATEGIS INDONESIA DARI WHO GHO
WHO_CATALOG = {
    # --- 1. Usia Harapan Hidup & Kematian Umum ---
    "Angka Harapan Hidup saat Lahir (Life Expectancy, Tahun)": {
        "code": "WHOSIS_000001", "kategori": "1. Harapan Hidup & Kematian", "unit": "Tahun",
        "desc": "Rata-rata perkiraan jumlah tahun hidup yang dapat dicapai bayi yang baru lahir di Indonesia."
    },
    "Angka Harapan Hidup Sehat (HALE at Birth, Tahun)": {
        "code": "WHOSIS_000002", "kategori": "1. Harapan Hidup & Kematian", "unit": "Tahun",
        "desc": "Perkiraan rata-rata tahun hidup dalam kondisi sehat tanpa keterbatasan akibat sakit parah."
    },
    "Angka Harapan Hidup pada Usia 60 Tahun (Life Expectancy at Age 60)": {
        "code": "WHOSIS_000015", "kategori": "1. Harapan Hidup & Kematian", "unit": "Tahun",
        "desc": "Rata-rata sisa tahun hidup yang diharapkan bagi penduduk yang telah mencapai usia 60 tahun."
    },
    "Probabilitas Kematian Dini Akibat PTM / NCD Usia 30-70 (%)": {
        "code": "NCDMORT3070", "kategori": "1. Harapan Hidup & Kematian", "unit": "%",
        "desc": "Peluang meninggal akibat penyakit kardiovaskular, kanker, diabetes, atau respirasi kronis antara usia 30-70."
    },

    # --- 2. Kesehatan Ibu, Bayi & Anak ---
    "Angka Kematian Balita (Under-five Mortality Rate per 1.000 Kelahiran)": {
        "code": "MDG_0000000007", "kategori": "2. Ibu, Bayi & Anak", "unit": "Per 1.000 Kelahiran",
        "desc": "Probabilitas anak meninggal sebelum genap usia lima tahun per seribu kelahiran hidup."
    },
    "Angka Kematian Bayi / IMR (per 1.000 Kelahiran)": {
        "code": "MDG_0000000001", "kategori": "2. Ibu, Bayi & Anak", "unit": "Per 1.000 Kelahiran",
        "desc": "Probabilitas bayi meninggal sebelum genap usia satu tahun per seribu kelahiran hidup."
    },
    "Angka Kematian Neonatal (per 1.000 Kelahiran)": {
        "code": "WHOSIS_000003", "kategori": "2. Ibu, Bayi & Anak", "unit": "Per 1.000 Kelahiran",
        "desc": "Kematian bayi dalam 28 hari pertama kehidupan per seribu kelahiran hidup."
    },
    "Rasio Kematian Ibu / MMR (per 100.000 Kelahiran Hidup)": {
        "code": "MDG_0000000026", "kategori": "2. Ibu, Bayi & Anak", "unit": "Per 100.000 Kelahiran",
        "desc": "Kematian perempuan terkait kehamilan atau persalinan per seratus ribu kelahiran hidup."
    },
    "Persalinan Ditolong Tenaga Kesehatan Terlatih (%)": {
        "code": "MDG_0000000025", "kategori": "2. Ibu, Bayi & Anak", "unit": "% Kelahiran",
        "desc": "Persentase persalinan yang dibantu oleh dokter, bidan, atau perawat berkualifikasi."
    },

    # --- 3. Imunisasi & Penyakit Menular ---
    "Cakupan Imunisasi Campak Balita (MCV1, %)": {
        "code": "WHS3_62", "kategori": "3. Imunisasi & Penyakit Menular", "unit": "%",
        "desc": "Persentase anak usia satu tahun yang menerima dosis pertama vaksin campak."
    },
    "Cakupan Imunisasi Polio (Pol3, %)": {
        "code": "WHS3_49", "kategori": "3. Imunisasi & Penyakit Menular", "unit": "%",
        "desc": "Persentase bayi yang telah menerima 3 dosis vaksin polio."
    },
    "Cakupan Imunisasi DTP3 (%)": {
        "code": "WHS3_40", "kategori": "3. Imunisasi & Penyakit Menular", "unit": "%",
        "desc": "Persentase bayi yang mendapatkan vaksin difteri, tetanus, dan pertusis lengkap."
    },
    "Insidensi Tuberkulosis / TB (per 100.000 Penduduk)": {
        "code": "MDG_0000000020", "kategori": "3. Imunisasi & Penyakit Menular", "unit": "Per 100.000 Penduduk",
        "desc": "Perkiraan jumlah kasus baru dan kambuh TB per seratus ribu penduduk dalam satu tahun."
    },
    "Prevalensi Tuberkulosis (per 100.000 Penduduk)": {
        "code": "MDG_0000000018", "kategori": "3. Imunisasi & Penyakit Menular", "unit": "Per 100.000 Penduduk",
        "desc": "Jumlah total penderita TB pada waktu tertentu per seratus ribu penduduk."
    },

    # --- 4. Tenaga Medis & Infrastruktur Kesehatan ---
    "Kepadatan Tenaga Medis / Dokter (per 10.000 Penduduk)": {
        "code": "HWF_0001", "kategori": "4. Tenaga Medis & Kapasitas", "unit": "Per 10.000 Penduduk",
        "desc": "Jumlah ketersediaan dokter umum dan spesialis per sepuluh ribu penduduk."
    },
    "Kepadatan Perawat & Bidan (per 10.000 Penduduk)": {
        "code": "HWF_0002", "kategori": "4. Tenaga Medis & Kapasitas", "unit": "Per 10.000 Penduduk",
        "desc": "Jumlah perawat dan bidan resmi yang bertugas per sepuluh ribu penduduk."
    },
    "Kepadatan Apoteker / Farmasis (per 10.000 Penduduk)": {
        "code": "HWF_0003", "kategori": "4. Tenaga Medis & Kapasitas", "unit": "Per 10.000 Penduduk",
        "desc": "Jumlah tenaga kefarmasian resmi per sepuluh ribu penduduk."
    },

    # --- 5. Akses Sanitasi & Jaminan Kesehatan ---
    "Cakupan Layanan Kesehatan Semesta (UHC Coverage Index)": {
        "code": "UHC_INDEX_REPORTED", "kategori": "5. Sanitasi & Jaminan Kesehatan", "unit": "Indeks (0-100)",
        "desc": "Indeks cakupan layanan esensial yang mencakup kesehatan reproduksi, penyakit menular, dan kapasitas rumah sakit."
    },
    "Populasi dengan Akses Air Minum Layak (%)": {
        "code": "WSH_WATER_BASIC", "kategori": "5. Sanitasi & Jaminan Kesehatan", "unit": "% Populasi",
        "desc": "Persentase penduduk yang menggunakan sumber air minum terlindungi."
    },
    "Populasi dengan Akses Sanitasi Dasar Layak (%)": {
        "code": "WSH_SANITATION_BASIC", "kategori": "5. Sanitasi & Jaminan Kesehatan", "unit": "% Populasi",
        "desc": "Persentase penduduk dengan akses fasilitas jamban dan sanitasi higienis."
    }
}

# =============================================================================
# 1. KONTROL PILIHAN INDIKATOR
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
    st.markdown(f"**Cakupan Negara:** Indonesia (IDN)")
    st.markdown(f"**Metodologi / Deskripsi:**\n{meta['desc']}")
    st.markdown("🔗 **Basis Data:** [WHO Global Health Observatory](https://www.who.int/data/gho)")

# =============================================================================
# 2. PENARIKAN DATA LIVE API WHO (INDONESIA)
# =============================================================================
st.subheader("2. Penarikan Data Runtun Waktu Nasional (Indonesia)")
st.caption("Seluruh riwayat tahun yang tercatat di basis data resmi WHO akan diambil secara otomatis.")

if st.button("📊 Ambil Data WHO (Live API)", type="primary"):
    with st.spinner(f"Menghubungi server WHO GHO API untuk seri {nama_indikator}..."):
        api_url = f"https://ghoapi.azureedge.net/api/{code_id}"
        query_params = {"$filter": "SpatialDim eq 'IDN'"}

        try:
            res = requests.get(api_url, params=query_params, headers=HEADERS, timeout=25)
            
            if res.status_code == 200:
                payload = res.json()
                items = payload.get("value", [])

                records = []
                for it in items:
                    th = it.get("TimeDim")
                    val = it.get("NumericValue")
                    
                    dim1 = it.get("Dim1")
                    if dim1 and dim1 not in ["BTSX", "TOTAL", "SEX_BTSX"]:
                        continue

                    if th is not None and val is not None:
                        try:
                            records.append({
                                "Tahun": int(th),
                                "Nilai": round(float(val), 2)
                            })
                        except (ValueError, TypeError):
                            continue

                if not records and items:
                    for it in items:
                        th = it.get("TimeDim")
                        val = it.get("NumericValue")
                        if th is not None and val is not None:
                            try:
                                records.append({"Tahun": int(th), "Nilai": round(float(val), 2)})
                            except (ValueError, TypeError):
                                continue

                if records:
                    val_col = f"Nilai ({meta['unit']})"
                    df_raw = pd.DataFrame(records)
                    df_who = df_raw.groupby("Tahun", as_index=False)["Nilai"].mean().round(2)
                    df_who = df_who.rename(columns={"Nilai": val_col}).sort_values(by="Tahun", ascending=True)

                    st.success(f"Berhasil menarik {len(df_who)} observasi tahunan resmi untuk Indonesia dari server WHO!")
                    st.divider()

                    # Tombol Unduh
                    c1, c2 = st.columns(2)
                    c1.download_button(
                        "📥 Unduh CSV",
                        df_who.to_csv(index=False).encode("utf-8"),
                        f"WHO_Indonesia_{code_id}.csv",
                        "text/csv"
                    )
                    buf = io.BytesIO()
                    with pd.ExcelWriter(buf, engine="openpyxl") as writer:
                        df_who.to_excel(writer, index=False, sheet_name="WHO Indonesia")
                    c2.download_button(
                        "📊 Unduh Excel (.xlsx)",
                        buf.getvalue(),
                        f"WHO_Indonesia_{code_id}.xlsx",
                        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                    )

                    # Visualisasi Plotly
                    fig = go.Figure()
                    fig.add_trace(go.Scatter(
                        x=df_who["Tahun"],
                        y=df_who[val_col],
                        mode="lines+markers",
                        name="Indonesia (WHO GHO)",
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
                    st.warning("Server WHO merespons, namun catatan observasi untuk Indonesia belum dipublikasikan pada kode ini.")
            else:
                st.error(f"Gagal menghubungi server WHO (Kode Status HTTP: {res.status_code}).")
        except Exception as e:
            st.error(f"Terjadi kesalahan saat memproses data WHO: {e}")

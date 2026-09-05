import io
import pandas as pd
import plotly.graph_objects as go
import requests
import streamlit as st

st.set_page_config(page_title="ILO Labour Market Explorer - Indonesia", layout="wide")

st.title("👷 ILO (International Labour Organization) - Pasar Tenaga Kerja Indonesia")
st.write(
    "Eksplorasi indikator resmi pasar tenaga kerja, pengangguran, upah, dan partisipasi gender dari "
    "**International Labour Organization (ILOSTAT Modelled Estimates)** khusus untuk **Indonesia** "
    "secara langsung (*100% real-time live API*)."
)

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

# KATALOG RESMI INDIKATOR KETENAGAKERJAAN ILO (ILOSTAT SERIES) UNTUK INDONESIA
ILO_CATALOG = {
    # =========================================================================
    # 1. Angkatan Kerja & Partisipasi (Labor Force Participation)
    # =========================================================================
    "Labor Force Participation Rate, Total (% of Population Ages 15+)": {
        "code": "SL.TLF.CACT.ZS",
        "kategori": "1. Partisipasi Angkatan Kerja (TPAK)",
        "unit": "%",
        "desc": "Tingkat partisipasi angkatan kerja (TPAK) total penduduk usia 15 tahun ke atas berdasarkan estimasi resmi ILO."
    },
    "Labor Force Participation Rate, Female (% of Female Ages 15+)": {
        "code": "SL.TLF.CACT.FE.ZS",
        "kategori": "1. Partisipasi Angkatan Kerja (TPAK)",
        "unit": "%",
        "desc": "Tingkat partisipasi angkatan kerja khusus perempuan usia 15 tahun ke atas."
    },
    "Labor Force Participation Rate, Male (% of Male Ages 15+)": {
        "code": "SL.TLF.CACT.MA.ZS",
        "kategori": "1. Partisipasi Angkatan Kerja (TPAK)",
        "unit": "%",
        "desc": "Tingkat partisipasi angkatan kerja khusus laki-laki usia 15 tahun ke atas."
    },
    "Ratio of Female to Male Labor Force Participation Rate (%)": {
        "code": "SL.TLF.CACT.FM.ZS",
        "kategori": "1. Partisipasi Angkatan Kerja (TPAK)",
        "unit": "%",
        "desc": "Rasio partisipasi perempuan terhadap laki-laki di pasar tenaga kerja (indikator kesetaraan gender)."
    },

    # =========================================================================
    # 2. Pengangguran & Underemployment
    # =========================================================================
    "Total Unemployment Rate (% of Total Labor Force)": {
        "code": "SL.UEM.TOTL.ZS",
        "kategori": "2. Pengangguran",
        "unit": "%",
        "desc": "Tingkat pengangguran terbuka nasional resmi berdasarkan metodologi harmonisasi standar ILO."
    },
    "Youth Unemployment Rate (% of Labor Force Ages 15-24)": {
        "code": "SL.UEM.1524.ZS",
        "kategori": "2. Pengangguran",
        "unit": "%",
        "desc": "Tingkat pengangguran angkatan kerja generasi muda (rentang usia 15–24 tahun)."
    },
    "Female Unemployment Rate (% of Female Labor Force)": {
        "code": "SL.UEM.TOTL.FE.ZS",
        "kategori": "2. Pengangguran",
        "unit": "%",
        "desc": "Tingkat pengangguran angkatan kerja perempuan."
    },
    "Male Unemployment Rate (% of Male Labor Force)": {
        "code": "SL.UEM.TOTL.MA.ZS",
        "kategori": "2. Pengangguran",
        "unit": "%",
        "desc": "Tingkat pengangguran angkatan kerja laki-laki."
    },

    # =========================================================================
    # 3. Kualitas Pekerjaan & Kerentanan (Job Quality & Informality)
    # =========================================================================
    "Vulnerable Employment (% of Total Employment)": {
        "code": "SL.EMP.VULN.ZS",
        "kategori": "3. Kualitas Pekerjaan & Kerentanan",
        "unit": "%",
        "desc": "Proporsi pekerja rentan (pekerja keluarga tanpa upah dan pekerja mandiri) terhadap total pekerja yang bekerja."
    },
    "Wage and Salaried Workers / Formal Employees (% of Total Employment)": {
        "code": "SL.EMP.WORK.ZS",
        "kategori": "3. Kualitas Pekerjaan & Kerentanan",
        "unit": "%",
        "desc": "Persentase pekerja penerima upah/gaji tetap (indikasi formalisasi pekerjaan) dari total tenaga kerja."
    },

    # =========================================================================
    # 4. Transformasi Struktural Sektoral (Employment by Sector)
    # =========================================================================
    "Employment in Services Sector (% of Total Employment)": {
        "code": "SL.SRV.EMPL.ZS",
        "kategori": "4. Distribusi Sektoral Tenaga Kerja",
        "unit": "%",
        "desc": "Pangsa penyerapan tenaga kerja di sektor jasa dan perdagangan modern."
    },
    "Employment in Industry / Manufacturing (% of Total Employment)": {
        "code": "SL.IND.EMPL.ZS",
        "kategori": "4. Distribusi Sektoral Tenaga Kerja",
        "unit": "%",
        "desc": "Pangsa penyerapan tenaga kerja di sektor industri pengolahan dan konstruksi."
    },
    "Employment in Agriculture (% of Total Employment)": {
        "code": "SL.AGR.EMPL.ZS",
        "kategori": "4. Distribusi Sektoral Tenaga Kerja",
        "unit": "%",
        "desc": "Pangsa penyerapan tenaga kerja di sektor primer pertanian, kehutanan, dan perikanan."
    }
}

# =============================================================================
# 1. KONTROL PEMILIHAN INDIKATOR
# =============================================================================
st.subheader("1. Pemilihan Indikator Resmi ILO")
col_kat, col_ind = st.columns([1.2, 2])

kategori_list = sorted(list(set(v["kategori"] for v in ILO_CATALOG.values())))
with col_kat:
    pilihan_kategori = st.selectbox("Kategori Bidang:", ["Semua Kategori"] + kategori_list)

opsi = [
    k for k, v in ILO_CATALOG.items()
    if pilihan_kategori == "Semua Kategori" or v["kategori"] == pilihan_kategori
]

with col_ind:
    selected_name = st.selectbox(f"Nama Indikator Tenaga Kerja ({len(opsi)} Tersedia):", opsi)

meta = ILO_CATALOG[selected_name]
kode_indikator = meta["code"]

with st.expander("ℹ️ Definisi & Metadata Resmi ILO", expanded=False):
    st.markdown(f"**Nama Indikator:** {selected_name}")
    st.markdown(f"**Kode Seri:** `{kode_indikator}`")
    st.markdown(f"**Kategori:** `{meta['kategori']}`")
    st.markdown(f"**Satuan:** `{meta['unit']}`")
    st.markdown(f"**Metodologi / Deskripsi:**\n{meta['desc']}")
    st.markdown("🔗 **Basis Data:** [ILOSTAT - International Labour Organization](https://ilostat.ilo.org/)")

# =============================================================================
# 2. PENARIKAN DATA LIVE VIA RESTFUL JSON API
# =============================================================================
st.subheader("2. Penarikan Data Runtun Waktu")

if st.button("📊 Ambil Data Ketenagakerjaan Indonesia", type="primary"):
    with st.spinner(f"Menghubungi endpoint resmi untuk seri {kode_indikator}..."):
        api_url = f"https://api.worldbank.org/v2/country/IDN/indicator/{kode_indikator}?format=json&per_page=1000"
        
        try:
            res = requests.get(api_url, headers=HEADERS, timeout=20)
            records = []
            
            if res.status_code == 200:
                payload = res.json()
                if len(payload) > 1 and isinstance(payload[1], list):
                    for item in payload[1]:
                        thn = item.get("date")
                        val = item.get("value")
                        if thn is not None and val is not None:
                            try:
                                records.append({
                                    "Tahun": int(thn),
                                    f"Nilai ({meta['unit']})": round(float(val), 2)
                                })
                            except (ValueError, TypeError):
                                continue

            if records:
                val_col = f"Nilai ({meta['unit']})"
                df_ilo = pd.DataFrame(records).sort_values(by="Tahun", ascending=True)

                st.success(f"Berhasil menarik {len(df_ilo)} observasi tahunan resmi dari basis data ILO!")
                st.divider()

                # Tombol Unduh Data
                c1, c2 = st.columns(2)
                c1.download_button(
                    "📥 Unduh CSV",
                    df_ilo.to_csv(index=False).encode("utf-8"),
                    f"ILO_IDN_{kode_indikator}.csv",
                    "text/csv"
                )
                buf = io.BytesIO()
                with pd.ExcelWriter(buf, engine="openpyxl") as writer:
                    df_ilo.to_excel(writer, index=False, sheet_name="ILO Data")
                c2.download_button(
                    "📊 Unduh Excel (.xlsx)",
                    buf.getvalue(),
                    f"ILO_IDN_{kode_indikator}.xlsx",
                    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )

                # Visualisasi Plotly Interaktif
                fig = go.Figure()
                fig.add_trace(go.Scatter(
                    x=df_ilo["Tahun"],
                    y=df_ilo[val_col],
                    mode="lines+markers",
                    name="Indonesia (ILO)",
                    line=dict(width=2.5, color="#D9534F"),
                    hovertemplate=f"Tahun %{{x}}<br>Nilai: %{{y:.2f}} {meta['unit']}<extra></extra>"
                ))
                fig.update_layout(
                    xaxis=dict(title="Tahun", tickmode="linear"),
                    yaxis=dict(title=meta["unit"]),
                    hovermode="x unified",
                    margin=dict(l=20, r=20, t=40, b=20)
                )
                st.plotly_chart(fig, use_container_width=True)

                with st.expander("📋 Tabel Data Runtun Waktu Lengkap"):
                    st.dataframe(df_ilo.sort_values(by="Tahun", ascending=False), use_container_width=True)
            else:
                st.warning("Observasi runtun waktu untuk indikator ini belum dilaporkan atau sedang dalam pembaruan.")
        except Exception as e:
            st.error(f"Gagal menghubungi server data ketenagakerjaan: {e}")

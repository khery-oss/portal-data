import io
import pandas as pd
import plotly.graph_objects as go
import requests
import streamlit as st

st.set_page_config(page_title="ILO Labour Market Explorer - Indonesia", layout="wide")

st.title("👷 ILO (International Labour Organization) - Pasar Tenaga Kerja Indonesia")
st.write(
    "Eksplorasi indikator pasar tenaga kerja, pengangguran, struktur upah, dan demografi kerja dari "
    "**International Labour Organization (ILOSTAT Modelled Estimates)** khusus untuk **Indonesia** "
    "secara langsung (*100% real-time live API*)."
)

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

# KATALOG LENGKAP RESMI INDIKATOR KETENAGAKERJAAN ILO UNTUK INDONESIA (40 INDIKATOR)
ILO_CATALOG = {
    # =========================================================================
    # 1. Partisipasi Angkatan Kerja (TPAK) & Angkatan Kerja
    # =========================================================================
    "Labor Force Participation Rate, Total (% of Population Ages 15+)": {
        "code": "SL.TLF.CACT.ZS", "kategori": "1. Partisipasi Angkatan Kerja (TPAK)", "unit": "%",
        "desc": "Tingkat partisipasi angkatan kerja (TPAK) total penduduk usia 15 tahun ke atas berdasarkan estimasi standar ILO."
    },
    "Labor Force Participation Rate, Female (% of Female Ages 15+)": {
        "code": "SL.TLF.CACT.FE.ZS", "kategori": "1. Partisipasi Angkatan Kerja (TPAK)", "unit": "%",
        "desc": "Tingkat partisipasi angkatan kerja khusus perempuan usia 15 tahun ke atas."
    },
    "Labor Force Participation Rate, Male (% of Male Ages 15+)": {
        "code": "SL.TLF.CACT.MA.ZS", "kategori": "1. Partisipasi Angkatan Kerja (TPAK)", "unit": "%",
        "desc": "Tingkat partisipasi angkatan kerja khusus laki-laki usia 15 tahun ke atas."
    },
    "Ratio of Female to Male Labor Force Participation Rate (%)": {
        "code": "SL.TLF.CACT.FM.ZS", "kategori": "1. Partisipasi Angkatan Kerja (TPAK)", "unit": "%",
        "desc": "Rasio partisipasi perempuan terhadap laki-laki di pasar tenaga kerja (indikator kesetaraan gender)."
    },
    "Youth Labor Force Participation Rate, Total (% of Ages 15-24)": {
        "code": "SL.TLF.ACTI.ZS", "kategori": "1. Partisipasi Angkatan Kerja (TPAK)", "unit": "%",
        "desc": "Tingkat partisipasi angkatan kerja penduduk usia muda (15–24 tahun)."
    },
    "Youth Labor Force Participation Rate, Female (% of Ages 15-24)": {
        "code": "SL.TLF.ACTI.FE.ZS", "kategori": "1. Partisipasi Angkatan Kerja (TPAK)", "unit": "%",
        "desc": "Tingkat partisipasi angkatan kerja pemuda perempuan (15–24 tahun)."
    },
    "Youth Labor Force Participation Rate, Male (% of Ages 15-24)": {
        "code": "SL.TLF.ACTI.MA.ZS", "kategori": "1. Partisipasi Angkatan Kerja (TPAK)", "unit": "%",
        "desc": "Tingkat partisipasi angkatan kerja pemuda laki-laki (15–24 tahun)."
    },
    "Total Labor Force (Persons)": {
        "code": "SL.TLF.TOTL.IN", "kategori": "1. Partisipasi Angkatan Kerja (TPAK)", "unit": "Jiwa",
        "desc": "Jumlah total angkatan kerja resmi Indonesia (bekerja + menganggur)."
    },
    "Female Labor Force (% of Total Labor Force)": {
        "code": "SL.TLF.TOTL.FE.ZS", "kategori": "1. Partisipasi Angkatan Kerja (TPAK)", "unit": "%",
        "desc": "Proporsi perempuan dalam keseluruhan angkatan kerja nasional."
    },

    # =========================================================================
    # 2. Rasio Penyerapan Kerja (Employment to Population Ratio)
    # =========================================================================
    "Employment to Population Ratio, Total 15+ (%)": {
        "code": "SL.EMP.TOTL.SP.ZS", "kategori": "2. Daya Serap Kerja (Emp-to-Pop)", "unit": "%",
        "desc": "Persentase penduduk usia kerja 15 tahun ke atas yang benar-benar terserap bekerja."
    },
    "Employment to Population Ratio, Female 15+ (%)": {
        "code": "SL.EMP.TOTL.SP.FE.ZS", "kategori": "2. Daya Serap Kerja (Emp-to-Pop)", "unit": "%",
        "desc": "Persentase perempuan usia kerja yang benar-benar terserap bekerja."
    },
    "Employment to Population Ratio, Male 15+ (%)": {
        "code": "SL.EMP.TOTL.SP.MA.ZS", "kategori": "2. Daya Serap Kerja (Emp-to-Pop)", "unit": "%",
        "desc": "Persentase laki-laki usia kerja yang benar-benar terserap bekerja."
    },
    "Youth Employment to Population Ratio, Total 15-24 (%)": {
        "code": "SL.EMP.1524.SP.ZS", "kategori": "2. Daya Serap Kerja (Emp-to-Pop)", "unit": "%",
        "desc": "Persentase penduduk muda (15–24 tahun) yang berstatus bekerja."
    },
    "Youth Employment to Population Ratio, Female 15-24 (%)": {
        "code": "SL.EMP.1524.SP.FE.ZS", "kategori": "2. Daya Serap Kerja (Emp-to-Pop)", "unit": "%",
        "desc": "Persentase perempuan muda yang berstatus bekerja."
    },
    "Youth Employment to Population Ratio, Male 15-24 (%)": {
        "code": "SL.EMP.1524.SP.MA.ZS", "kategori": "2. Daya Serap Kerja (Emp-to-Pop)", "unit": "%",
        "desc": "Persentase laki-laki muda yang berstatus bekerja."
    },

    # =========================================================================
    # 3. Pengangguran Umum, Pemuda, & NEET
    # =========================================================================
    "Total Unemployment Rate (% of Total Labor Force)": {
        "code": "SL.UEM.TOTL.ZS", "kategori": "3. Pengangguran & NEET", "unit": "%",
        "desc": "Tingkat pengangguran terbuka nasional resmi berdasarkan metodologi harmonisasi standar ILO."
    },
    "Female Unemployment Rate (% of Female Labor Force)": {
        "code": "SL.UEM.TOTL.FE.ZS", "kategori": "3. Pengangguran & NEET", "unit": "%",
        "desc": "Tingkat pengangguran angkatan kerja perempuan."
    },
    "Male Unemployment Rate (% of Male Labor Force)": {
        "code": "SL.UEM.TOTL.MA.ZS", "kategori": "3. Pengangguran & NEET", "unit": "%",
        "desc": "Tingkat pengangguran angkatan kerja laki-laki."
    },
    "Youth Unemployment Rate (% of Labor Force Ages 15-24)": {
        "code": "SL.UEM.1524.ZS", "kategori": "3. Pengangguran & NEET", "unit": "%",
        "desc": "Tingkat pengangguran angkatan kerja generasi muda usia 15–24 tahun."
    },
    "Youth Unemployment Rate, Female (% of Female Youth Labor Force)": {
        "code": "SL.UEM.1524.FE.ZS", "kategori": "3. Pengangguran & NEET", "unit": "%",
        "desc": "Tingkat pengangguran angkatan kerja perempuan muda usia 15–24 tahun."
    },
    "Youth Unemployment Rate, Male (% of Male Youth Labor Force)": {
        "code": "SL.UEM.1524.MA.ZS", "kategori": "3. Pengangguran & NEET", "unit": "%",
        "desc": "Tingkat pengangguran angkatan kerja laki-laki muda usia 15–24 tahun."
    },
    "Youth NEET Rate (% of Youth Population Ages 15-24)": {
        "code": "SL.UEM.NEET.ZS", "kategori": "3. Pengangguran & NEET", "unit": "%",
        "desc": "Persentase generasi muda yang tidak bersekolah, bekerja, atau mengikuti pelatihan (Not in Education, Employment, or Training)."
    },
    "Youth NEET Rate, Female (% of Female Youth Population)": {
        "code": "SL.UEM.NEET.FE.ZS", "kategori": "3. Pengangguran & NEET", "unit": "%",
        "desc": "Persentase pemuda perempuan usia 15–24 yang tergolong NEET."
    },
    "Youth NEET Rate, Male (% of Male Youth Population)": {
        "code": "SL.UEM.NEET.MA.ZS", "kategori": "3. Pengangguran & NEET", "unit": "%",
        "desc": "Persentase pemuda laki-laki usia 15–24 yang tergolong NEET."
    },

    # =========================================================================
    # 4. Pengangguran Menurut Tingkat Pendidikan
    # =========================================================================
    "Unemployment with Advanced Education (% of Total Labor Force with Advanced Education)": {
        "code": "SL.UEM.ADVN.ZS", "kategori": "4. Pengangguran Menurut Pendidikan", "unit": "%",
        "desc": "Tingkat pengangguran angkatan kerja berpendidikan tinggi (Diploma, Sarjana, Pascasarjana)."
    },
    "Unemployment with Intermediate Education (% of Total Labor Force with Intermediate Education)": {
        "code": "SL.UEM.INTM.ZS", "kategori": "4. Pengangguran Menurut Pendidikan", "unit": "%",
        "desc": "Tingkat pengangguran angkatan kerja tamatan pendidikan menengah (SMP / SMA / SMK)."
    },
    "Unemployment with Basic Education (% of Total Labor Force with Basic Education)": {
        "code": "SL.UEM.BASC.ZS", "kategori": "4. Pengangguran Menurut Pendidikan", "unit": "%",
        "desc": "Tingkat pengangguran angkatan kerja berpendidikan dasar (SD atau di bawahnya)."
    },

    # =========================================================================
    # 5. Kualitas Pekerjaan, Formalisasi & Status Pekerjaan
    # =========================================================================
    "Vulnerable Employment (% of Total Employment)": {
        "code": "SL.EMP.VULN.ZS", "kategori": "5. Kualitas Pekerjaan & Formalitas", "unit": "%",
        "desc": "Proporsi pekerja rentan (pekerja keluarga tidak dibayar dan pekerja mandiri) terhadap total pekerja."
    },
    "Vulnerable Employment, Female (% of Female Employment)": {
        "code": "SL.EMP.VULN.FE.ZS", "kategori": "5. Kualitas Pekerjaan & Formalitas", "unit": "%",
        "desc": "Proporsi pekerja perempuan yang tergolong dalam status rentan."
    },
    "Vulnerable Employment, Male (% of Male Employment)": {
        "code": "SL.EMP.VULN.MA.ZS", "kategori": "5. Kualitas Pekerjaan & Formalitas", "unit": "%",
        "desc": "Proporsi pekerja laki-laki yang tergolong dalam status rentan."
    },
    "Wage and Salaried Workers / Formal Employees (% of Total Employment)": {
        "code": "SL.EMP.WORK.ZS", "kategori": "5. Kualitas Pekerjaan & Formalitas", "unit": "%",
        "desc": "Persentase pekerja penerima upah/gaji reguler (indikasi formalisasi pasar kerja)."
    },
    "Wage and Salaried Workers, Female (% of Female Employment)": {
        "code": "SL.EMP.WORK.FE.ZS", "kategori": "5. Kualitas Pekerjaan & Formalitas", "unit": "%",
        "desc": "Persentase tenaga kerja perempuan yang bekerja sebagai buruh/karyawan berupah tetap."
    },
    "Wage and Salaried Workers, Male (% of Male Employment)": {
        "code": "SL.EMP.WORK.MA.ZS", "kategori": "5. Kualitas Pekerjaan & Formalitas", "unit": "%",
        "desc": "Persentase tenaga kerja laki-laki yang bekerja sebagai buruh/karyawan berupah tetap."
    },
    "Own-Account Self-Employed Workers (% of Total Employment)": {
        "code": "SL.EMP.OWAC.ZS", "kategori": "5. Kualitas Pekerjaan & Formalitas", "unit": "%",
        "desc": "Persentase pekerja mandiri yang berusaha sendiri tanpa mempekerjakan buruh tetap."
    },
    "Contributing Family Workers (% of Total Employment)": {
        "code": "SL.FAM.WORK.ZS", "kategori": "5. Kualitas Pekerjaan & Formalitas", "unit": "%",
        "desc": "Persentase pekerja keluarga tanpa upah yang membantu usaha keluarga."
    },
    "Employers (% of Total Employment)": {
        "code": "SL.EMP.MPLY.ZS", "kategori": "5. Kualitas Pekerjaan & Formalitas", "unit": "%",
        "desc": "Persentase pelaku usaha yang mempekerjakan buruh atau tenaga kerja berbayar."
    },

    # =========================================================================
    # 6. Transformasi Struktural Sektoral (Distribusi Lapangan Usaha)
    # =========================================================================
    "Employment in Services Sector (% of Total Employment)": {
        "code": "SL.SRV.EMPL.ZS", "kategori": "6. Distribusi Sektoral Tenaga Kerja", "unit": "%",
        "desc": "Pangsa penyerapan tenaga kerja di sektor jasa dan perdagangan modern."
    },
    "Employment in Industry / Manufacturing (% of Total Employment)": {
        "code": "SL.IND.EMPL.ZS", "kategori": "6. Distribusi Sektoral Tenaga Kerja", "unit": "%",
        "desc": "Pangsa penyerapan tenaga kerja di sektor industri pengolahan, pertambangan, dan konstruksi."
    },
    "Employment in Agriculture (% of Total Employment)": {
        "code": "SL.AGR.EMPL.ZS", "kategori": "6. Distribusi Sektoral Tenaga Kerja", "unit": "%",
        "desc": "Pangsa penyerapan tenaga kerja di sektor primer pertanian, kehutanan, dan perikanan."
    },
    "Female Employment in Services (% of Female Employment)": {
        "code": "SL.SRV.EMPL.FE.ZS", "kategori": "6. Distribusi Sektoral Tenaga Kerja", "unit": "%",
        "desc": "Proporsi tenaga kerja perempuan yang terserap di sektor jasa."
    },
    "Female Employment in Industry (% of Female Employment)": {
        "code": "SL.IND.EMPL.FE.ZS", "kategori": "6. Distribusi Sektoral Tenaga Kerja", "unit": "%",
        "desc": "Proporsi tenaga kerja perempuan yang terserap di sektor industri/manufaktur."
    },
    "Female Employment in Agriculture (% of Female Employment)": {
        "code": "SL.AGR.EMPL.FE.ZS", "kategori": "6. Distribusi Sektoral Tenaga Kerja", "unit": "%",
        "desc": "Proporsi tenaga kerja perempuan yang terserap di sektor pertanian."
    },

    # =========================================================================
    # 7. Isu Khusus: Pekerja Anak & Manajemen Perempuan
    # =========================================================================
    "Children in Employment (% of Children Ages 7-14)": {
        "code": "SL.TLF.0714.ZS", "kategori": "7. Perlindungan & Representasi", "unit": "%",
        "desc": "Persentase anak usia 7–14 tahun yang terlibat dalam kegiatan ekonomi/bekerja."
    },
    "Female Share of Employment in Senior and Middle Management (%)": {
        "code": "SL.EMP.SMGT.FE.ZS", "kategori": "7. Perlindungan & Representasi", "unit": "%",
        "desc": "Porsi representasi perempuan pada posisi manajemen tingkat menengah hingga puncak."
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
    st.markdown(f"**Kode Seri Resmi:** `{kode_indikator}`")
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

                st.success(f"Berhasil menarik {len(df_ilo)} observasi tahunan resmi langsung dari server!")
                st.divider()

                # Unduh Data
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

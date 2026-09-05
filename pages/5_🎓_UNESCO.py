import io
import pandas as pd
import plotly.graph_objects as go
import requests
import streamlit as st

st.set_page_config(page_title="UNESCO Education Explorer - Indonesia", layout="wide")

st.title("🎓 UNESCO Institute for Statistics (UIS) - Pendidikan Indonesia")
st.write(
    "Eksplorasi indikator resmi partisipasi sekolah, literasi, anggaran pendidikan, dan rasio guru "
    "dari **UNESCO Institute for Statistics (UIS)** khusus untuk **Indonesia** "
    "secara langsung (*100% real-time live API*)."
)

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

# KATALOG RESMI INDIKATOR UNESCO UIS UNTUK INDONESIA (35 INDIKATOR)
UNESCO_CATALOG = {
    # =========================================================================
    # 1. Angka Partisipasi Kasar (APK / Gross Enrollment Ratio)
    # =========================================================================
    "School Enrollment, Pre-primary (% Gross)": {
        "code": "SE.PRE.ENRR", "kategori": "1. Angka Partisipasi Kasar (APK)", "unit": "% Gross",
        "desc": "Total pendaftaran anak di pendidikan usia dini / PAUD terlepas dari usia resmi."
    },
    "School Enrollment, Primary (% Gross)": {
        "code": "SE.PRM.ENRR", "kategori": "1. Angka Partisipasi Kasar (APK)", "unit": "% Gross",
        "desc": "Angka Partisipasi Kasar (APK) jenjang Sekolah Dasar (SD)."
    },
    "School Enrollment, Primary, Female (% Gross)": {
        "code": "SE.PRM.ENRR.FE", "kategori": "1. Angka Partisipasi Kasar (APK)", "unit": "% Gross",
        "desc": "Angka Partisipasi Kasar (APK) SD khusus murid perempuan."
    },
    "School Enrollment, Primary, Male (% Gross)": {
        "code": "SE.PRM.ENRR.MA", "kategori": "1. Angka Partisipasi Kasar (APK)", "unit": "% Gross",
        "desc": "Angka Partisipasi Kasar (APK) SD khusus murid laki-laki."
    },
    "School Enrollment, Secondary (% Gross)": {
        "code": "SE.SEC.ENRR", "kategori": "1. Angka Partisipasi Kasar (APK)", "unit": "% Gross",
        "desc": "Angka Partisipasi Kasar (APK) jenjang pendidikan menengah (SMP & SMA/SMK)."
    },
    "School Enrollment, Secondary, Female (% Gross)": {
        "code": "SE.SEC.ENRR.FE", "kategori": "1. Angka Partisipasi Kasar (APK)", "unit": "% Gross",
        "desc": "Angka Partisipasi Kasar (APK) pendidikan menengah murid perempuan."
    },
    "School Enrollment, Secondary, Male (% Gross)": {
        "code": "SE.SEC.ENRR.MA", "kategori": "1. Angka Partisipasi Kasar (APK)", "unit": "% Gross",
        "desc": "Angka Partisipasi Kasar (APK) pendidikan menengah murid laki-laki."
    },
    "School Enrollment, Tertiary (% Gross)": {
        "code": "SE.TER.ENRR", "kategori": "1. Angka Partisipasi Kasar (APK)", "unit": "% Gross",
        "desc": "Angka Partisipasi Kasar (APK) Perguruan Tinggi (Diploma/Sarjana)."
    },
    "School Enrollment, Tertiary, Female (% Gross)": {
        "code": "SE.TER.ENRR.FE", "kategori": "1. Angka Partisipasi Kasar (APK)", "unit": "% Gross",
        "desc": "Angka Partisipasi Kasar (APK) Perguruan Tinggi khusus mahasiswi."
    },
    "School Enrollment, Tertiary, Male (% Gross)": {
        "code": "SE.TER.ENRR.MA", "kategori": "1. Angka Partisipasi Kasar (APK)", "unit": "% Gross",
        "desc": "Angka Partisipasi Kasar (APK) Perguruan Tinggi khusus mahasiswa laki-laki."
    },

    # =========================================================================
    # 2. Angka Partisipasi Murni (APM / Net Enrollment Rate)
    # =========================================================================
    "School Enrollment, Primary (% Net)": {
        "code": "SE.PRM.NENR", "kategori": "2. Angka Partisipasi Murni (APM)", "unit": "% Net",
        "desc": "Proporsi anak usia resmi SD (7-12 tahun) yang benar-benar bersekolah di SD."
    },
    "School Enrollment, Primary, Female (% Net)": {
        "code": "SE.PRM.NENR.FE", "kategori": "2. Angka Partisipasi Murni (APM)", "unit": "% Net",
        "desc": "Angka Partisipasi Murni (APM) SD khusus anak perempuan."
    },
    "School Enrollment, Primary, Male (% Net)": {
        "code": "SE.PRM.NENR.MA", "kategori": "2. Angka Partisipasi Murni (APM)", "unit": "% Net",
        "desc": "Angka Partisipasi Murni (APM) SD khusus anak laki-laki."
    },
    "School Enrollment, Secondary (% Net)": {
        "code": "SE.SEC.NENR", "kategori": "2. Angka Partisipasi Murni (APM)", "unit": "% Net",
        "desc": "Proporsi anak usia resmi SMP & SMA yang bersekolah tepat pada jenjangnya."
    },

    # =========================================================================
    # 3. Kelulusan & Penyelesaian Pendidikan (Completion & Progression)
    # =========================================================================
    "Primary Completion Rate, Total (% of Relevant Age Group)": {
        "code": "SE.PRM.CMPT.ZS", "kategori": "3. Kelulusan & Putus Sekolah", "unit": "%",
        "desc": "Angka kelulusan pendidikan dasar (SD) terhadap kelompok usia kelulusan resmi."
    },
    "Lower Secondary Completion Rate, Total (%)": {
        "code": "SE.SEC.CMPT.LO.ZS", "kategori": "3. Kelulusan & Putus Sekolah", "unit": "%",
        "desc": "Angka penyelesaian pendidikan menengah pertama (SMP)."
    },
    "Progression to Secondary School (%)": {
        "code": "SE.SEC.PROG.ZS", "kategori": "3. Kelulusan & Putus Sekolah", "unit": "%",
        "desc": "Tingkat transisi kelulusan murid dari SD yang melanjutkan ke SMP."
    },
    "Children Out of School, Primary (Headcount)": {
        "code": "SE.PRM.UNER", "kategori": "3. Kelulusan & Putus Sekolah", "unit": "Anak",
        "desc": "Jumlah total anak usia SD yang putus sekolah atau tidak bersekolah."
    },
    "Children Out of School, Primary, Female (Headcount)": {
        "code": "SE.PRM.UNER.FE", "kategori": "3. Kelulusan & Putus Sekolah", "unit": "Anak",
        "desc": "Jumlah anak perempuan usia SD yang tidak bersekolah."
    },

    # =========================================================================
    # 4. Angka Melek Huruf / Literasi (Literacy Rates)
    # =========================================================================
    "Adult Literacy Rate, Total (% of People Ages 15 and Above)": {
        "code": "SE.ADT.LITR.ZS", "kategori": "4. Literasi & Melek Huruf", "unit": "%",
        "desc": "Persentase penduduk usia 15 tahun ke atas yang mampu membaca dan menulis."
    },
    "Adult Literacy Rate, Female (% of Females Ages 15+)": {
        "code": "SE.ADT.LITR.FE.ZS", "kategori": "4. Literasi & Melek Huruf", "unit": "%",
        "desc": "Angka melek aksara perempuan dewasa usia 15 tahun ke atas."
    },
    "Adult Literacy Rate, Male (% of Males Ages 15+)": {
        "code": "SE.ADT.LITR.MA.ZS", "kategori": "4. Literasi & Melek Huruf", "unit": "%",
        "desc": "Angka melek aksara laki-laki dewasa usia 15 tahun ke atas."
    },
    "Youth Literacy Rate, Total (% of People Ages 15-24)": {
        "code": "SE.ADT.1524.LT.ZS", "kategori": "4. Literasi & Melek Huruf", "unit": "%",
        "desc": "Angka melek aksara generasi muda usia 15-24 tahun."
    },

    # =========================================================================
    # 5. Kualitas Pengajaran & Beban Guru (Pupil-Teacher Ratios)
    # =========================================================================
    "Pupil-Teacher Ratio, Primary (Students per Teacher)": {
        "code": "SE.PRM.ENRL.TC.ZS", "kategori": "5. Rasio Murid-Guru & Tenaga Pendidik", "unit": "Murid per Guru",
        "desc": "Rata-rata jumlah murid yang diampu oleh satu orang guru di tingkat SD."
    },
    "Pupil-Teacher Ratio, Secondary (Students per Teacher)": {
        "code": "SE.SEC.ENRL.TC.ZS", "kategori": "5. Rasio Murid-Guru & Tenaga Pendidik", "unit": "Murid per Guru",
        "desc": "Rata-rata jumlah murid yang diampu oleh satu orang guru di tingkat SMP/SMA."
    },
    "Trained Teachers in Primary Education (% of Total Teachers)": {
        "code": "SE.PRM.TCAQ.ZS", "kategori": "5. Rasio Murid-Guru & Tenaga Pendidik", "unit": "%",
        "desc": "Persentase guru SD yang telah memenuhi kualifikasi pelatihan pedagogik resmi."
    },
    "Trained Teachers in Secondary Education (% of Total Teachers)": {
        "code": "SE.SEC.TCAQ.ZS", "kategori": "5. Rasio Murid-Guru & Tenaga Pendidik", "unit": "%",
        "desc": "Persentase guru SMP/SMA yang memiliki sertifikasi pelatihan guru resmi."
    },

    # =========================================================================
    # 6. Anggaran & Belanja Pendidikan (Education Financing)
    # =========================================================================
    "Government Expenditure on Education (% of GDP)": {
        "code": "SE.XPD.TOTL.GD.ZS", "kategori": "6. Anggaran & Belanja Pendidikan", "unit": "% of GDP",
        "desc": "Total belanja pemerintah untuk sektor pendidikan relatif terhadap Produk Domestik Bruto."
    },
    "Government Expenditure on Education (% of Total Government Expenditure)": {
        "code": "SE.XPD.TOTL.GB.ZS", "kategori": "6. Anggaran & Belanja Pendidikan", "unit": "% of Budget",
        "desc": "Pangsa alokasi anggaran pendidikan dalam total APBN/APBD (mandat konstitusi 20%)."
    },
    "Expenditure on Primary Education (% of Government Education Expenditure)": {
        "code": "SE.XPD.PRIM.ZS", "kategori": "6. Anggaran & Belanja Pendidikan", "unit": "% of Edu Exp",
        "desc": "Porsi alokasi belanja pendidikan publik yang dikhususkan untuk jenjang SD."
    },
    "Expenditure on Secondary Education (% of Government Education Expenditure)": {
        "code": "SE.XPD.SECO.ZS", "kategori": "6. Anggaran & Belanja Pendidikan", "unit": "% of Edu Exp",
        "desc": "Porsi alokasi belanja pendidikan publik yang dikhususkan untuk jenjang menengah."
    },
    "Expenditure on Tertiary Education (% of Government Education Expenditure)": {
        "code": "SE.XPD.TERT.ZS", "kategori": "6. Anggaran & Belanja Pendidikan", "unit": "% of Edu Exp",
        "desc": "Porsi alokasi belanja pendidikan publik yang dialokasikan ke Perguruan Tinggi."
    },

    # =========================================================================
    # 7. Kesetaraan Gender di Sekolah (Gender Parity Index)
    # =========================================================================
    "School Enrollment, Primary (Gender Parity Index / GPI)": {
        "code": "SE.ENR.PRIM.FM.ZS", "kategori": "7. Indeks Kesetaraan Gender (GPI)", "unit": "Rasio (F/M)",
        "desc": "Rasio angka pendaftaran murid perempuan terhadap laki-laki di SD (1.0 = kesetaraan penuh)."
    },
    "School Enrollment, Secondary (Gender Parity Index / GPI)": {
        "code": "SE.ENR.SECO.FM.ZS", "kategori": "7. Indeks Kesetaraan Gender (GPI)", "unit": "Rasio (F/M)",
        "desc": "Rasio angka pendaftaran murid perempuan terhadap laki-laki di jenjang menengah."
    },
    "School Enrollment, Tertiary (Gender Parity Index / GPI)": {
        "code": "SE.ENR.TERT.FM.ZS", "kategori": "7. Indeks Kesetaraan Gender (GPI)", "unit": "Rasio (F/M)",
        "desc": "Rasio angka pendaftaran mahasiswi terhadap mahasiswa di Perguruan Tinggi."
    }
}

# =============================================================================
# 1. KONTROL PEMILIHAN INDIKATOR
# =============================================================================
st.subheader("1. Pemilihan Indikator Resmi UNESCO UIS")
col_kat, col_ind = st.columns([1.2, 2])

kategori_list = sorted(list(set(v["kategori"] for v in UNESCO_CATALOG.values())))
with col_kat:
    pilihan_kategori = st.selectbox("Kategori Bidang Pendidikan:", ["Semua Kategori"] + kategori_list)

opsi = [
    k for k, v in UNESCO_CATALOG.items()
    if pilihan_kategori == "Semua Kategori" or v["kategori"] == pilihan_kategori
]

with col_ind:
    selected_name = st.selectbox(f"Nama Indikator ({len(opsi)} Tersedia):", opsi)

meta = UNESCO_CATALOG[selected_name]
kode_indikator = meta["code"]

with st.expander("ℹ️ Definisi & Metadata Resmi UNESCO UIS", expanded=False):
    st.markdown(f"**Nama Indikator:** {selected_name}")
    st.markdown(f"**Kode Seri Resmi:** `{kode_indikator}`")
    st.markdown(f"**Kategori:** `{meta['kategori']}`")
    st.markdown(f"**Satuan Pengukuran:** `{meta['unit']}`")
    st.markdown(f"**Metodologi / Deskripsi:**\n{meta['desc']}")
    st.markdown("🔗 **Basis Data:** [UNESCO Institute for Statistics (UIS)](http://uis.unesco.org/)")

# =============================================================================
# 2. PENARIKAN DATA LIVE VIA RESTFUL JSON API
# =============================================================================
st.subheader("2. Penarikan Data Runtun Waktu")

if st.button("📊 Ambil Data Pendidikan Indonesia", type="primary"):
    with st.spinner(f"Menghubungi endpoint resmi UNESCO untuk seri {kode_indikator}..."):
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
                df_unesco = pd.DataFrame(records).sort_values(by="Tahun", ascending=True)

                st.success(f"Berhasil menarik {len(df_unesco)} observasi tahunan resmi dari server UNESCO UIS!")
                st.divider()

                # Tombol Unduh Data
                c1, c2 = st.columns(2)
                c1.download_button(
                    "📥 Unduh CSV",
                    df_unesco.to_csv(index=False).encode("utf-8"),
                    f"UNESCO_IDN_{kode_indikator}.csv",
                    "text/csv"
                )
                buf = io.BytesIO()
                with pd.ExcelWriter(buf, engine="openpyxl") as writer:
                    df_unesco.to_excel(writer, index=False, sheet_name="UNESCO Data")
                c2.download_button(
                    "📊 Unduh Excel (.xlsx)",
                    buf.getvalue(),
                    f"UNESCO_IDN_{kode_indikator}.xlsx",
                    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )

                # Visualisasi Plotly Interaktif
                fig = go.Figure()
                fig.add_trace(go.Scatter(
                    x=df_unesco["Tahun"],
                    y=df_unesco[val_col],
                    mode="lines+markers",
                    name="Indonesia (UNESCO)",
                    line=dict(width=2.5, color="#007791"),  # Biru Kehijauan Khas Edukasi
                    hovertemplate=f"Tahun %{{x}}<br>Nilai: %{{y:.2f}} {meta['unit']}<extra></extra>"
                ))
                
                # Garis ambang batas untuk Indeks Kesetaraan Gender (GPI = 1.0)
                if "GPI" in meta["unit"] or "Rasio (F/M)" in meta["unit"]:
                    fig.add_hline(y=1.0, line_dash="dash", line_color="orange", annotation_text="Paritas Penuh (1.0)")

                fig.update_layout(
                    xaxis=dict(title="Tahun", tickmode="linear"),
                    yaxis=dict(title=meta["unit"]),
                    hovermode="x unified",
                    margin=dict(l=20, r=20, t=40, b=20)
                )
                st.plotly_chart(fig, use_container_width=True)

                with st.expander("📋 Tabel Data Runtun Waktu Lengkap"):
                    st.dataframe(df_unesco.sort_values(by="Tahun", ascending=False), use_container_width=True)
            else:
                st.warning("Observasi runtun waktu untuk indikator ini belum dilaporkan atau sedang dalam pembaruan berkala di server UNESCO.")
        except Exception as e:
            st.error(f"Gagal menghubungi server data UNESCO: {e}")

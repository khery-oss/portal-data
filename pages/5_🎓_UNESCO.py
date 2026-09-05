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

# Kode negara Indonesia di UIS API
COUNTRY_CODE = "IDN"

# =============================================================================
# KATALOG INDIKATOR UNESCO UIS
# Kode menggunakan format resmi UIS API (bukan World Bank mirror)
# Referensi: https://api.uis.unesco.org/api/public/definitions/indicators
# =============================================================================
UNESCO_CATALOG = {
    # =========================================================================
    # 1. Angka Partisipasi Kasar (APK / Gross Enrollment Ratio)
    # =========================================================================
    "School Enrollment, Pre-primary (% Gross)": {
        "code": "NERA.1.cp", "kategori": "1. Angka Partisipasi Kasar (APK)", "unit": "% Gross",
        "gpi": False,
        "desc": "Total pendaftaran anak di pendidikan usia dini / PAUD terlepas dari usia resmi."
    },
    "School Enrollment, Primary (% Gross)": {
        "code": "NERA.1", "kategori": "1. Angka Partisipasi Kasar (APK)", "unit": "% Gross",
        "gpi": False,
        "desc": "Angka Partisipasi Kasar (APK) jenjang Sekolah Dasar (SD)."
    },
    "School Enrollment, Primary, Female (% Gross)": {
        "code": "NERA.1.F", "kategori": "1. Angka Partisipasi Kasar (APK)", "unit": "% Gross",
        "gpi": False,
        "desc": "Angka Partisipasi Kasar (APK) SD khusus murid perempuan."
    },
    "School Enrollment, Primary, Male (% Gross)": {
        "code": "NERA.1.M", "kategori": "1. Angka Partisipasi Kasar (APK)", "unit": "% Gross",
        "gpi": False,
        "desc": "Angka Partisipasi Kasar (APK) SD khusus murid laki-laki."
    },
    "School Enrollment, Secondary (% Gross)": {
        "code": "NERA.2", "kategori": "1. Angka Partisipasi Kasar (APK)", "unit": "% Gross",
        "gpi": False,
        "desc": "Angka Partisipasi Kasar (APK) jenjang pendidikan menengah (SMP & SMA/SMK)."
    },
    "School Enrollment, Secondary, Female (% Gross)": {
        "code": "NERA.2.F", "kategori": "1. Angka Partisipasi Kasar (APK)", "unit": "% Gross",
        "gpi": False,
        "desc": "Angka Partisipasi Kasar (APK) pendidikan menengah murid perempuan."
    },
    "School Enrollment, Secondary, Male (% Gross)": {
        "code": "NERA.2.M", "kategori": "1. Angka Partisipasi Kasar (APK)", "unit": "% Gross",
        "gpi": False,
        "desc": "Angka Partisipasi Kasar (APK) pendidikan menengah murid laki-laki."
    },
    "School Enrollment, Tertiary (% Gross)": {
        "code": "NERA.5T8", "kategori": "1. Angka Partisipasi Kasar (APK)", "unit": "% Gross",
        "gpi": False,
        "desc": "Angka Partisipasi Kasar (APK) Perguruan Tinggi (Diploma/Sarjana)."
    },
    "School Enrollment, Tertiary, Female (% Gross)": {
        "code": "NERA.5T8.F", "kategori": "1. Angka Partisipasi Kasar (APK)", "unit": "% Gross",
        "gpi": False,
        "desc": "Angka Partisipasi Kasar (APK) Perguruan Tinggi khusus mahasiswi."
    },
    "School Enrollment, Tertiary, Male (% Gross)": {
        "code": "NERA.5T8.M", "kategori": "1. Angka Partisipasi Kasar (APK)", "unit": "% Gross",
        "gpi": False,
        "desc": "Angka Partisipasi Kasar (APK) Perguruan Tinggi khusus mahasiswa laki-laki."
    },

    # =========================================================================
    # 2. Angka Partisipasi Murni (APM / Net Enrollment Rate)
    # =========================================================================
    "School Enrollment, Primary (% Net)": {
        "code": "NERA.1.cp", "kategori": "2. Angka Partisipasi Murni (APM)", "unit": "% Net",
        "gpi": False,
        "desc": "Proporsi anak usia resmi SD (7-12 tahun) yang benar-benar bersekolah di SD."
    },
    "School Enrollment, Primary, Female (% Net)": {
        "code": "NERA.1.cp.F", "kategori": "2. Angka Partisipasi Murni (APM)", "unit": "% Net",
        "gpi": False,
        "desc": "Angka Partisipasi Murni (APM) SD khusus anak perempuan."
    },
    "School Enrollment, Primary, Male (% Net)": {
        "code": "NERA.1.cp.M", "kategori": "2. Angka Partisipasi Murni (APM)", "unit": "% Net",
        "gpi": False,
        "desc": "Angka Partisipasi Murni (APM) SD khusus anak laki-laki."
    },
    "School Enrollment, Secondary (% Net)": {
        "code": "NERA.2.cp", "kategori": "2. Angka Partisipasi Murni (APM)", "unit": "% Net",
        "gpi": False,
        "desc": "Proporsi anak usia resmi SMP & SMA yang bersekolah tepat pada jenjangnya."
    },

    # =========================================================================
    # 3. Kelulusan & Penyelesaian Pendidikan
    # =========================================================================
    "Primary Completion Rate, Total (% of Relevant Age Group)": {
        "code": "CR.1", "kategori": "3. Kelulusan & Putus Sekolah", "unit": "%",
        "gpi": False,
        "desc": "Angka kelulusan pendidikan dasar (SD) terhadap kelompok usia kelulusan resmi."
    },
    "Lower Secondary Completion Rate, Total (%)": {
        "code": "CR.2", "kategori": "3. Kelulusan & Putus Sekolah", "unit": "%",
        "gpi": False,
        "desc": "Angka penyelesaian pendidikan menengah pertama (SMP)."
    },
    "Children Out of School, Primary (Headcount)": {
        "code": "OOSR.1.cp", "kategori": "3. Kelulusan & Putus Sekolah", "unit": "Anak",
        "gpi": False,
        "desc": "Jumlah total anak usia SD yang putus sekolah atau tidak bersekolah."
    },
    "Children Out of School, Primary, Female (Headcount)": {
        "code": "OOSR.1.cp.F", "kategori": "3. Kelulusan & Putus Sekolah", "unit": "Anak",
        "gpi": False,
        "desc": "Jumlah anak perempuan usia SD yang tidak bersekolah."
    },

    # =========================================================================
    # 4. Literasi & Melek Huruf
    # =========================================================================
    "Adult Literacy Rate, Total (% of People Ages 15 and Above)": {
        "code": "LR.AG15T99", "kategori": "4. Literasi & Melek Huruf", "unit": "%",
        "gpi": False,
        "desc": "Persentase penduduk usia 15 tahun ke atas yang mampu membaca dan menulis."
    },
    "Adult Literacy Rate, Female (% of Females Ages 15+)": {
        "code": "LR.AG15T99.F", "kategori": "4. Literasi & Melek Huruf", "unit": "%",
        "gpi": False,
        "desc": "Angka melek aksara perempuan dewasa usia 15 tahun ke atas."
    },
    "Adult Literacy Rate, Male (% of Males Ages 15+)": {
        "code": "LR.AG15T99.M", "kategori": "4. Literasi & Melek Huruf", "unit": "%",
        "gpi": False,
        "desc": "Angka melek aksara laki-laki dewasa usia 15 tahun ke atas."
    },
    "Youth Literacy Rate, Total (% of People Ages 15-24)": {
        "code": "LR.AG15T24", "kategori": "4. Literasi & Melek Huruf", "unit": "%",
        "gpi": False,
        "desc": "Angka melek aksara generasi muda usia 15-24 tahun."
    },

    # =========================================================================
    # 5. Rasio Murid-Guru & Tenaga Pendidik
    # =========================================================================
    "Pupil-Teacher Ratio, Primary (Students per Teacher)": {
        "code": "PTR.1", "kategori": "5. Rasio Murid-Guru & Tenaga Pendidik", "unit": "Murid per Guru",
        "gpi": False,
        "desc": "Rata-rata jumlah murid yang diampu oleh satu orang guru di tingkat SD."
    },
    "Pupil-Teacher Ratio, Secondary (Students per Teacher)": {
        "code": "PTR.2", "kategori": "5. Rasio Murid-Guru & Tenaga Pendidik", "unit": "Murid per Guru",
        "gpi": False,
        "desc": "Rata-rata jumlah murid yang diampu oleh satu orang guru di tingkat SMP/SMA."
    },
    "Trained Teachers in Primary Education (% of Total Teachers)": {
        "code": "TRTP.1", "kategori": "5. Rasio Murid-Guru & Tenaga Pendidik", "unit": "%",
        "gpi": False,
        "desc": "Persentase guru SD yang telah memenuhi kualifikasi pelatihan pedagogik resmi."
    },
    "Trained Teachers in Secondary Education (% of Total Teachers)": {
        "code": "TRTP.2", "kategori": "5. Rasio Murid-Guru & Tenaga Pendidik", "unit": "%",
        "gpi": False,
        "desc": "Persentase guru SMP/SMA yang memiliki sertifikasi pelatihan guru resmi."
    },

    # =========================================================================
    # 6. Anggaran & Belanja Pendidikan
    # =========================================================================
    "Government Expenditure on Education (% of GDP)": {
        "code": "XGDP.FSGOV", "kategori": "6. Anggaran & Belanja Pendidikan", "unit": "% of GDP",
        "gpi": False,
        "desc": "Total belanja pemerintah untuk sektor pendidikan relatif terhadap Produk Domestik Bruto."
    },
    "Government Expenditure on Education (% of Total Government Expenditure)": {
        "code": "XGOV.FSGOV", "kategori": "6. Anggaran & Belanja Pendidikan", "unit": "% of Budget",
        "gpi": False,
        "desc": "Pangsa alokasi anggaran pendidikan dalam total APBN/APBD (mandat konstitusi 20%)."
    },
    "Expenditure on Primary Education (% of Government Education Expenditure)": {
        "code": "XUNIT.FSGOV.PPPCONST.1", "kategori": "6. Anggaran & Belanja Pendidikan", "unit": "% of Edu Exp",
        "gpi": False,
        "desc": "Porsi alokasi belanja pendidikan publik yang dikhususkan untuk jenjang SD."
    },
    "Expenditure on Tertiary Education (% of Government Education Expenditure)": {
        "code": "XUNIT.FSGOV.PPPCONST.5T8", "kategori": "6. Anggaran & Belanja Pendidikan", "unit": "% of Edu Exp",
        "gpi": False,
        "desc": "Porsi alokasi belanja pendidikan publik yang dialokasikan ke Perguruan Tinggi."
    },

    # =========================================================================
    # 7. Indeks Kesetaraan Gender (GPI)
    # =========================================================================
    "School Enrollment, Primary (Gender Parity Index / GPI)": {
        "code": "NERA.1.GPI", "kategori": "7. Indeks Kesetaraan Gender (GPI)", "unit": "Rasio (F/M)",
        "gpi": True,
        "desc": "Rasio angka pendaftaran murid perempuan terhadap laki-laki di SD (1.0 = kesetaraan penuh)."
    },
    "School Enrollment, Secondary (Gender Parity Index / GPI)": {
        "code": "NERA.2.GPI", "kategori": "7. Indeks Kesetaraan Gender (GPI)", "unit": "Rasio (F/M)",
        "gpi": True,
        "desc": "Rasio angka pendaftaran murid perempuan terhadap laki-laki di jenjang menengah."
    },
    "School Enrollment, Tertiary (Gender Parity Index / GPI)": {
        "code": "NERA.5T8.GPI", "kategori": "7. Indeks Kesetaraan Gender (GPI)", "unit": "Rasio (F/M)",
        "gpi": True,
        "desc": "Rasio angka pendaftaran mahasiswi terhadap mahasiswa di Perguruan Tinggi."
    },
    "Literacy Rate (Gender Parity Index / GPI)": {
        "code": "LR.AG15T99.GPI", "kategori": "7. Indeks Kesetaraan Gender (GPI)", "unit": "Rasio (F/M)",
        "gpi": True,
        "desc": "Rasio angka melek huruf perempuan terhadap laki-laki usia 15 tahun ke atas."
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
    st.markdown(f"**Kode Seri UIS:** `{kode_indikator}`")
    st.markdown(f"**Kategori:** `{meta['kategori']}`")
    st.markdown(f"**Satuan Pengukuran:** `{meta['unit']}`")
    st.markdown(f"**Metodologi / Deskripsi:**\n{meta['desc']}")
    st.markdown("🔗 **Basis Data:** [UNESCO Institute for Statistics (UIS)](https://uis.unesco.org/)")

# =============================================================================
# 2. PENARIKAN DATA — UIS NATIVE API
# =============================================================================
st.subheader("2. Penarikan Data Runtun Waktu")

def fetch_uis(indicator_code: str, country: str) -> list:
    """
    Tarik data dari UIS API native (api.uis.unesco.org).
    Fallback ke World Bank mirror jika UIS API tidak merespons.
    """
    # Endpoint 1: UIS API native
    uis_url = (
        f"https://api.uis.unesco.org/api/public/data/indicators"
        f"?indicator={indicator_code}&country={country}&format=json"
    )
    try:
        res = requests.get(uis_url, headers=HEADERS, timeout=20)
        if res.status_code == 200:
            payload = res.json()
            data_list = payload.get("data", payload if isinstance(payload, list) else [])
            records = []
            for row in data_list:
                thn = row.get("year") or row.get("period")
                val = row.get("value")
                if thn is not None and val is not None:
                    try:
                        records.append({"Tahun": int(str(thn)[:4]), "nilai_raw": float(val)})
                    except (ValueError, TypeError):
                        continue
            if records:
                return records, "UIS API"
    except Exception:
        pass

    # Endpoint 2: World Bank mirror (fallback)
    # Kode WB untuk indikator UIS menggunakan format SE.xxx
    wb_code_map = {
        "NERA.1.cp": "SE.PRE.ENRR", "NERA.1": "SE.PRM.ENRR",
        "NERA.1.F": "SE.PRM.ENRR.FE", "NERA.1.M": "SE.PRM.ENRR.MA",
        "NERA.2": "SE.SEC.ENRR", "NERA.2.F": "SE.SEC.ENRR.FE",
        "NERA.2.M": "SE.SEC.ENRR.MA", "NERA.5T8": "SE.TER.ENRR",
        "NERA.5T8.F": "SE.TER.ENRR.FE", "NERA.5T8.M": "SE.TER.ENRR.MA",
        "NERA.1.cp.F": "SE.PRM.NENR.FE", "NERA.1.cp.M": "SE.PRM.NENR.MA",
        "NERA.2.cp": "SE.SEC.NENR",
        "CR.1": "SE.PRM.CMPT.ZS", "CR.2": "SE.SEC.CMPT.LO.ZS",
        "OOSR.1.cp": "SE.PRM.UNER", "OOSR.1.cp.F": "SE.PRM.UNER.FE",
        "LR.AG15T99": "SE.ADT.LITR.ZS", "LR.AG15T99.F": "SE.ADT.LITR.FE.ZS",
        "LR.AG15T99.M": "SE.ADT.LITR.MA.ZS", "LR.AG15T24": "SE.ADT.1524.LT.ZS",
        "PTR.1": "SE.PRM.ENRL.TC.ZS", "PTR.2": "SE.SEC.ENRL.TC.ZS",
        "TRTP.1": "SE.PRM.TCAQ.ZS", "TRTP.2": "SE.SEC.TCAQ.ZS",
        "XGDP.FSGOV": "SE.XPD.TOTL.GD.ZS", "XGOV.FSGOV": "SE.XPD.TOTL.GB.ZS",
        "XUNIT.FSGOV.PPPCONST.1": "SE.XPD.PRIM.ZS",
        "XUNIT.FSGOV.PPPCONST.5T8": "SE.XPD.TERT.ZS",
        "NERA.1.GPI": "SE.ENR.PRIM.FM.ZS", "NERA.2.GPI": "SE.ENR.SECO.FM.ZS",
        "NERA.5T8.GPI": "SE.ENR.TERT.FM.ZS", "LR.AG15T99.GPI": None,
    }
    wb_code = wb_code_map.get(indicator_code)
    if wb_code:
        try:
            wb_url = f"https://api.worldbank.org/v2/country/IDN/indicator/{wb_code}?format=json&per_page=1000"
            res_wb = requests.get(wb_url, headers=HEADERS, timeout=20)
            if res_wb.status_code == 200:
                payload_wb = res_wb.json()
                if len(payload_wb) > 1 and isinstance(payload_wb[1], list):
                    records = []
                    for item in payload_wb[1]:
                        thn = item.get("date")
                        val = item.get("value")
                        if thn is not None and val is not None:
                            try:
                                records.append({"Tahun": int(thn), "nilai_raw": round(float(val), 4)})
                            except (ValueError, TypeError):
                                continue
                    if records:
                        return records, "World Bank (UNESCO mirror)"
        except Exception:
            pass

    return [], None

if st.button("📊 Ambil Data Pendidikan Indonesia", type="primary"):
    with st.spinner(f"Menghubungi server UNESCO UIS untuk seri {kode_indikator}..."):
        records, sumber = fetch_uis(kode_indikator, COUNTRY_CODE)

        if records:
            val_col = f"Nilai ({meta['unit']})"
            df_unesco = (
                pd.DataFrame(records)
                .groupby("Tahun", as_index=False)["nilai_raw"]
                .mean()
                .round(2)
                .rename(columns={"nilai_raw": val_col})
                .sort_values(by="Tahun", ascending=True)
            )

            st.success(f"Berhasil menarik **{len(df_unesco)}** observasi tahunan dari **{sumber}**!")
            st.divider()

            # Tombol Unduh
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

            # Visualisasi Plotly
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=df_unesco["Tahun"],
                y=df_unesco[val_col],
                mode="lines+markers",
                name="Indonesia (UNESCO UIS)",
                line=dict(width=2.5, color="#007791"),
                marker=dict(size=7),
                hovertemplate=f"Tahun %{{x}}<br>Nilai: %{{y:.2f}} {meta['unit']}<extra></extra>"
            ))

            # Garis paritas gender — berdasarkan flag `gpi` di katalog, bukan tebak-tebak string
            if meta.get("gpi"):
                fig.add_hline(
                    y=1.0,
                    line_dash="dash",
                    line_color="orange",
                    annotation_text="Paritas Penuh (1.0)",
                    annotation_position="top right"
                )

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
            st.warning(
                "Observasi untuk indikator ini belum tersedia atau sedang dalam pembaruan. "
                "Coba pilih indikator lain."
            )

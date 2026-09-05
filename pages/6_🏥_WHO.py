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

# DAFTAR KURASI INDIKATOR PILIHAN WHO YANG TERBUKTI AKTIF & LENGKAP UNTUK INDONESIA
WHO_CATALOG = {
    # --- 1. Life Expectancy & Mortality ---
    "Life expectancy at birth (years)": {
        "code": "WHOSIS_000001", "kategori": "1. Life Expectancy & Mortality", "unit": "Years",
        "desc": "Average number of years that a newborn is expected to live if current mortality rates apply."
    },
    "Healthy life expectancy (HALE) at birth (years)": {
        "code": "WHOSIS_000002", "kategori": "1. Life Expectancy & Mortality", "unit": "Years",
        "desc": "Average number of years that a person can expect to live in full health."
    },
    "Life expectancy at age 60 (years)": {
        "code": "WHOSIS_000015", "kategori": "1. Life Expectancy & Mortality", "unit": "Years",
        "desc": "Average number of years that a person at age 60 can expect to live."
    },
    "Probability (%) of dying between exact ages 30 and 70 from cardiovascular disease, cancer, diabetes, or chronic respiratory disease": {
        "code": "NCDMORT3070", "kategori": "1. Life Expectancy & Mortality", "unit": "%",
        "desc": "Unconditional probability of dying between ages 30 and 70 from major non-communicable diseases."
    },
    "Adult mortality rate (probability of dying between 15 and 60 years per 1,000 population)": {
        "code": "WHOSIS_000007", "kategori": "1. Life Expectancy & Mortality", "unit": "Per 1,000 Population",
        "desc": "Probability of a 15-year-old dying before reaching age 60."
    },

    # --- 2. Child & Maternal Health ---
    "Under-five mortality rate (probability of dying by age 5 per 1,000 live births)": {
        "code": "MDG_0000000007", "kategori": "2. Child & Maternal Health", "unit": "Per 1,000 Live Births",
        "desc": "Probability of dying between birth and exact age 5 per 1,000 live births."
    },
    "Infant mortality rate (probability of dying between birth and exact age 1 per 1,000 live births)": {
        "code": "MDG_0000000001", "kategori": "2. Child & Maternal Health", "unit": "Per 1,000 Live Births",
        "desc": "Probability of dying between birth and exact age 1."
    },
    "Neonatal mortality rate (per 1,000 live births)": {
        "code": "WHOSIS_000003", "kategori": "2. Child & Maternal Health", "unit": "Per 1,000 Live Births",
        "desc": "Probability of dying during the first 28 completed days of life per 1,000 live births."
    },
    "Maternal mortality ratio (per 100,000 live births)": {
        "code": "MDG_0000000026", "kategori": "2. Child & Maternal Health", "unit": "Per 100,000 Live Births",
        "desc": "Number of maternal deaths per 100,000 live births during a specified time period."
    },

    # --- 3. Nutrition & Growth ---
    "Stunting prevalence among children under 5 years (%)": {
        "code": "NUTRITION_STUNTING_PREV", "kategori": "3. Nutrition & Growth", "unit": "%",
        "desc": "Prevalence of moderate and severe stunting (height-for-age < -2 SD from WHO median)."
    },
    "Wasting prevalence among children under 5 years (%)": {
        "code": "NUTRITION_WASTING_PREV", "kategori": "3. Nutrition & Growth", "unit": "%",
        "desc": "Prevalence of moderate and severe wasting (weight-for-height < -2 SD from WHO median)."
    },
    "Overweight prevalence among children under 5 years (%)": {
        "code": "NUTRITION_OVERWEIGHT_PREV", "kategori": "3. Nutrition & Growth", "unit": "%",
        "desc": "Prevalence of overweight (weight-for-height > +2 SD from WHO median)."
    },

    # --- 4. Immunization & Infectious Diseases ---
    "Measles-containing-vaccine first-dose (MCV1) immunization coverage among 1-year-olds (%)": {
        "code": "WHS3_62", "kategori": "4. Immunization & Infectious Diseases", "unit": "%",
        "desc": "Percentage of surviving infants who received one dose of measles-containing vaccine."
    },
    "Tuberculosis incidence (per 100,000 population)": {
        "code": "MDG_0000000020", "kategori": "4. Immunization & Infectious Diseases", "unit": "Per 100,000 Population",
        "desc": "Estimated number of new and relapse tuberculosis cases arising in a given year."
    },

    # --- 5. Health Workforce & Infrastructure ---
    "Medical doctors (per 10,000 population)": {
        "code": "HWF_0001", "kategori": "5. Health Workforce", "unit": "Per 10,000 Population",
        "desc": "Number of medical doctors per 10,000 population."
    },
    "Nursing and midwifery personnel (per 10,000 population)": {
        "code": "HWF_0002", "kategori": "5. Health Workforce", "unit": "Per 10,000 Population",
        "desc": "Number of nursing and midwifery personnel per 10,000 population."
    },

    # --- 6. UHC & Health Financing ---
    "UHC service coverage index": {
        "code": "UHC_INDEX_REPORTED", "kategori": "6. UHC & Health Financing", "unit": "Index (0-100)",
        "desc": "Composite index of essential service coverage."
    },
    "Out-of-pocket expenditure as percentage of current health expenditure (CHE) (%)": {
        "code": "SH_XPD_OOPC_CH_ZS", "kategori": "6. UHC & Health Financing", "unit": "% of Current Health Exp.",
        "desc": "Share of out-of-pocket payments by households in total health expenditure."
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
    st.markdown(f"**Indikator Resmi WHO:** {nama_indikator}")
    st.markdown(f"**Kode Seri GHO:** `{code_id}`")
    st.markdown(f"**Satuan Pengukuran:** `{meta['unit']}`")
    st.markdown(f"**Cakupan Geografis:** Indonesia (IDN)")
    st.markdown(f"**Deskripsi Metodologi:**\n{meta['desc']}")
    st.markdown("🔗 **Portal Sumber Resmi:** [WHO Global Health Observatory](https://www.who.int/data/gho)")

# =============================================================================
# 2. PENARIKAN DATA LIVE API WHO (INDONESIA)
# =============================================================================
st.subheader("2. Penarikan Data Runtun Waktu Nasional (Indonesia)")
st.caption("Seluruh riwayat tahun yang tercatat di basis data resmi WHO akan diambil secara *real-time*.")

if st.button("📊 Ambil Data WHO (Live API)", type="primary"):
    with st.spinner(f"Menghubungi server WHO GHO API untuk seri '{nama_indikator}'..."):
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

                    st.success(f"Berhasil menarik {len(df_who)} observasi tahunan resmi untuk Indonesia langsung dari server WHO!")
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

                    # Visualisasi Plotly Interaktif
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
                    st.warning("Server WHO merespons, namun catatan observasi runtun waktu untuk Indonesia belum dipublikasikan pada seri indikator ini.")
            else:
                st.error(f"Gagal menghubungi server WHO (Kode Status HTTP: {res.status_code}).")
        except Exception as e:
            st.error(f"Terjadi kesalahan saat memproses data WHO: {e}")

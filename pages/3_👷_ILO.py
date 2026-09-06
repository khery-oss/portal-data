import io
import pandas as pd
import plotly.graph_objects as go
import requests
import streamlit as st

st.set_page_config(page_title="ILO Labour Market Explorer - Indonesia", layout="wide")

st.title("👷 ILO (International Labour Organization) - Pasar Tenaga Kerja Indonesia")
st.write(
    "Eksplorasi indikator pasar tenaga kerja Indonesia dari **International Labour Organization (ILO)** "
    "via World Bank Data API — sumber mirror resmi ILOSTAT yang digunakan secara internasional. "
    "Hanya indikator yang benar-benar memiliki data Indonesia yang ditampilkan."
)

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

# =============================================================================
# 1. LOAD KATALOG INDIKATOR KETENAGAKERJAAN ILO DARI WORLD BANK
# Sumber: World Bank source=2 (WDI) — filter topik labour & social protection
# =============================================================================
@st.cache_data(ttl=86400, show_spinner=False)
def load_labour_indicators():
    """Ambil semua indikator ketenagakerjaan ILO dari World Bank WDI."""
    indicators = []
    # Topic 10 = Social Protection & Labor (ILO data ada di sini)
    url = "https://api.worldbank.org/v2/indicator?source=2&topic=10&format=json&per_page=3000"
    try:
        res = requests.get(url, headers=HEADERS, timeout=25)
        data = res.json()
        if len(data) > 1 and data[1]:
            for item in data[1]:
                ind_id = item.get("id")
                ind_name = item.get("name")
                if ind_id and ind_name:
                    indicators.append({
                        "id": ind_id,
                        "name": ind_name,
                        "sourceNote": item.get("sourceNote", ""),
                    })
    except Exception:
        pass
    return indicators

with st.spinner("Menghubungkan ke katalog ILO via World Bank..."):
    all_indicators = load_labour_indicators()

if not all_indicators:
    st.error("Gagal memuat katalog indikator. Periksa koneksi internet.")
    st.stop()

# =============================================================================
# 2. PENCARIAN INDIKATOR
# =============================================================================
st.subheader("1. Pencarian Indikator Ketenagakerjaan")

query = st.text_input(
    "🔍 Ketik topik ketenagakerjaan (Bahasa Inggris):",
    placeholder="Contoh: unemployment, labor force, employment, wage, vulnerable, neet, self-employed",
    value="unemployment"
).strip()

if query:
    query_tokens = query.lower().split()
    results = [
        ind for ind in all_indicators
        if all(
            token in ind["name"].lower() or token in ind["id"].lower()
            for token in query_tokens
        )
    ]
    results = sorted(results, key=lambda x: len(x["name"]))

    if not results:
        st.warning(f"Tidak ditemukan indikator ketenagakerjaan untuk kata kunci **'{query}'**. Coba kata kunci lain.")
        st.stop()

    st.success(f"Ditemukan **{len(results)}** indikator terkait **'{query}'** di katalog ILO.")

    selected_ind = st.selectbox(
        "Pilih Indikator:",
        options=results,
        format_func=lambda item: item["name"]
    )

    kode_indikator = selected_ind["id"]

    with st.expander("ℹ️ Definisi & Metadata Resmi", expanded=False):
        st.markdown(f"**Kode Indikator ILO:** `{kode_indikator}`")
        st.markdown(f"**Sumber:** International Labour Organization (ILOSTAT) via World Bank Data API")
        note = selected_ind.get("sourceNote", "")
        if note:
            st.markdown(f"**Definisi:** {note}")
        st.markdown("🔗 [ILOSTAT — International Labour Organization](https://ilostat.ilo.org/)")

    # =============================================================================
    # 3. PENARIKAN DATA INDONESIA
    # =============================================================================
    st.subheader("2. Penarikan Data Indonesia")

    if st.button("📊 Ambil Data Ketenagakerjaan Indonesia", type="primary"):
        with st.spinner(f"Menarik data Indonesia untuk '{selected_ind['name']}'..."):
            api_url = (
                f"https://api.worldbank.org/v2/country/IDN/indicator/{kode_indikator}"
                f"?format=json&per_page=1000"
            )
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
                                        "nilai_raw": round(float(val), 4)
                                    })
                                except (ValueError, TypeError):
                                    continue

                if not records:
                    st.warning(
                        f"Indikator **'{selected_ind['name']}'** terdaftar di katalog ILO "
                        f"namun data untuk Indonesia belum tersedia. Silakan pilih indikator lain."
                    )
                    st.stop()

                # Deteksi unit dari nama indikator
                name_lower = selected_ind["name"].lower()
                if "% of gdp" in name_lower:
                    unit = "% of GDP"
                elif "ratio" in name_lower and "%" not in selected_ind["name"]:
                    unit = "Rasio"
                elif "%" in selected_ind["name"]:
                    unit = "%"
                elif any(k in name_lower for k in ["number", "headcount", "persons", "total labor force"]):
                    unit = "Jiwa"
                else:
                    unit = "Nilai"

                val_col = f"Nilai ({unit})"
                df_ilo = (
                    pd.DataFrame(records)
                    .groupby("Tahun", as_index=False)["nilai_raw"]
                    .mean()
                    .round(2)
                    .rename(columns={"nilai_raw": val_col})
                    .sort_values(by="Tahun", ascending=True)
                )

                st.success(f"Berhasil menarik **{len(df_ilo)}** observasi tahunan untuk Indonesia!")
                st.divider()

                # Tombol Unduh
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

                # Visualisasi Plotly
                fig = go.Figure()
                fig.add_trace(go.Scatter(
                    x=df_ilo["Tahun"],
                    y=df_ilo[val_col],
                    mode="lines+markers",
                    name="Indonesia (ILO)",
                    line=dict(width=2.5, color="#D9534F"),
                    marker=dict(size=7),
                    hovertemplate=f"Tahun %{{x}}<br>Nilai: %{{y:.2f}} {unit}<extra></extra>"
                ))
                fig.update_layout(
                    xaxis=dict(title="Tahun", tickmode="linear"),
                    yaxis=dict(title=unit),
                    hovermode="x unified",
                    margin=dict(l=20, r=20, t=40, b=20)
                )
                st.plotly_chart(fig, use_container_width=True)

                with st.expander("📋 Tabel Data Runtun Waktu Lengkap"):
                    st.dataframe(
                        df_ilo.sort_values(by="Tahun", ascending=False),
                        use_container_width=True
                    )

            except Exception as e:
                st.error(f"Gagal mengambil data: {e}")

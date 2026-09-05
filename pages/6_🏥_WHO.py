import io
import pandas as pd
import plotly.graph_objects as go
import requests
import streamlit as st

st.set_page_config(page_title="WHO Explorer - IndoEcon", layout="wide")

st.title("🏥 WHO (World Health Organization) - Modal Manusia & Kesehatan")
st.markdown(
    "Eksplorasi seluruh indikator kesehatan publik dan modal manusia (*human capital*) Indonesia langsung dari "
    "**Direktori Utama WHO Global Health Observatory (GHO) API** secara *real-time* (*100% Live API Dinamis*)."
)

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

# =============================================================================
# 1. TARIK DIREKTORI INDIKATOR AKTIF LANGSUNG DARI SERVER WHO
# =============================================================================
@st.cache_data(ttl=86400, show_spinner=False)
def get_who_indicators():
    try:
        res = requests.get("https://ghoapi.azureedge.net/api/Indicator", headers=HEADERS, timeout=20)
        if res.status_code == 200:
            data = res.json().get("value", [])
            mapping = {}
            for item in data:
                code = item.get("IndicatorCode")
                name = item.get("IndicatorName")
                if code and name:
                    mapping[name] = code
            return mapping
    except Exception:
        pass
    return {}

with st.spinner("Menghubungkan ke direktori pusat WHO untuk memuat daftar indikator aktif..."):
    indicator_dict = get_who_indicators()

if not indicator_dict:
    st.error("Gagal terhubung ke direktori utama server WHO. Pastikan koneksi internet stabil.")
    st.stop()

st.subheader("1. Pemilihan Indikator Dinamis WHO")

# Kotak Pencarian & Pilihan Indikator Berbasis Live Directory WHO
search_term = st.text_input("🔍 Cari Indikator Kesehatan (ketik kata kunci, misal: Mortality, Hospital, Stunting, Life):", "")

filtered_options = [
    name for name in indicator_dict.keys()
    if not search_term.strip() or search_term.lower() in name.lower()
]

if not filtered_options:
    st.warning("Tidak ditemukan indikator yang cocok dengan kata kunci tersebut.")
    st.stop()

selected_indicator_name = st.selectbox(
    f"Pilih dari {len(filtered_options)} Indikator Aktif Tersedia:",
    filtered_options
)

selected_code = indicator_dict[selected_indicator_name]

with st.expander("ℹ️ Metadata Resmi WHO GHO", expanded=False):
    st.markdown(f"**Nama Indikator:** {selected_indicator_name}")
    st.markdown(f"**Kode Seri GHO API:** `{selected_code}`")
    st.markdown(f"**Cakupan Geografis:** Indonesia (`IDN`)")
    st.markdown("🔗 **Sumber Resmi:** [WHO Global Health Observatory](https://www.who.int/data/gho)")

# =============================================================================
# 2. PENARIKAN DATA RUN TUN WAKTU INDONESIA
# =============================================================================
st.subheader("2. Penarikan Data Runtun Waktu Nasional (Indonesia)")
st.caption("Data runtun waktu historis ditarik seketika langsung dari peladen WHO khusus untuk wilayah Indonesia.")

if st.button("📊 Ambil Data WHO (Live API)", type="primary"):
    with st.spinner(f"Menarik data runtun waktu untuk '{selected_indicator_name}'..."):
        api_url = f"https://ghoapi.azureedge.net/api/{selected_code}"
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
                    
                    # Saring agregat jenis kelamin umum jika tersedia
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
                    df_raw = pd.DataFrame(records)
                    df_who = df_raw.groupby("Tahun", as_index=False)["Nilai"].mean().round(2)
                    df_who = df_who.sort_values(by="Tahun", ascending=True)

                    st.success(f"Berhasil menarik {len(df_who)} observasi tahunan resmi untuk Indonesia dari server WHO!")
                    st.divider()

                    # Tombol Unduh Berkas
                    c1, c2 = st.columns(2)
                    c1.download_button(
                        "📥 Unduh CSV",
                        df_who.to_csv(index=False).encode("utf-8"),
                        f"WHO_Indonesia_{selected_code}.csv",
                        "text/csv"
                    )
                    buf = io.BytesIO()
                    with pd.ExcelWriter(buf, engine="openpyxl") as writer:
                        df_who.to_excel(writer, index=False, sheet_name="WHO Indonesia")
                    c2.download_button(
                        "📊 Unduh Excel (.xlsx)",
                        buf.getvalue(),
                        f"WHO_Indonesia_{selected_code}.xlsx",
                        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                    )

                    # Visualisasi Plotly Interaktif
                    fig = go.Figure()
                    fig.add_trace(go.Scatter(
                        x=df_who["Tahun"],
                        y=df_who["Nilai"],
                        mode="lines+markers",
                        name="Indonesia (WHO GHO)",
                        line=dict(width=2.8, color="#0093D5"),
                        marker=dict(size=7),
                        hovertemplate="Tahun %{x}<br>Nilai: %{y:,.2f}<extra></extra>"
                    ))
                    fig.update_layout(
                        xaxis=dict(title="Tahun", tickmode="linear"),
                        yaxis=dict(title="Nilai Indikator"),
                        hovermode="x unified",
                        margin=dict(l=20, r=20, t=30, b=20)
                    )
                    st.plotly_chart(fig, use_container_width=True)

                    with st.expander("📋 Tabel Runtun Waktu Lengkap"):
                        st.dataframe(df_who.sort_values(by="Tahun", ascending=False), use_container_width=True)
                else:
                    st.warning("Server WHO merespons, namun catatan observasi runtun waktu untuk Indonesia belum tersedia pada indikator ini.")
            else:
                st.error(f"Gagal menghubungi server WHO (Kode Status HTTP: {res.status_code}).")
        except Exception as e:
            st.error(f"Terjadi kesalahan saat memproses data WHO: {e}")

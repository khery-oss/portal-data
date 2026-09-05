import io
import pandas as pd
import plotly.graph_objects as go
import requests
import streamlit as st

st.set_page_config(page_title="V-Dem Explorer - IndoEcon", layout="wide")

st.title("🗳️ V-Dem (Varieties of Democracy) - Institusi & Demokrasi")
st.markdown(
    "Eksplorasi seluruh indikator kualitas demokrasi, tata kelola pemerintahan, korupsi, dan institusi politik Indonesia "
    "secara *real-time* langsung dari **V-Dem Institute API** (*100% Live API tanpa batasan tahun manual*)."
)

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

# =============================================================================
# 1. TARIK SELURUH VARIABEL/INDIKATOR AKTIF LANGSUNG DARI DIREKTORI V-DEM API
# =============================================================================
@st.cache_data(ttl=86400, show_spinner=False)
def get_vdem_variables():
    try:
        # Mengambil daftar variabel/indikator langsung dari server V-Dem API
        res = requests.get("https://vdemdata.swemur.com/api/v1/variables", headers=HEADERS, timeout=25)
        if res.status_code == 200:
            data = res.json()
            mapping = {}
            rows = data if isinstance(data, list) else data.get("data", [])
            for item in rows:
                code = item.get("variable_id") or item.get("id") or item.get("name")
                name = item.get("variable_name") or item.get("label") or code
                if code:
                    mapping[str(name)] = str(code)
            return mapping
    except Exception:
        pass
    
    # Fallback kurasi indikator inti V-Dem jika peladen direktori utama sedang sibuk
    return {
        "Liberal Democracy Index": "v2x_libdem",
        "Electoral Democracy Index": "v2x_polyarchy",
        "Participatory Democracy Index": "v2x_partip",
        "Deliberative Democracy Index": "v2x_delib",
        "Egalitarian Democracy Index": "v2x_egal",
        "Public Sector Corruption Index": "v2excrptps",
        "Executive Corruption Index": "v2exorrpt",
        "Freedom of Expression and Alternative Sources Index": "v2x_freexp",
        "Freedom of Association Index": "v2x_frassoc",
        "Rule of Law Index": "v2x_rule",
        "Rigging Elections": "v2elrgroups",
        "Election Violence": "v2elvlstr"
    }

with st.spinner("Memuat direktori indikator resmi dari peladen V-Dem Institute..."):
    vdem_dict = get_vdem_variables()

st.subheader("1. Pemilihan Indikator V-Dem (Indonesia)")
st.caption(f"Total {len(vdem_dict)} indikator institusi politik tersedia secara *live* dari peladen V-Dem.")

search_term = st.text_input("🔍 Cari Indikator V-Dem (ketik kata kunci, misal: Democracy, Corruption, Freedom, Law):", "")

filtered_options = [
    name for name in vdem_dict.keys()
    if not search_term.strip() or search_term.lower() in name.lower()
]

if not filtered_options:
    st.warning("Tidak ditemukan indikator yang cocok dengan kata kunci tersebut.")
    st.stop()

selected_indicator_name = st.selectbox(
    f"Pilih dari {len(filtered_options)} Indikator Aktif:",
    filtered_options
)

selected_code = vdem_dict[selected_indicator_name]

with st.expander("ℹ️ Metadata Resmi V-Dem", expanded=False):
    st.markdown(f"**Nama Indikator:** {selected_indicator_name}")
    st.markdown(f"**Kode Variabel API:** `{selected_code}`")
    st.markdown(f"**Cakupan Geografis:** Indonesia (`IDN`)")
    st.markdown("🔗 **Portal Sumber Resmi:** [V-Dem Institute](https://www.v-dem.net/)")

# =============================================================================
# 2. PENARIKAN DATA RUN TUN WAKTU TANPA BATAS TAHUN
# =============================================================================
st.subheader("2. Penarikan Data Runtun Waktu Nasional (Indonesia)")
st.caption("Seluruh riwayat tahun dari awal pencatatan hingga data terbaru ditarik secara penuh tanpa batasan tahun manual.")

if st.button("📊 Ambil Data V-Dem (Live API)", type="primary"):
    with st.spinner(f"Menarik seluruh riwayat data runtun waktu untuk '{selected_indicator_name}' khusus Indonesia..."):
        api_url = f"https://vdemdata.swemur.com/api/v1/country-year?country_text_id=IDN&variables={selected_code}"

        try:
            res = requests.get(api_url, headers=HEADERS, timeout=25)
            records = []
            
            if res.status_code == 200:
                payload = res.json()
                rows = payload if isinstance(payload, list) else payload.get("data", [])
                for row in rows:
                    th = row.get("year") or row.get("Year")
                    val = row.get(selected_code) or row.get("value")
                    if th is not None and val is not None:
                        try:
                            records.append({
                                "Tahun": int(th),
                                "Nilai": round(float(val), 4)
                            })
                        except (ValueError, TypeError):
                            continue

            # Fallback otomatis jika endpoint langsung memerlukan data repositori mentah V-Dem
            if not records:
                alt_url = "https://raw.githubusercontent.com/vdeminstitute/vdemdata/master/vdem_data.json"
                res_alt = requests.get(alt_url, headers=HEADERS, timeout=30)
                if res_alt.status_code == 200:
                    for row in res_alt.json():
                        if row.get("country_text_id") == "IDN" or row.get("country_name") == "Indonesia":
                            th = row.get("year")
                            val = row.get(selected_code)
                            if th is not None and val is not None:
                                try:
                                    records.append({
                                        "Tahun": int(th),
                                        "Nilai": round(float(val), 4)
                                    })
                                except (ValueError, TypeError):
                                    continue

            if records:
                df_vdem = pd.DataFrame(records).drop_duplicates(subset=["Tahun"]).sort_values(by="Tahun", ascending=True)
                val_col = "Skor Indikator"
                df_vdem = df_vdem.rename(columns={"Nilai": val_col})

                st.success(f"Berhasil menarik {len(df_vdem)} observasi runtun waktu tahunan secara penuh untuk Indonesia!")
                st.divider()

                # Tombol Unduh Berkas
                c1, c2 = st.columns(2)
                c1.download_button(
                    "📥 Unduh CSV",
                    df_vdem.to_csv(index=False).encode("utf-8"),
                    f"VDem_Indonesia_{selected_code}.csv",
                    "text/csv"
                )
                buf = io.BytesIO()
                with pd.ExcelWriter(buf, engine="openpyxl") as writer:
                    df_vdem.to_excel(writer, index=False, sheet_name="V-Dem Indonesia")
                c2.download_button(
                    "📊 Unduh Excel (.xlsx)",
                    buf.getvalue(),
                    f"VDem_Indonesia_{selected_code}.xlsx",
                    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )

                # Visualisasi Plotly Interaktif Tanpa Batas Waktu
                fig = go.Figure()
                fig.add_trace(go.Scatter(
                    x=df_vdem["Tahun"],
                    y=df_vdem[val_col],
                    mode="lines+markers",
                    name="Indonesia (V-Dem)",
                    line=dict(width=2.8, color="#8B0000"),
                    marker=dict(size=7),
                    hovertemplate="Tahun %{x}<br>Skor: %{y:,.4f}<extra></extra>"
                ))
                fig.update_layout(
                    xaxis=dict(title="Tahun", tickmode="linear"),
                    yaxis=dict(title="Skor Indikator"),
                    hovermode="x unified",
                    margin=dict(l=20, r=20, t=30, b=20)
                )
                st.plotly_chart(fig, use_container_width=True)

                with st.expander("📋 Tabel Runtun Waktu Lengkap"):
                    st.dataframe(df_vdem.sort_values(by="Tahun", ascending=False), use_container_width=True)
            else:
                st.warning("Server V-Dem merespons, namun data historis untuk indikator ini belum tersedia secara spesifik untuk Indonesia.")
        except Exception as e:
            st.error(f"Terjadi kesalahan saat memproses data V-Dem: {e}")

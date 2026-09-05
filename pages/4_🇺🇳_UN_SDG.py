import io
import pandas as pd
import plotly.graph_objects as go
import requests
import streamlit as st

st.set_page_config(page_title="UN Data Explorer - Indonesia", layout="wide")

st.title("🇺🇳 United Nations (UN) SDG - Portal Data Indonesia")
st.write(
    "Eksplorasi indikator pembangunan berkelanjutan dan sosio-ekonomi dari **United Nations Statistics Division (UNSD API)** "
    "khusus untuk **Indonesia (M49 Code: 360)** secara langsung (*100% real-time live API*)."
)

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

# 1. Pilihan Mode Tampilan
mode = st.radio(
    "Pilih Mode Tampilan:",
    ["⭐ Indikator Utama Sosio-Ekonomi (Langsung Siap)", "🔍 Jelajahi Seluruh Katalog PBB (Pencarian Bebas)"],
    horizontal=True
)

# DAFTAR KOMPILASI SOSIO-EKONOMI UTAMA INDONESIA (Tanpa Perlu Loading Berat)
POPULAR_UN_SERIES = {
    "Annual Growth Rate of Real GDP per Employed Person (%)": {
        "code": "SL_EMP_PCAP", "goal": "Goal 8: Pekerjaan Layak & Pertumbuhan", "unit": "%",
        "desc": "Laju pertumbuhan tahunan PDB riil per tenaga kerja yang bekerja (produktivitas tenaga kerja)."
    },
    "Annual Growth Rate of Real GDP per Capita (%)": {
        "code": "NY_GDP_PCAP", "goal": "Goal 8: Pekerjaan Layak & Pertumbuhan", "unit": "%",
        "desc": "Laju pertumbuhan tahunan Produk Domestik Bruto riil per kapita."
    },
    "Unemployment Rate (% of Total Labor Force)": {
        "code": "SL_TLF_UEM", "goal": "Goal 8: Pekerjaan Layak & Pertumbuhan", "unit": "%",
        "desc": "Tingkat pengangguran terbuka nasional resmi berdasarkan pemantauan ILO/PBB."
    },
    "Proportion of Youth Not in Education, Employment or Training (NEET) (%)": {
        "code": "SL_TLF_NEET", "goal": "Goal 8: Pekerjaan Layak & Pertumbuhan", "unit": "%",
        "desc": "Persentase generasi muda (usia 15-24) yang tidak bersekolah, bekerja, atau mengikuti pelatihan."
    },
    "Proportion of Population Below International Poverty Line (%)": {
        "code": "SI_POV_DAY1", "goal": "Goal 1: Pengentasan Kemiskinan", "unit": "%",
        "desc": "Persentase penduduk yang hidup di bawah garis kemiskinan ekstrem internasional."
    },
    "Income Share Held by Bottom 40% of Population (%)": {
        "code": "SI_DST_040P", "goal": "Goal 10: Penurunan Kesenjangan", "unit": "%",
        "desc": "Pangsa pendapatan nasional yang dinikmati oleh 40% penduduk terbawah (indikator ketimpangan)."
    },
    "Manufacturing Value Added as Proportion of GDP (%)": {
        "code": "NV_IND_MANF", "goal": "Goal 9: Industri & Inovasi", "unit": "% of GDP",
        "desc": "Nilai tambah sektor industri manufaktur sebagai proporsi dari total PDB nasional."
    },
    "Renewable Energy Share in Total Final Energy Consumption (%)": {
        "code": "EG_FEC_RNEW", "goal": "Goal 7: Energi Bersih", "unit": "%",
        "desc": "Pangsa energi baru terbarukan dalam total konsumsi energi nasional."
    },
    "Carbon Dioxide Emissions per Unit of Value Added (kg CO2)": {
        "code": "EN_ATM_CO2MVA", "goal": "Goal 9: Industri & Inovasi", "unit": "kg CO2 / USD",
        "desc": "Intensitas emisi karbon dioksida per unit nilai tambah manufaktur."
    }
}

selected_code = None
selected_title = None

if mode == "⭐ Indikator Utama Sosio-Ekonomi (Langsung Siap)":
    st.subheader("1. Pemilihan Indikator Sosio-Ekonomi")
    selected_title = st.selectbox("Pilih Indikator:", list(POPULAR_UN_SERIES.keys()))
    meta = POPULAR_UN_SERIES[selected_title]
    selected_code = meta["code"]
    satuan_display = meta["unit"]
    deskripsi_display = meta["desc"]
    goal_display = meta["goal"]

else:
    st.subheader("1. Pencarian di Seluruh Katalog PBB")
    
    # Hanya jalankan pemanggilan ke server PBB saat tab pencarian ini dibuka
    @st.cache_data(ttl=86400)
    def fetch_un_catalog():
        url = "https://unstats.un.org/sdgapi/v1/sdg/Series/List?allparams=false"
        try:
            res = requests.get(url, headers=HEADERS, timeout=12)
            if res.status_code == 200:
                data = res.json()
                return [
                    {
                        "code": item.get("code"),
                        "description": item.get("description", ""),
                        "goal": f"Goal {', '.join(item.get('goal', []))}" if item.get("goal") else "Umum"
                    }
                    for item in data if item.get("code") and item.get("description")
                ]
        except Exception:
            pass
        return []

    with st.spinner("Mengambil daftar katalog dari PBB..."):
        all_un_catalog = fetch_un_catalog()

    if all_un_catalog:
        query_un = st.text_input(
            "Ketik kata kunci (misal: 'poverty', 'gdp', 'water', 'forest', 'health'):",
            value="gdp"
        ).strip()

        if query_un:
            tokens = query_un.lower().split()
            results = [
                s for s in all_un_catalog
                if all(token in s["description"].lower() or token in s["code"].lower() for token in tokens)
            ]
            if results:
                st.success(f"Ditemukan {len(results)} indikator terkait di database PBB!")
                selected_item = st.selectbox(
                    "Pilih Indikator:",
                    options=results,
                    format_func=lambda x: f"[{x['goal']}] {x['description']}"
                )
                selected_code = selected_item["code"]
                selected_title = selected_item["description"]
                satuan_display = "Nilai Observasi"
                deskripsi_display = selected_item["description"]
                goal_display = selected_item["goal"]
            else:
                st.warning("Tidak ada indikator yang cocok.")
    else:
        st.warning("Koneksi katalog global PBB sedang lambat. Gunakan tab 'Indikator Utama Sosio-Ekonomi' untuk akses cepat.")

# 2. Penarikan Data Runtun Waktu
if selected_code:
    with st.expander("ℹ️ Metadata Resmi PBB (UNSD)", expanded=False):
        st.markdown(f"**Nama Indikator:** {selected_title}")
        st.markdown(f"**Target SDG:** `{goal_display}`")
        st.markdown(f"**UN Series Code:** `{selected_code}`")
        st.markdown(f"**Kode Negara PBB:** `360 (Indonesia)`")
        st.markdown(f"**Definisi:**\n{deskripsi_display}")
        st.markdown("🔗 **Sumber Data:** [UNSD Global SDG Database Portal](https://unstats.un.org/sdgs/dataportal)")

    if st.button("📊 Ambil Data PBB Indonesia", type="primary"):
        with st.spinner(f"Menarik runtun waktu resmi untuk seri {selected_code}..."):
            post_url = "https://unstats.un.org/sdgapi/v1/sdg/Series/Data"
            payload = {"seriesCodes": [selected_code], "geoAreaCodes": [360]}
            
            try:
                res = requests.post(post_url, json=payload, headers=HEADERS, timeout=15)
                records = []
                
                if res.status_code == 200:
                    data_json = res.json().get("data", [])
                    for item in data_json:
                        thn = item.get("timePeriodStart")
                        val = item.get("value")
                        if thn and val is not None:
                            try:
                                records.append({
                                    "Tahun": int(thn),
                                    f"Nilai ({satuan_display})": round(float(val), 2)
                                })
                            except (ValueError, TypeError):
                                continue

                if records:
                    df_un = pd.DataFrame(records).drop_duplicates(subset=["Tahun"]).sort_values(by="Tahun", ascending=True)
                    val_col = f"Nilai ({satuan_display})"

                    st.success(f"Berhasil menarik {len(df_un)} observasi tahunan langsung dari server PBB!")
                    st.divider()

                    c1, c2 = st.columns(2)
                    c1.download_button(
                        "📥 Unduh CSV",
                        df_un.to_csv(index=False).encode("utf-8"),
                        f"UN_SDG_{selected_code}_IDN.csv",
                        "text/csv"
                    )
                    buf = io.BytesIO()
                    with pd.ExcelWriter(buf, engine="openpyxl") as writer:
                        df_un.to_excel(writer, index=False, sheet_name="UN Data")
                    c2.download_button(
                        "📊 Unduh Excel (.xlsx)",
                        buf.getvalue(),
                        f"UN_SDG_{selected_code}_IDN.xlsx",
                        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                    )

                    fig = go.Figure()
                    fig.add_trace(go.Scatter(
                        x=df_un["Tahun"],
                        y=df_un[val_col],
                        mode="lines+markers",
                        name="Indonesia (UN SDGs)",
                        line=dict(width=2.5, color="#009edb"),
                        hovertemplate=f"Tahun %{{x}}<br>Nilai: %{{y}}<extra></extra>"
                    ))
                    fig.update_layout(
                        xaxis=dict(title="Tahun", tickmode="linear"),
                        yaxis=dict(title=satuan_display),
                        hovermode="x unified",
                        margin=dict(l=20, r=20, t=40, b=20)
                    )
                    st.plotly_chart(fig, use_container_width=True)

                    with st.expander("📋 Tabel Data Runtun Waktu Lengkap"):
                        st.dataframe(df_un.sort_values(by="Tahun", ascending=False), use_container_width=True)
                else:
                    st.warning("Observasi runtun waktu untuk indikator ini belum dilaporkan atau sedang dalam proses pembaruan di server PBB.")
            except Exception as e:
                st.error(f"Gagal menghubungi server PBB: {e}")

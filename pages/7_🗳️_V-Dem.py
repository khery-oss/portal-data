import io
import pandas as pd
import plotly.graph_objects as go
import requests
import streamlit as st

st.set_page_config(page_title="V-Dem Explorer - IndoEcon", layout="wide")

st.title("🗳️ V-Dem (Varieties of Democracy) - Institusi & Demokrasi")
st.markdown(
    "Eksplorasi indeks kualitas demokrasi, tata kelola pemerintahan, korupsi, dan institusi politik Indonesia resmi dari "
    "**V-Dem Institute REST API** secara *real-time* (*100% Live API Streaming*)."
)

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

# KATALOG INDIKATOR UTAMA V-Dem UNTUK INDONESIA (V-Dem Country-Year Dataset API)
VDEM_CATALOG = {
    # --- 1. Demokrasi & Rezim ---
    "Indeks Demokrasi Liberal (Liberal Democracy Index, v2x_libdem)": {
        "code": "v2x_libdem", "kategori": "1. Demokrasi & Rezim", "unit": "Skor (0 - 1)",
        "desc": "Mengukur perlindungan hak minoritas, supremasi hukum, dan konstrain eksekutif terhadap kekuasaan."
    },
    "Indeks Demokrasi Elektoral (Electoral Democracy Index, v2x_polyarchy)": {
        "code": "v2x_polyarchy", "kategori": "1. Demokrasi & Rezim", "unit": "Skor (0 - 1)",
        "desc": "Mengukur tingkat kebebasan pemilu, hak pilih universal, dan kebebasan berorganisasi."
    },
    "Indeks Demokrasi Partisipatif (Participatory Democracy Index, v2x_partip)": {
        "code": "v2x_partip", "kategori": "1. Demokrasi & Rezim", "unit": "Skor (0 - 1)",
        "desc": "Mengukur tingkat partisipasi warga negara melalui lembaga lokal dan langsung."
    },
    "Indeks Demokrasi Deliberatif (Deliberative Democracy Index, v2x_delib)": {
        "code": "v2x_delib", "kategori": "1. Demokrasi & Rezim", "unit": "Skor (0 - 1)",
        "desc": "Mengukur sejauh mana proses politik didasarkan pada argumen publik dan kepentingan umum."
    },

    # --- 2. Korupsi & Akuntabilitas ---
    "Indeks Korupsi Publik (Public Sector Corruption Index, v2excrptps)": {
        "code": "v2excrptps", "kategori": "2. Korupsi & Tata Kelola", "unit": "Skor (0 - 1)",
        "desc": "Mengukur seberapa besar pejabat publik menggelapkan dana atau menerima suap di sektor publik."
    },
    "Indeks Korupsi Eksekutif (Executive Corruption Index, v2exorrpt)": {
        "code": "v2exorrpt", "kategori": "2. Korupsi & Tata Kelola", "unit": "Skor (0 - 1)",
        "desc": "Mengukur korupsi yang melibatkan pemegang kekuasaan eksekutif tertinggi dan stafnya."
    },
    "Akuntabilitas Publik (Vertical Accountability Index, v2x_veracc)": {
        "code": "v2x_veracc", "kategori": "2. Korupsi & Tata Kelola", "unit": "Skor (0 - 1)",
        "desc": "Mengukur kemampuan masyarakat dalam meminta pertanggungjawaban penguasa melalui pemilu dan kebebasan media."
    },

    # --- 3. Kebebasan Sipil & Media ---
    "Indeks Kebebasan Pers (Freedom of Expression & Alternative Sources, v2x_freexp)": {
        "code": "v2x_freexp", "kategori": "3. Kebebasan Sipil & Media", "unit": "Skor (0 - 1)",
        "desc": "Mengukur kebebasan media cetak/elektronik, kebebasan akademis, dan kebebasan berekspresi warga."
    },
    "Indeks Kebebasan Berorganisasi & Berkumpul (v2x_frassoc)": {
        "code": "v2x_frassoc", "kategori": "3. Kebebasan Sipil & Media", "unit": "Skor (0 - 1)",
        "desc": "Mengukur kebebasan partai politik, serikat pekerja, dan organisasi masif sipil."
    },
    "Rule of Law / Supremasi Hukum (v2x_rule)": {
        "code": "v2x_rule", "kategori": "3. Kebebasan Sipil & Media", "unit": "Skor (0 - 1)",
        "desc": "Mengukur prediktabilitas penegakan hukum, independensi peradilan, dan kepatuhan hukum."
    }
}

# =============================================================================
# 1. KONTROL PILIHAN INDIKATOR
# =============================================================================
st.subheader("1. Pemilihan Indikator V-Dem")
c_kat, c_ind = st.columns([1.2, 2])

kategori_list = sorted(list(set(v["kategori"] for v in VDEM_CATALOG.values())))
with c_kat:
    kat_pilihan = st.selectbox("Kategori Bidang:", ["Semua Kategori"] + kategori_list)

opsi = [
    k for k, v in VDEM_CATALOG.items()
    if kat_pilihan == "Semua Kategori" or v["kategori"] == kat_pilihan
]

with c_ind:
    nama_indikator = st.selectbox(f"Pilih Indikator ({len(opsi)} Tersedia):", opsi)

meta = VDEM_CATALOG[nama_indikator]
code_id = meta["code"]

with st.expander("ℹ️ Definisi & Metadata Resmi V-Dem", expanded=False):
    st.markdown(f"**Indikator V-Dem:** {nama_indikator}")
    st.markdown(f"**Kode Seri:** `{code_id}`")
    st.markdown(f"**Satuan Pengukuran:** `{meta['unit']}`")
    st.markdown(f"**Cakupan Negara:** Indonesia (IDN / Country Code: 133)")
    st.markdown(f"**Deskripsi Metodologi:**\n{meta['desc']}")
    st.markdown("🔗 **Portal Sumber Resmi:** [V-Dem Institute](https://www.v-dem.net/)")

# =============================================================================
# 2. PENARIKAN DATA LIVE API V-Dem (INDONESIA)
# =============================================================================
st.subheader("2. Penarikan Data Runtun Waktu Nasional (Indonesia)")
st.caption("Seluruh riwayat tahun dari basis data V-Dem Institute akan ditarik secara langsung dan real-time.")

if st.button("📊 Ambil Data V-Dem (Live API)", type="primary"):
    with st.spinner(f"Menghubungi peladen V-Dem API untuk seri '{nama_indikator}'..."):
        # V-Dem menyediakan akses publik data dalam format JSON terstruktur untuk Indonesia (IDN / cowcode 133)
        api_url = f"https://vdemdata.swemur.com/api/v1/country-year?country_text_id=IDN&variables={code_id}"

        try:
            res = requests.get(api_url, headers=HEADERS, timeout=25)
            
            records = []
            if res.status_code == 200:
                payload = res.json()
                # Tangani struktur data JSON V-Dem
                rows = payload if isinstance(payload, list) else payload.get("data", [])
                for row in rows:
                    th = row.get("year") or row.get("Year")
                    val = row.get(code_id) or row.get("value")
                    if th is not None and val is not None:
                        try:
                            records.append({
                                "Tahun": int(th),
                                "Nilai": round(float(val), 4)
                            })
                        except (ValueError, TypeError):
                            continue

            # Fallback API publik alternatif jika endpoint utama memerlukan penyesuaian header
            if not records:
                alt_url = f"https://raw.githubusercontent.com/vdeminstitute/vdemdata/master/vdem_data.json"
                # Menggunakan fallback penarikan data langsung dari repositori resmi V-Dem GitHub
                res_alt = requests.get(alt_url, headers=HEADERS, timeout=30)
                if res_alt.status_code == 200:
                    all_data = res_alt.json()
                    for row in all_data:
                        if row.get("country_text_id") == "IDN" or row.get("country_name") == "Indonesia":
                            th = row.get("year")
                            val = row.get(code_id)
                            if th is not None and val is not None:
                                try:
                                    records.append({
                                        "Tahun": int(th),
                                        "Nilai": round(float(val), 4)
                                    })
                                except (ValueError, TypeError):
                                    continue

            if records:
                val_col = f"Skor ({meta['unit']})"
                df_vdem = pd.DataFrame(records).drop_duplicates(subset=["Tahun"]).sort_values(by="Tahun", ascending=True)
                df_vdem = df_vdem.rename(columns={"Nilai": val_col})

                st.success(f"Berhasil menarik {len(df_vdem)} observasi tahunan institusi politik Indonesia dari V-Dem!")
                st.divider()

                # Tombol Unduh Berkas
                c1, c2 = st.columns(2)
                c1.download_button(
                    "📥 Unduh CSV",
                    df_vdem.to_csv(index=False).encode("utf-8"),
                    f"VDem_Indonesia_{code_id}.csv",
                    "text/csv"
                )
                buf = io.BytesIO()
                with pd.ExcelWriter(buf, engine="openpyxl") as writer:
                    df_vdem.to_excel(writer, index=False, sheet_name="V-Dem Indonesia")
                c2.download_button(
                    "📊 Unduh Excel (.xlsx)",
                    buf.getvalue(),
                    f"VDem_Indonesia_{code_id}.xlsx",
                    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )

                # Visualisasi Plotly Interaktif
                fig = go.Figure()
                fig.add_trace(go.Scatter(
                    x=df_vdem["Tahun"],
                    y=df_vdem[val_col],
                    mode="lines+markers",
                    name="Indonesia (V-Dem Institute)",
                    line=dict(width=2.8, color="#8B0000"),
                    marker=dict(size=7),
                    hovertemplate=f"Tahun %{{x}}<br>Skor: %{{y:,.4f}}<extra></extra>"
                ))
                fig.update_layout(
                    xaxis=dict(title="Tahun", tickmode="linear"),
                    yaxis=dict(title=meta["unit"]),
                    hovermode="x unified",
                    margin=dict(l=20, r=20, t=30, b=20)
                )
                st.plotly_chart(fig, use_container_width=True)

                with st.expander("📋 Tabel Runtun Waktu Lengkap"):
                    st.dataframe(df_vdem.sort_values(by="Tahun", ascending=False), use_container_width=True)
            else:
                st.warning("Data untuk indikator ini belum merespons dengan benar. Silakan coba beberapa saat lagi.")
        except Exception as e:
            st.error(f"Terjadi kesalahan saat memproses data V-Dem: {e}")

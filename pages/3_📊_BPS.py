import io
import pandas as pd
import plotly.graph_objects as go
import requests
import streamlit as st

st.set_page_config(page_title="BPS Live Data - IndoEcon Explorer", layout="wide")

st.title("📊 Portal Data BPS (Live WebAPI BPS)")
st.write(
    "Data indikator strategis nasional yang ditarik **secara langsung (*real-time*)** dari server "
    "**WebAPI Badan Pusat Statistik (BPS)**."
)

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

api_key = st.secrets.get("BPS_APP_ID") or st.secrets.get("BPS_API_KEY")
if not api_key:
    st.error("⚠️ Key BPS belum disetel di Streamlit Secrets (`BPS_APP_ID`).")
    st.stop()

DOMAIN = "0000"  # Agregat Nasional

# PEMETAAN 32 INDIKATOR STRATEGIS RESMI KE VAR_ID RESMI BPS
BPS_LIVE_INDICATORS = {
    # 1. Kemiskinan & Kesejahteraan
    "Persentase Penduduk Miskin (P0)": {"var_id": "23", "kategori": "1. Kemiskinan & Kesejahteraan", "unit": "%"},
    "Garis Kemiskinan (Rupiah/Kapita/Bulan)": {"var_id": "182", "kategori": "1. Kemiskinan & Kesejahteraan", "unit": "Rp"},
    "Jumlah Penduduk Miskin": {"var_id": "24", "kategori": "1. Kemiskinan & Kesejahteraan", "unit": "Ribu Jiwa"},
    "Indeks Kedalaman Kemiskinan (P1)": {"var_id": "25", "kategori": "1. Kemiskinan & Kesejahteraan", "unit": "Indeks"},
    "Indeks Keparahan Kemiskinan (P2)": {"var_id": "27", "kategori": "1. Kemiskinan & Kesejahteraan", "unit": "Indeks"},
    "Gini Ratio": {"var_id": "185", "kategori": "1. Kemiskinan & Kesejahteraan", "unit": "Koefisien"},

    # 2. Pendidikan & SDM
    "Indeks Pembangunan Manusia (IPM)": {"var_id": "26", "kategori": "2. Pendidikan & SDM", "unit": "Poin Indeks"},
    "Harapan Lama Sekolah (HLS)": {"var_id": "41", "kategori": "2. Pendidikan & SDM", "unit": "Tahun"},
    "Rata-rata Lama Sekolah (RLS)": {"var_id": "42", "kategori": "2. Pendidikan & SDM", "unit": "Tahun"},
    "Angka Harapan Hidup (AHH)": {"var_id": "40", "kategori": "2. Pendidikan & SDM", "unit": "Tahun"},
    "Pengeluaran Riil per Kapita yang Disesuaikan": {"var_id": "43", "kategori": "2. Pendidikan & SDM", "unit": "Ribu Rp"},
    "Angka Melek Huruf Penduduk 15+": {"var_id": "103", "kategori": "2. Pendidikan & SDM", "unit": "%"},
    "Angka Partisipasi Murni (APM) SD": {"var_id": "120", "kategori": "2. Pendidikan & SDM", "unit": "%"},
    "Angka Partisipasi Murni (APM) SMP": {"var_id": "121", "kategori": "2. Pendidikan & SDM", "unit": "%"},
    "Angka Partisipasi Murni (APM) SMA": {"var_id": "122", "kategori": "2. Pendidikan & SDM", "unit": "%"},

    # 3. Ketenagakerjaan
    "Tingkat Pengangguran Terbuka (TPT)": {"var_id": "6", "kategori": "3. Ketenagakerjaan", "unit": "%"},
    "Tingkat Partisipasi Angkatan Kerja (TPAK)": {"var_id": "5", "kategori": "3. Ketenagakerjaan", "unit": "%"},
    "Penduduk Bekerja Menurut Lapangan Pekerjaan Utama": {"var_id": "326", "kategori": "3. Ketenagakerjaan", "unit": "Orang"},
    "Persentase Pekerja Formal": {"var_id": "327", "kategori": "3. Ketenagakerjaan", "unit": "%"},
    "Rata-rata Upah/Gaji Bersih Pekerja": {"var_id": "330", "kategori": "3. Ketenagakerjaan", "unit": "Rupiah"},

    # 4. Makroekonomi, Harga & Perdagangan
    "Laju Pertumbuhan PDB Riil": {"var_id": "104", "kategori": "4. Makroekonomi & PDB", "unit": "%"},
    "PDB Atas Dasar Harga Konstan (ADHK)": {"var_id": "105", "kategori": "4. Makroekonomi & PDB", "unit": "Miliar Rp"},
    "PDB Atas Dasar Harga Berlaku (ADHB)": {"var_id": "106", "kategori": "4. Makroekonomi & PDB", "unit": "Miliar Rp"},
    "PDB per Kapita": {"var_id": "107", "kategori": "4. Makroekonomi & PDB", "unit": "Juta Rp"},
    "Indeks Harga Konsumen (IHK)": {"var_id": "2", "kategori": "4. Makroekonomi & PDB", "unit": "Poin Indeks"},
    "Perkembangan Nilai Ekspor": {"var_id": "203", "kategori": "4. Makroekonomi & PDB", "unit": "Juta USD"},
    "Perkembangan Nilai Impor": {"var_id": "205", "kategori": "4. Makroekonomi & PDB", "unit": "Juta USD"},

    # 5. Kependudukan, Gender & Sosial
    "Jumlah Penduduk": {"var_id": "12", "kategori": "5. Kependudukan & Sosial", "unit": "Ribu Jiwa"},
    "Laju Pertumbuhan Penduduk": {"var_id": "13", "kategori": "5. Kependudukan & Sosial", "unit": "%"},
    "Rasio Jenis Kelamin": {"var_id": "15", "kategori": "5. Kependudukan & Sosial", "unit": "Rasio"},
    "Indeks Pembangunan Gender (IPG)": {"var_id": "291", "kategori": "5. Kependudukan & Sosial", "unit": "Poin Indeks"},
    "Indeks Pemberdayaan Gender (IDG)": {"var_id": "293", "kategori": "5. Kependudukan & Sosial", "unit": "Poin Indeks"},
}

# ==============================================================================
# 1. Kontrol Pemilihan Indikator
# ==============================================================================
st.subheader("1. Pemilihan Indikator BPS")
col_kat, col_ind = st.columns([1, 1.8])

kategori_list = sorted(list(set(v["kategori"] for v in BPS_LIVE_INDICATORS.values())))
with col_kat:
    pilihan_kategori = st.selectbox("Kategori Bidang:", ["Semua Kategori"] + kategori_list)

opsi_indikator = [
    k for k, v in BPS_LIVE_INDICATORS.items()
    if pilihan_kategori == "Semua Kategori" or v["kategori"] == pilihan_kategori
]

with col_ind:
    selected_name = st.selectbox(f"Nama Indikator ({len(opsi_indikator)} Tersedia):", opsi_indikator)

meta = BPS_LIVE_INDICATORS[selected_name]
selected_var_id = meta["var_id"]

# ==============================================================================
# 2. Filter Rentang Tahun
# ==============================================================================
st.subheader("2. Rentang Tahun")
YEARS = [str(y) for y in range(2000, 2026)]

col_t1, col_t2 = st.columns(2)
with col_t1:
    th_start = st.selectbox("Tahun Mulai:", YEARS, index=YEARS.index("2015"))
with col_t2:
    th_end = st.selectbox("Tahun Selesai:", YEARS, index=YEARS.index("2024"))

if int(th_start) > int(th_end):
    st.error("Tahun mulai tidak boleh melebihi tahun selesai.")
    st.stop()

# ==============================================================================
# 3. Penarikan Data Live dari WebAPI BPS
# ==============================================================================
@st.cache_data(ttl=3600, show_spinner=False)
def fetch_live_bps_data(var_id, y_start, y_end):
    th_code_start = int(y_start) - 1900
    th_code_end = int(y_end) - 1900
    
    # Format range BPS yang valid
    th_param = f"{th_code_start}:{th_code_end}" if th_code_start != th_code_end else str(th_code_start)
    
    url = f"https://webapi.bps.go.id/v1/api/list/model/data/lang/ind/domain/{DOMAIN}/var/{var_id}/th/{th_param}/key/{api_key}/"
    
    try:
        r = requests.get(url, headers=HEADERS, timeout=20)
        res = r.json()
        return res, None
    except Exception as e:
        return None, str(e)

if st.button("🌐 Ambil Data Langsung dari BPS", type="primary"):
    with st.spinner(f"Meminta data resmi BPS untuk '{selected_name}' ({th_start}–{th_end})..."):
        res, err = fetch_live_bps_data(selected_var_id, th_start, th_end)

    if err:
        st.error(f"Gagal koneksi ke WebAPI BPS: {err}")
        st.stop()

    if not res or res.get("status") != "OK" or res.get("data-availability") == "list-not-available":
        st.warning(f"Server BPS belum menyediakan rilis tabel digital untuk '{selected_name}' pada periode {th_start}–{th_end}.")
        st.stop()

    datacontent = res.get("datacontent", {})
    vervar = {str(item["val"]): str(item["label"]) for item in res.get("vervar", [])}
    tahun_dict = {str(item["val"]): str(item["label"]) for item in res.get("tahun", [])}

    records = []
    selected_range_years = [str(y) for y in range(int(th_start), int(th_end) + 1)]

    for cell_key, val in datacontent.items():
        if val is not None:
            k_str = str(cell_key)

            # Ekstraksi label rincian (vervar)
            rincian_lbl = "Nasional"
            for v_val, v_lbl in vervar.items():
                if k_str.startswith(v_val):
                    rincian_lbl = v_lbl
                    break

            # Ekstraksi label tahun
            tahun_lbl = None
            for t_val, t_lbl in tahun_dict.items():
                if t_val in k_str:
                    tahun_lbl = t_lbl
                    break

            th_clean = "".join(filter(str.isdigit, str(tahun_lbl)))[:4] if tahun_lbl else None

            if th_clean and th_clean in selected_range_years:
                try:
                    num_val = float(str(val).replace(",", ".").strip())
                except ValueError:
                    num_val = val

                records.append({
                    "Tahun": th_clean,
                    "Kategori / Rincian": rincian_lbl,
                    "Nilai": num_val
                })

    if records:
        df_raw = pd.DataFrame(records).drop_duplicates()
        df_pivot = df_raw.pivot_table(index="Tahun", columns="Kategori / Rincian", values="Nilai", aggfunc="first").reset_index()

        df_grid = pd.DataFrame({"Tahun": selected_range_years})
        df_final = pd.merge(df_grid, df_pivot, on="Tahun", how="left").sort_values("Tahun")

        st.success(f"Data riil berhasil ditarik dari BPS: **{selected_name}** (Var ID: {selected_var_id})")
        st.caption(f"Satuan Resmi: **{meta['unit']}** | Sumber: **WebAPI Badan Pusat Statistik**")

        st.divider()

        # Visualisasi Grafik
        st.subheader(f"📈 Tren Deret Waktu: {selected_name}")
        fig = go.Figure()

        val_cols = [c for c in df_final.columns if c != "Tahun"]
        for col in val_cols:
            fig.add_trace(go.Scatter(
                x=df_final["Tahun"],
                y=df_final[col],
                mode="lines+markers",
                name=col,
                connectgaps=False,
                hovertemplate=f"Tahun %{{x}}<br>{col}: %{{y}}<extra></extra>"
            ))

        fig.update_layout(
            xaxis=dict(title="Tahun", tickmode="linear"),
            yaxis=dict(title=meta["unit"]),
            hovermode="x unified",
            margin=dict(l=20, r=20, t=40, b=20)
        )
        st.plotly_chart(fig, use_container_width=True)

        # Tabel Data & Ekspor
        st.subheader("📋 Tabel Data Observasi Resmi")
        c_csv, c_xlsx = st.columns(2)
        c_csv.download_button(
            "📥 Unduh CSV",
            df_final.to_csv(index=False).encode("utf-8"),
            f"BPS_Live_{selected_var_id}_{th_start}_{th_end}.csv",
            "text/csv"
        )

        buf = io.BytesIO()
        with pd.ExcelWriter(buf, engine="openpyxl") as writer:
            df_final.to_excel(writer, index=False, sheet_name="Data BPS")
        c_xlsx.download_button(
            "📊 Unduh Excel (.xlsx)",
            buf.getvalue(),
            f"BPS_Live_{selected_var_id}_{th_start}_{th_end}.xlsx",
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

        st.dataframe(df_final.fillna("-"), use_container_width=True)
        st.caption("💡 Tanda strip (-) menandakan data belum dialokasikan pada rilis tahun tersebut.")
    else:
        st.warning("Server BPS merespons status OK, namun tidak ditemukan sel angka pada rentang tahun ini.")

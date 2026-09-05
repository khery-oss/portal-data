import io
import pandas as pd
import plotly.graph_objects as go
import requests
import streamlit as st

st.set_page_config(page_title="BPS Explorer - IndoEcon", layout="wide")

st.title("📊 BPS (Badan Pusat Statistik RI) - Indikator Strategis Nasional")
st.markdown(
    "Eksplorasi indikator sosial-ekonomi resmi Indonesia dari **WebAPI BPS RI** secara *real-time* (*100% Live API*)."
)

# =============================================================================
# MANAJEMEN API KEY (SESUAI POLA FRED)
# =============================================================================
bps_api_key = ""
if "BPS_API_KEY" in st.secrets:
    bps_api_key = st.secrets["BPS_API_KEY"]
else:
    with st.sidebar:
        st.subheader("🔐 Autentikasi BPS WebAPI")
        bps_api_key = st.text_input(
            "Masukkan BPS API Key:",
            type="password",
            help="Masukkan API key resmi BPS Anda. Nilai ini tidak akan disimpan di dalam kode."
        )

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

# =============================================================================
# KATALOG INDIKATOR RESMI BPS (STRUKTUR SERAGAM & AMAN)
# =============================================================================
BPS_CATALOG = {
    # --- 1. Kemiskinan & Ketimpangan ---
    "Persentase Penduduk Miskin Nasional (P0, %)": {
        "var": "23",
        "kategori": "1. Kemiskinan & Ketimpangan",
        "unit": "%",
        "desc": "Persentase penduduk miskin nasional berdasarkan Survei Sosial Ekonomi Nasional (Susenas)."
    },
    "Gini Ratio / Rasio Gini Nasional": {
        "var": "149",
        "kategori": "1. Kemiskinan & Ketimpangan",
        "unit": "Koefisien Gini",
        "desc": "Tingkat ketimpangan pengeluaran agregat penduduk Indonesia (0 = merata sempurna, 1 = timpang sempurna)."
    },
    "Garis Kemiskinan Nasional (Rp/Kapita/Bulan)": {
        "var": "25",
        "kategori": "1. Kemiskinan & Ketimpangan",
        "unit": "Rp/Kapita/Bulan",
        "desc": "Batas minimum rupiah untuk memenuhi kebutuhan dasar makanan dan non-makanan per orang sebulan."
    },

    # --- 2. Ketenagakerjaan ---
    "Tingkat Pengangguran Terbuka (TPT) Nasional (%)": {
        "var": "543",
        "kategori": "2. Ketenagakerjaan",
        "unit": "%",
        "desc": "Persentase jumlah penganggur terhadap total angkatan kerja berdasarkan Sakernas."
    },
    "Tingkat Partisipasi Angkatan Kerja (TPAK) Nasional (%)": {
        "var": "542",
        "kategori": "2. Ketenagakerjaan",
        "unit": "%",
        "desc": "Persentase penduduk usia kerja (15 tahun ke atas) yang aktif secara ekonomi."
    },

    # --- 3. Pembangunan Manusia ---
    "Indeks Pembangunan Manusia (IPM) Nasional": {
        "var": "498",
        "kategori": "3. Pembangunan Manusia",
        "unit": "Indeks",
        "desc": "Capaian komposit derajat kesehatan, taraf pendidikan, dan standar hidup layak."
    },
    "Angka Harapan Hidup saat Lahir (AHH) Nasional": {
        "var": "500",
        "kategori": "3. Pembangunan Manusia",
        "unit": "Tahun",
        "desc": "Perkiraan rata-rata tahun hidup yang dapat dicapai bayi yang baru lahir."
    },
    "Rata-rata Lama Sekolah (RLS) Nasional": {
        "var": "501",
        "kategori": "3. Pembangunan Manusia",
        "unit": "Tahun",
        "desc": "Rata-rata lama bersekolah formal yang ditempuh oleh penduduk usia 25 tahun ke atas."
    }
}

# =============================================================================
# 1. KONTROL PEMILIHAN INDIKATOR
# =============================================================================
st.subheader("1. Pemilihan Indikator Resmi BPS")
col_kat, col_ind = st.columns([1.2, 2])

kategori_list = sorted(list(set(v.get("kategori", "") for v in BPS_CATALOG.values())))

with col_kat:
    pilihan_kategori = st.selectbox("Kategori Bidang:", ["Semua Kategori"] + kategori_list)

opsi = [
    k for k, v in BPS_CATALOG.items()
    if pilihan_kategori == "Semua Kategori" or v.get("kategori") == pilihan_kategori
]

with col_ind:
    selected_name = st.selectbox(f"Nama Indikator ({len(opsi)} Tersedia):", opsi)

meta = BPS_CATALOG[selected_name]

with st.expander("ℹ️ Definisi & Metadata Resmi BPS", expanded=False):
    st.markdown(f"**Nama Indikator:** {selected_name}")
    st.markdown(f"**Variable ID BPS:** `{meta['var']}`")
    st.markdown(f"**Kategori Bidang:** `{meta['kategori']}`")
    st.markdown(f"**Satuan Pengukuran:** `{meta['unit']}`")
    st.markdown(f"**Metodologi / Deskripsi:**\n{meta['desc']}")
    st.markdown("🔗 **Portal Sumber Resmi:** [WebAPI BPS RI](https://webapi.bps.go.id/)")

# =============================================================================
# 2. PENARIKAN DATA LIVE DARI SERVER RESMI BPS
# =============================================================================
st.subheader("2. Penarikan Data Runtun Waktu Nasional")

if not bps_api_key:
    st.warning("⚠️ BPS API Key belum terdeteksi. Silakan simpan di `st.secrets` dengan kunci `BPS_API_KEY` atau masukkan lewat bilah samping.")
else:
    if st.button("📊 Ambil Data BPS Langsung", type="primary"):
        with st.spinner(f"Menghubungi server WebAPI BPS untuk indikator {selected_name}..."):
            api_url = f"https://webapi.bps.go.id/v1/api/list/model/data/lang/ind/domain/0000/var/{meta['var']}/key/{bps_api_key}/"

            try:
                res = requests.get(api_url, headers=HEADERS, timeout=25)
                
                if res.status_code == 200:
                    payload = res.json()
                    
                    if payload.get("data-availability") == "available":
                        vervar_list = payload.get("vervar", [])
                        tahun_list = payload.get("tahun", [])
                        datacontent = payload.get("datacontent", {})

                        # Identifikasi kode entitas nasional INDONESIA
                        id_indonesia = None
                        for v in vervar_list:
                            if "INDONESIA" in str(v.get("label", "")).upper():
                                id_indonesia = str(v.get("val"))
                                break

                        map_tahun = {str(t["val"]): str(t["label"]).strip() for t in tahun_list}

                        records = []
                        for key_code, raw_val in datacontent.items():
                            if raw_val is None:
                                continue
                            try:
                                num_val = float(raw_val)
                            except (ValueError, TypeError):
                                continue

                            # Hanya filter entitas nasional jika vervar tersedia
                            if id_indonesia and not key_code.startswith(id_indonesia):
                                continue

                            for th_id, th_label in map_tahun.items():
                                if th_id in key_code:
                                    try:
                                        th_int = int(th_label[:4])
                                        records.append({"Tahun": th_int, "Nilai": num_val})
                                    except ValueError:
                                        pass
                                    break

                        if records:
                            val_col = f"Nilai ({meta['unit']})"
                            df_raw = pd.DataFrame(records)
                            df_bps = df_raw.groupby("Tahun", as_index=False)["Nilai"].mean().round(2)
                            df_bps = df_bps.rename(columns={"Nilai": val_col}).sort_values(by="Tahun", ascending=True)

                            st.success(f"Berhasil menarik {len(df_bps)} observasi resmi langsung dari WebAPI BPS!")
                            st.divider()

                            # Tombol Unduh Data
                            c1, c2 = st.columns(2)
                            c1.download_button(
                                "📥 Unduh CSV",
                                df_bps.to_csv(index=False).encode("utf-8"),
                                f"BPS_{meta['var']}_Nasional.csv",
                                "text/csv"
                            )
                            buf = io.BytesIO()
                            with pd.ExcelWriter(buf, engine="openpyxl") as writer:
                                df_bps.to_excel(writer, index=False, sheet_name="BPS Data")
                            c2.download_button(
                                "📊 Unduh Excel (.xlsx)",
                                buf.getvalue(),
                                f"BPS_{meta['var']}_Nasional.xlsx",
                                "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                            )

                            # Visualisasi Plotly
                            fig = go.Figure()
                            fig.add_trace(go.Scatter(
                                x=df_bps["Tahun"],
                                y=df_bps[val_col],
                                mode="lines+markers",
                                name="Indonesia",
                                line=dict(width=2.8, color="#00529B"),
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

                            with st.expander("📋 Tabel Data Runtun Waktu Lengkap"):
                                st.dataframe(df_bps.sort_values(by="Tahun", ascending=False), use_container_width=True)
                        else:
                            st.warning("Data observasi nasional untuk variabel ini sedang dalam pembaruan di server BPS.")
                    else:
                        st.warning("Server BPS merespons: data belum tersedia untuk parameter variabel ini.")
                else:
                    st.error(f"Gagal menghubungi server BPS (Status HTTP: {res.status_code}).")
            except Exception as e:
                st.error(f"Terjadi kesalahan koneksi saat memproses data BPS: {e}")

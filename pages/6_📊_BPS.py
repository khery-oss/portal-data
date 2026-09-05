import io
import pandas as pd
import plotly.graph_objects as go
import requests
import streamlit as st

st.set_page_config(page_title="BPS Data Explorer - Badan Pusat Statistik", layout="wide")

st.title("📊 BPS (Badan Pusat Statistik RI) - Data Statistik Nasional & Daerah")
st.write(
    "Eksplorasi indikator sosial-ekonomi strategis Indonesia dari **WebAPI Resmi Badan Pusat Statistik (BPS RI)** "
    "secara langsung (*100% live API*) lintas provinsi dan runtun waktu."
)

# KUNCI API RESMI BPS
BPS_APP_ID = "a94870b1e82c1b3dfdb6d2935df375bc"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

# KATALOG ID VARIABEL RESMI BPS PUSAT (DOMAIN: 0000)
BPS_CATALOG = {
    # --- 1. Kemiskinan & Ketimpangan ---
    "Persentase Penduduk Miskin menurut Provinsi (P0, %)": {
        "var_id": "23", "kategori": "1. Kemiskinan & Ketimpangan", "unit": "%",
        "desc": "Proporsi penduduk yang berada di bawah Garis Kemiskinan resmi BPS per provinsi."
    },
    "Gini Ratio / Rasio Gini menurut Provinsi": {
        "var_id": "149", "kategori": "1. Kemiskinan & Ketimpangan", "unit": "Koefisien Gini",
        "desc": "Ukuran ketimpangan pengeluaran penduduk agregat (skala 0 hingga 1)."
    },
    "Garis Kemiskinan menurut Provinsi (Rupiah/Kapita/Bulan)": {
        "var_id": "25", "kategori": "1. Kemiskinan & Ketimpangan", "unit": "Rp/Kapita/Bulan",
        "desc": "Nilai pengeluaran minimum kebutuhan makanan dan non-makanan per kapita per bulan."
    },
    "Jumlah Penduduk Miskin menurut Provinsi (Ribu Jiwa)": {
        "var_id": "24", "kategori": "1. Kemiskinan & Ketimpangan", "unit": "Ribu Jiwa",
        "desc": "Total populasi penduduk yang hidup di bawah garis kemiskinan."
    },

    # --- 2. Ketenagakerjaan (Sakernas) ---
    "Tingkat Pengangguran Terbuka (TPT) menurut Provinsi (%)": {
        "var_id": "543", "kategori": "2. Ketenagakerjaan (Sakernas)", "unit": "%",
        "desc": "Persentase jumlah penganggur terhadap jumlah angkatan kerja resmi."
    },
    "Tingkat Partisipasi Angkatan Kerja (TPAK) menurut Provinsi (%)": {
        "var_id": "542", "kategori": "2. Ketenagakerjaan (Sakernas)", "unit": "%",
        "desc": "Persentase penduduk usia kerja yang aktif secara ekonomi (bekerja atau mencari kerja)."
    },

    # --- 3. Indeks Pembangunan Manusia (IPM) ---
    "Indeks Pembangunan Manusia (IPM) menurut Provinsi": {
        "var_id": "498", "kategori": "3. Pembangunan Manusia (IPM)", "unit": "Indeks",
        "desc": "Pencapaian pembangunan manusia berbasis kesehatan, pendidikan, dan standar hidup layak."
    },
    "Angka Harapan Hidup saat Lahir (AHH) menurut Provinsi (Tahun)": {
        "var_id": "500", "kategori": "3. Pembangunan Manusia (IPM)", "unit": "Tahun",
        "desc": "Rata-rata perkiraan banyak tahun yang dapat ditempuh oleh seseorang sejak lahir."
    },
    "Rata-rata Lama Sekolah (RLS) menurut Provinsi (Tahun)": {
        "var_id": "501", "kategori": "3. Pembangunan Manusia (IPM)", "unit": "Tahun",
        "desc": "Jumlah tahun yang dihabiskan oleh penduduk usia 25 tahun ke atas dalam pendidikan formal."
    },

    # --- 4. Pertumbuhan Ekonomi & PDRB ---
    "Laju Pertumbuhan PDRB atas Dasar Harga Konstan (%)": {
        "var_id": "52", "kategori": "4. Pertumbuhan Ekonomi & PDRB", "unit": "%",
        "desc": "Pertumbuhan Produk Domestik Regional Bruto riil tahunan antar-provinsi."
    }
}

# =============================================================================
# 1. KONTROL PEMILIHAN INDIKATOR
# =============================================================================
st.subheader("1. Pemilihan Indikator Resmi BPS")
col_kat, col_ind = st.columns([1.2, 2])

daftar_kategori = sorted(list(set(v["kategori"] for v in BPS_CATALOG.values())))
with col_kat:
    pilihan_kategori = st.selectbox("Kategori Bidang Statistik:", ["Semua Kategori"] + daftar_kategori)

opsi = [
    k for k, v in BPS_CATALOG.items()
    if pilihan_kategori == "Semua Kategori" or v["kategori"] == pilihan_kategori
]

with col_ind:
    nama_indikator = st.selectbox(f"Nama Indikator ({len(opsi)} Tersedia):", opsi)

meta = BPS_CATALOG[nama_indikator]
var_id = meta["var_id"]

with st.expander("ℹ️ Definisi & Metadata Resmi BPS", expanded=False):
    st.markdown(f"**Indikator:** {nama_indikator}")
    st.markdown(f"**Variable ID BPS:** `{var_id}`")
    st.markdown(f"**Kategori:** `{meta['kategori']}`")
    st.markdown(f"**Satuan Pengukuran:** `{meta['unit']}`")
    st.markdown(f"**Metodologi / Deskripsi:**\n{meta['desc']}")
    st.markdown("🔗 **Portal Sumber Resmi:** [BPS Indonesia - WebAPI Service](https://webapi.bps.go.id/)")

# =============================================================================
# 2. PENARIKAN DATA LIVE DARI SERVER RESMI BPS RI
# =============================================================================
st.subheader("2. Penarikan Data Runtun Waktu & Wilayah")

if st.button("📊 Ambil Data BPS Langsung", type="primary"):
    with st.spinner(f"Menghubungi server WebAPI BPS Jakarta untuk variabel ID {var_id}..."):
        # Endpoint resmi WebAPI BPS level nasional/provinsi (domain 0000 = BPS Pusat)
        api_url = f"https://webapi.bps.go.id/v1/api/list/model/data/lang/ind/domain/0000/var/{var_id}/key/{BPS_APP_ID}/"
        
        try:
            res = requests.get(api_url, headers=HEADERS, timeout=25)
            
            if res.status_code == 200:
                payload = res.json()
                
                if payload.get("data-availability") == "available":
                    vervar_list = payload.get("vervar", [])
                    tahun_list = payload.get("tahun", [])
                    turtahun_list = payload.get("turtahun", [])
                    datacontent = payload.get("datacontent", {})

                    # Mapping ID ke Label
                    map_vervar = {str(item["val"]): item["label"] for item in vervar_list}
                    map_tahun = {str(item["val"]): item["label"] for item in tahun_list}
                    map_turtahun = {str(item["val"]): item["label"] for item in turtahun_list}

                    records = []
                    for key_code, raw_val in datacontent.items():
                        if raw_val is not None:
                            try:
                                clean_val = float(raw_val)
                            except (ValueError, TypeError):
                                continue

                            # Dekode ID dimensi BPS: format key BPS adalah kombinasi ID dimensi
                            matched_wilayah = None
                            for v_id, v_label in map_vervar.items():
                                if key_code.startswith(str(v_id)):
                                    matched_wilayah = v_label
                                    rem = key_code[len(str(v_id)):]
                                    break
                            
                            if not matched_wilayah:
                                continue

                            # Cocokkan Tahun
                            matched_tahun = None
                            for th_id, th_label in map_tahun.items():
                                if str(th_id) in rem:
                                    matched_tahun = th_label
                                    break
                            
                            if matched_wilayah and matched_tahun:
                                try:
                                    th_int = int(str(matched_tahun)[:4])
                                    records.append({
                                        "Wilayah / Provinsi": str(matched_wilayah).strip(),
                                        "Tahun": th_int,
                                        f"Nilai ({meta['unit']})": clean_val
                                    })
                                except ValueError:
                                    continue

                    if records:
                        val_col = f"Nilai ({meta['unit']})"
                        df_raw = pd.DataFrame(records)
                        
                        # Rata-rata jika ada semesteran/turunan tahunan
                        df_bps = df_raw.groupby(["Wilayah / Provinsi", "Tahun"], as_index=False)[val_col].mean().round(2)

                        st.success(f"Berhasil menarik {len(df_bps)} observasi langsung dari server WebAPI BPS!")
                        st.divider()

                        daftar_wilayah = sorted(df_bps["Wilayah / Provinsi"].unique())
                        default_pilihan = ["INDONESIA"] if "INDONESIA" in daftar_wilayah else [daftar_wilayah[0]]

                        # Pilihan Wilayah / Provinsi untuk Komparasi
                        wilayah_terpilih = st.multiselect(
                            "Pilih Wilayah / Provinsi untuk Ditampilkan:",
                            options=daftar_wilayah,
                            default=default_pilihan
                        )

                        if wilayah_terpilih:
                            df_filtered = df_bps[df_bps["Wilayah / Provinsi"].isin(wilayah_terpilih)]

                            # Pivot untuk grafik & tabel runtun waktu
                            df_pivot = df_filtered.pivot_table(
                                index="Tahun",
                                columns="Wilayah / Provinsi",
                                values=val_col
                            ).sort_index(ascending=True).reset_index()

                            # Tombol Unduh
                            c1, c2 = st.columns(2)
                            c1.download_button(
                                "📥 Unduh CSV",
                                df_pivot.to_csv(index=False).encode("utf-8"),
                                f"BPS_{var_id}_Data.csv",
                                "text/csv"
                            )
                            buf = io.BytesIO()
                            with pd.ExcelWriter(buf, engine="openpyxl") as writer:
                                df_pivot.to_excel(writer, index=False, sheet_name="BPS Data")
                            c2.download_button(
                                "📊 Unduh Excel (.xlsx)",
                                buf.getvalue(),
                                f"BPS_{var_id}_Data.xlsx",
                                "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                            )

                            # Visualisasi Plotly Interaktif
                            fig = go.Figure()
                            for w in wilayah_terpilih:
                                if w in df_pivot.columns:
                                    is_nasional = (w.upper() == "INDONESIA")
                                    fig.add_trace(go.Scatter(
                                        x=df_pivot["Tahun"],
                                        y=df_pivot[w],
                                        mode="lines+markers",
                                        name=w,
                                        line=dict(width=3.5 if is_nasional else 2.0),
                                        marker=dict(size=8 if is_nasional else 5),
                                        connectgaps=False,
                                        hovertemplate=f"<b>{w}</b><br>Tahun %{{x}}<br>Nilai: %{{y:,.2f}} {meta['unit']}<extra></extra>"
                                    ))

                            fig.update_layout(
                                xaxis=dict(title="Tahun", tickmode="linear"),
                                yaxis=dict(title=meta["unit"]),
                                hovermode="x unified",
                                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
                                margin=dict(l=20, r=20, t=50, b=20)
                            )
                            st.plotly_chart(fig, use_container_width=True)

                            with st.expander("📋 Tabel Runtun Waktu Lengkap"):
                                st.dataframe(
                                    df_pivot.sort_values(by="Tahun", ascending=False).fillna("-"),
                                    use_container_width=True
                                )
                        else:
                            st.warning("Pilih setidaknya satu wilayah / provinsi untuk menampilkan data.")
                    else:
                        st.warning("Data observasi untuk variabel ini sedang dalam proses sinkronisasi di server BPS.")
                else:
                    st.warning("Data belum tersedia di server BPS untuk variabel ini.")
            else:
                st.error(f"Gagal menghubungi server BPS (Kode Status: {res.status_code}).")
        except Exception as e:
            st.error(f"Terjadi kesalahan saat memproses data BPS: {e}")

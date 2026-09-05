import io
import pandas as pd
import plotly.graph_objects as go
import requests
import streamlit as st

st.set_page_config(page_title="BPS Data Explorer - IndoEcon", layout="wide")

st.title("📊 BPS (Badan Pusat Statistik RI) - Statistik Nasional")
st.markdown(
    "Eksplorasi indikator resmi **Tingkat Nasional (Indonesia)** langsung dari "
    "**WebAPI BPS RI** secara *real-time* (*100% Live API*)."
)

# API key diambil otomatis dari secrets
bps_api_key = st.secrets.get("BPS_API_KEY", "")

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

if not bps_api_key:
    st.error("⚙️ Kunci WebAPI BPS belum dikonfigurasi di secrets pengembang (`st.secrets['BPS_API_KEY']`).")
    st.stop()

# KATALOG INDIKATOR RESMI BPS NASIONAL
BPS_CATALOG = {
    # --- Kemiskinan & Ketimpangan ---
    "Persentase Penduduk Miskin Nasional (P0, %)": {
        "var_id": "23", "kategori": "1. Kemiskinan & Ketimpangan", "unit": "%",
        "desc": "Persentase penduduk yang berada di bawah Garis Kemiskinan resmi BPS (agregat nasional)."
    },
    "Gini Ratio / Rasio Gini Nasional": {
        "var_id": "149", "kategori": "1. Kemiskinan & Ketimpangan", "unit": "Koefisien Gini",
        "desc": "Tingkat ketimpangan pengeluaran penduduk agregat (skala 0 hingga 1)."
    },
    "Garis Kemiskinan Nasional (Rp/Kapita/Bulan)": {
        "var_id": "25", "kategori": "1. Kemiskinan & Ketimpangan", "unit": "Rp/Kapita/Bulan",
        "desc": "Nilai pengeluaran minimum kebutuhan pokok makanan dan non-makanan per kapita sebulan."
    },
    "Jumlah Penduduk Miskin Nasional (Juta Jiwa)": {
        "var_id": "24", "kategori": "1. Kemiskinan & Ketimpangan", "unit": "Ribu Jiwa",
        "desc": "Total jumlah penduduk miskin di Indonesia."
    },

    # --- Ketenagakerjaan ---
    "Tingkat Pengangguran Terbuka (TPT) Nasional (%)": {
        "var_id": "543", "kategori": "2. Ketenagakerjaan", "unit": "%",
        "desc": "Persentase jumlah penganggur terhadap total angkatan kerja resmi BPS."
    },
    "Tingkat Partisipasi Angkatan Kerja (TPAK) Nasional (%)": {
        "var_id": "542", "kategori": "2. Ketenagakerjaan", "unit": "%",
        "desc": "Persentase penduduk usia 15 tahun ke atas yang aktif dalam kegiatan ekonomi."
    },

    # --- Pembangunan Manusia ---
    "Indeks Pembangunan Manusia (IPM) Nasional": {
        "var_id": "498", "kategori": "3. Pembangunan Manusia", "unit": "Indeks",
        "desc": "Capaian komposit derajat kesehatan, taraf pendidikan, dan standar hidup layak."
    },
    "Angka Harapan Hidup saat Lahir (AHH) Nasional": {
        "var_id": "500", "kategori": "3. Pembangunan Manusia", "unit": "Tahun",
        "desc": "Rata-rata perkiraan banyak tahun yang dapat ditempuh oleh bayi yang baru lahir."
    },
    "Rata-rata Lama Sekolah (RLS) Nasional": {
        "var_id": "501", "kategori": "3. Pembangunan Manusia", "unit": "Tahun",
        "desc": "Rata-rata jumlah tahun pendidikan formal penduduk usia 25 tahun ke atas."
    }
}

# =============================================================================
# 1. KONTROL PILIHAN INDIKATOR
# =============================================================================
st.subheader("1. Pemilihan Indikator Resmi BPS")
c_kat, c_ind = st.columns([1.2, 2])

daftar_kategori = sorted(list(set(v["kategori"] for v in BPS_CATALOG.values())))
with c_kat:
    kat_pilihan = st.selectbox("Kategori Bidang:", ["Semua Kategori"] + daftar_kategori)

opsi = [
    k for k, v in BPS_CATALOG.items()
    if kat_pilihan == "Semua Kategori" or v["kategori"] == kat_pilihan
]

with c_ind:
    nama_indikator = st.selectbox(f"Pilih Indikator ({len(opsi)} Tersedia):", opsi)

meta = BPS_CATALOG[nama_indikator]
var_id = meta["var_id"]

with st.expander("ℹ️ Definisi & Metadata Resmi BPS", expanded=False):
    st.markdown(f"**Indikator:** {nama_indikator}")
    st.markdown(f"**Variable ID:** `{var_id}`")
    st.markdown(f"**Kategori:** `{meta['kategori']}`")
    st.markdown(f"**Satuan:** `{meta['unit']}`")
    st.markdown(f"**Deskripsi:**\n{meta['desc']}")
    st.markdown("🔗 **Portal Sumber:** [WebAPI BPS RI](https://webapi.bps.go.id/)")

# =============================================================================
# 2. PENARIKAN DATA RUN TUN WAKTU
# =============================================================================
st.subheader("2. Penarikan Data Runtun Waktu Nasional")

if st.button("📊 Ambil Data BPS", type="primary"):
    with st.spinner(f"Menghubungi WebAPI BPS untuk variabel ID {var_id}..."):
        api_url = f"https://webapi.bps.go.id/v1/api/list/model/data/lang/ind/domain/0000/var/{var_id}/key/{bps_api_key}/"

        try:
            res = requests.get(api_url, headers=HEADERS, timeout=25)
            if res.status_code == 200:
                payload = res.json()

                if payload.get("data-availability") == "available":
                    vervar_list = payload.get("vervar", [])
                    tahun_list = payload.get("tahun", [])
                    datacontent = payload.get("datacontent", {})

                    # Identifikasi ID wilayah INDONESIA
                    id_nasional = None
                    for v in vervar_list:
                        if "INDONESIA" in str(v.get("label", "")).upper():
                            id_nasional = str(v.get("val"))
                            break

                    map_tahun = {str(t["val"]): str(t["label"]).strip() for t in tahun_list}

                    records = []
                    for key_str, raw_val in datacontent.items():
                        if raw_val is None:
                            continue
                        try:
                            val_num = float(raw_val)
                        except (ValueError, TypeError):
                            continue

                        # Saring hanya agregat nasional
                        if id_nasional and not key_str.startswith(id_nasional):
                            continue

                        # Ekstraksi tahun
                        for th_id, th_label in map_tahun.items():
                            if th_id in key_str:
                                try:
                                    th_int = int(th_label[:4])
                                    records.append({"Tahun": th_int, "Nilai": val_num})
                                except ValueError:
                                    pass
                                break

                    if records:
                        val_col = f"Nilai ({meta['unit']})"
                        df_raw = pd.DataFrame(records)
                        df_bps = df_raw.groupby("Tahun", as_index=False)["Nilai"].mean().round(2)
                        df_bps = df_bps.rename(columns={"Nilai": val_col}).sort_values(by="Tahun", ascending=True)

                        st.success(f"Berhasil menarik {len(df_bps)} observasi resmi dari server BPS!")
                        st.divider()

                        # Unduh Data
                        c1, c2 = st.columns(2)
                        c1.download_button(
                            "📥 Unduh CSV",
                            df_bps.to_csv(index=False).encode("utf-8"),
                            f"BPS_Nasional_{var_id}.csv",
                            "text/csv"
                        )
                        buf = io.BytesIO()
                        with pd.ExcelWriter(buf, engine="openpyxl") as writer:
                            df_bps.to_excel(writer, index=False, sheet_name="BPS Data")
                        c2.download_button(
                            "📊 Unduh Excel (.xlsx)",
                            buf.getvalue(),
                            f"BPS_Nasional_{var_id}.xlsx",
                            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                        )

                        # Grafik Plotly
                        fig = go.Figure()
                        fig.add_trace(go.Scatter(
                            x=df_bps["Tahun"],
                            y=df_bps[val_col],
                            mode="lines+markers",
                            name="Nasional (Indonesia)",
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
                        st.warning("Observasi runtun waktu nasional untuk indikator ini sedang diperbarui di server BPS.")
                else:
                    st.warning("Respon server BPS: data belum tersedia untuk parameter ini.")
            else:
                st.error(f"Gagal menghubungi server BPS (Kode Status HTTP: {res.status_code}).")
        except Exception as e:
            st.error(f"Terjadi kendala koneksi: {e}")

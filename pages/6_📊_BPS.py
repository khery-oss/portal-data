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

bps_api_key = st.secrets.get("BPS_API_KEY", "")

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

if not bps_api_key:
    st.error("⚙️ Kunci WebAPI BPS belum terdeteksi di `st.secrets['BPS_API_KEY']`.")
    st.stop()

# KATALOG INDIKATOR DENGAN VARIABLE ID RESMI BPS
BPS_CATALOG = {
    "Persentase Penduduk Miskin Nasional (P0, %)": {
        "var_id": "23", "kategori": "1. Kemiskinan & Ketimpangan", "unit": "%",
        "desc": "Persentase penduduk di bawah garis kemiskinan nasional (Susenas)."
    },
    "Gini Ratio / Rasio Gini Nasional": {
        "var_id": "149", "kategori": "1. Kemiskinan & Ketimpangan", "unit": "Koefisien Gini",
        "desc": "Ukuran ketimpangan agregat pengeluaran nasional."
    },
    "Garis Kemiskinan Nasional (Rp/Kapita/Bulan)": {
        "var_id": "25", "kategori": "1. Kemiskinan & Ketimpangan", "unit": "Rp/Kapita/Bulan",
        "desc": "Batas minimum rupiah kebutuhan pokok per kapita per bulan."
    },
    "Tingkat Pengangguran Terbuka (TPT) Nasional (%)": {
        "var_id": "543", "kategori": "2. Ketenagakerjaan", "unit": "%",
        "desc": "Persentase pengangguran terbuka terhadap angkatan kerja (Sakernas)."
    },
    "Tingkat Partisipasi Angkatan Kerja (TPAK) Nasional (%)": {
        "var_id": "542", "kategori": "2. Ketenagakerjaan", "unit": "%",
        "desc": "Persentase angkatan kerja terhadap penduduk usia 15 tahun ke atas."
    },
    "Indeks Pembangunan Manusia (IPM) Nasional": {
        "var_id": "498", "kategori": "3. Pembangunan Manusia", "unit": "Indeks",
        "desc": "Capaian komposit IPM nasional berbasis standar baru BPS."
    }
}

# =============================================================================
# 1. PEMILIHAN INDIKATOR
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
    st.markdown(f"**Satuan:** `{meta['unit']}`")
    st.markdown(f"**Metodologi / Deskripsi:**\n{meta['desc']}")

# =============================================================================
# 2. PENARIKAN DATA LIVE API BPS
# =============================================================================
st.subheader("2. Penarikan Data Runtun Waktu Nasional")

# Batasi rentang penarikan agar query tidak ditolak oleh server BPS
jumlah_tahun = st.slider("Rentang Pengambilan Periode Rilis Terbaru:", min_value=3, max_value=10, value=6)

if st.button("📊 Ambil Data BPS Langsung", type="primary"):
    with st.spinner(f"Menghubungi WebAPI BPS untuk variabel {var_id}..."):
        # Ambil daftar ID tahun resmi yang terdaftar di BPS Pusat
        url_tahun = f"https://webapi.bps.go.id/v1/api/list/model/tahun/lang/ind/domain/0000/key/{bps_api_key}/"
        tahun_map = {}
        try:
            r_th = requests.get(url_tahun, headers=HEADERS, timeout=20)
            if r_th.status_code == 200:
                p_th = r_th.json()
                if p_th.get("data-availability") == "available":
                    raw_th = p_th.get("data", [])
                    th_list = raw_th[1] if isinstance(raw_th, list) and len(raw_th) > 1 else raw_th
                    for item in th_list:
                        if isinstance(item, dict):
                            val = item.get("val") or item.get("th_id")
                            lbl = item.get("label") or item.get("th")
                            if val and lbl:
                                try:
                                    tahun_map[int(str(lbl)[:4])] = str(val)
                                except ValueError:
                                    pass
        except Exception:
            pass

        # Urutkan tahun terbaru dan ambil sejumlah pilihan slider
        tahun_terpilih = sorted(tahun_map.keys(), reverse=True)[:jumlah_tahun]
        records = []

        # Tarik data per tahun terdaftar via API resmi BPS
        for th_label in tahun_terpilih:
            th_id = tahun_map[th_label]
            api_url = f"https://webapi.bps.go.id/v1/api/list/model/data/lang/ind/domain/0000/var/{var_id}/th/{th_id}/key/{bps_api_key}/"
            
            try:
                res = requests.get(api_url, headers=HEADERS, timeout=15)
                if res.status_code == 200:
                    payload = res.json()
                    if payload.get("data-availability") == "available":
                        vervar = payload.get("vervar", [])
                        datacontent = payload.get("datacontent", {})

                        # Cari penanda entitas nasional "INDONESIA"
                        id_nasional = None
                        for v in vervar:
                            if "INDONESIA" in str(v.get("label", "")).upper():
                                id_nasional = str(v.get("val"))
                                break

                        for k_code, r_val in datacontent.items():
                            if r_val is not None:
                                try:
                                    f_val = float(r_val)
                                    if id_nasional:
                                        if k_code.startswith(id_nasional):
                                            records.append({"Tahun": th_label, "Nilai": f_val})
                                    else:
                                        records.append({"Tahun": th_label, "Nilai": f_val})
                                except (ValueError, TypeError):
                                    continue
            except Exception:
                continue

        if records:
            val_col = f"Nilai ({meta['unit']})"
            df_raw = pd.DataFrame(records)
            df_bps = df_raw.groupby("Tahun", as_index=False)["Nilai"].mean().round(2)
            df_bps = df_bps.rename(columns={"Nilai": val_col}).sort_values(by="Tahun", ascending=True)

            st.success(f"Berhasil menarik {len(df_bps)} observasi tahunan resmi langsung dari server BPS!")
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

            # Visualisasi Garis Runtun Waktu
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
            st.warning("Server BPS tidak mengembalikan observasi untuk rentang tahun yang diminta. Coba turunkan rentang tahun.")

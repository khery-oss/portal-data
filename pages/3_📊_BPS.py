import io
import time
import pandas as pd
import plotly.graph_objects as go
import requests
import streamlit as st

st.set_page_config(page_title="BPS Data Explorer", layout="wide")

st.title("📊 Portal Data Resmi BPS")
st.write(
    "Eksplorasi seluruh indikator dan wilayah resmi dari **WebAPI Badan Pusat"
    " Statistik (BPS)**."
)

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    )
}

if "BPS_APP_ID" in st.secrets:
  BPS_APP_ID = st.secrets["BPS_APP_ID"]
else:
  st.error("⚠️ Masukkan `BPS_APP_ID` di Streamlit Secrets terlebih dahulu.")
  st.stop()


# 1. Mengambil Seluruh Wilayah Resmi BPS (Nasional, Provinsi, Kab/Kota)
@st.cache_data(ttl=86400)
def get_all_domains():
  url = f"https://webapi.bps.go.id/v1/api/list/model/domain/type/all/key/{BPS_APP_ID}/"
  try:
    r = requests.get(url, headers=HEADERS, timeout=20)
    res = r.json()
    if res.get("status") == "OK" and len(res.get("data", [])) > 1:
      domains = res["data"][1]
      dom_map = {}
      for d in domains:
        dom_id = str(d["domain_id"])
        dom_name = d["domain_name"]
        dom_map[f"{dom_name} ({dom_id})"] = dom_id
      return dom_map
  except Exception:
    pass

  # Fallback jika endpoint list domain sedang lambat
  return {
      "Nasional (0000)": "0000",
      "DKI Jakarta (3100)": "3100",
      "Jawa Barat (3200)": "3200",
      "Jawa Tengah (3300)": "3300",
      "Jawa Timur (3500)": "3500",
      "Kota Bandung (3273)": "3273",
      "Kota Surabaya (3578)": "3578",
      "Kota Makassar (7371)": "7371",
  }


all_domains = get_all_domains()

# 2. Pilihan Cakupan Wilayah
col_wil1, col_wil2 = st.columns([2, 1])
with col_wil1:
  selected_domain_label = st.selectbox(
      "1. Pilih Wilayah (Nasional, Provinsi, atau Kab/Kota):",
      list(all_domains.keys()),
      index=0,
  )
  domain_code = all_domains[selected_domain_label]

with col_wil2:
  st.caption("Cakupan Terpilih:")
  st.code(f"Kode Domain: {domain_code}")


# 3. Mengambil Seluruh Katalog Indikator/Variabel BPS
@st.cache_data(ttl=3600)
def get_variables(domain, page=1):
  url = f"https://webapi.bps.go.id/v1/api/list/model/var/lang/ind/domain/{domain}/page/{page}/key/{BPS_APP_ID}/"
  try:
    r = requests.get(url, headers=HEADERS, timeout=20)
    data = r.json()
    if data.get("status") == "OK" and len(data.get("data", [])) > 1:
      total_pages = data["data"][0].get("pages", 1)
      items = {
          f"{item['title']} (ID: {item['var_id']})": item["var_id"]
          for item in data["data"][1]
      }
      return items, total_pages
  except Exception:
    pass
  return {}, 1


col_p1, col_p2 = st.columns([1, 3])
with col_p1:
  page_num = st.number_input(
      "Halaman Katalog BPS:", min_value=1, max_value=50, value=1, step=1
  )

vars_dict, total_pages = get_variables(domain_code, page=page_num)

with col_p2:
  if vars_dict:
    selected_var_label = st.selectbox(
        f"2. Pilih Indikator BPS (Total {total_pages} Halaman Tersedia):",
        list(vars_dict.keys()),
    )
    var_id = vars_dict[selected_var_label]
  else:
    st.warning("Tidak ditemukan variabel aktif di halaman ini untuk domain ini.")
    st.stop()

# 4. Filter Rentang Waktu Panjang (Otomatis Batched di Background)
st.write("---")
col_t1, col_t2 = st.columns(2)
with col_t1:
  tahun_mulai = st.number_input(
      "Tahun Awal:", min_value=1990, max_value=2026, value=2010
  )
with col_t2:
  tahun_selesai = st.number_input(
      "Tahun Akhir:", min_value=tahun_mulai, max_value=2026, value=2024
  )

# Eksekusi Penarikan Data
if st.button("📊 Tarik Data Lengkap", type="primary"):
  # Bagi rentang tahun menjadi blok 3-tahunan agar memenuhi aturan BPS
  all_years_range = list(range(int(tahun_mulai), int(tahun_selesai) + 1))
  batches = [
      all_years_range[i : i + 3] for i in range(0, len(all_years_range), 3)
  ]

  records = []
  progress_bar = st.progress(0)

  with st.spinner(
      f"Mengunduh data {selected_var_label} untuk {len(all_years_range)} tahun..."
  ):
    for idx, b in enumerate(batches):
      th_query = f"{b[0]}:{b[-1]}" if len(b) > 1 else str(b[0])
      url = f"https://webapi.bps.go.id/v1/api/list/model/data/lang/ind/domain/{domain_code}/var/{var_id}/th/{th_query}/key/{BPS_APP_ID}/"

      try:
        res = requests.get(url, headers=HEADERS, timeout=20).json()
        if (
            res.get("status") == "OK"
            and res.get("data-availability") != "list-not-available"
        ):
          content = res.get("datacontent", {})
          vervar = {
              str(item["val"]): item["label"] for item in res.get("vervar", [])
          }
          tahun_dict = {
              str(item["val"]): item["label"] for item in res.get("tahun", [])
          }

          for k, v in content.items():
            if v is not None:
              k_str = str(k)
              nama_rincian = selected_domain_label.split(" (")[0]
              label_tahun = "-"

              for v_val, v_lbl in vervar.items():
                if k_str.startswith(v_val):
                  nama_rincian = v_lbl
                  break

              for t_val, t_lbl in tahun_dict.items():
                if t_val in k_str:
                  label_tahun = t_lbl
                  break

              records.append({
                  "Rincian / Kategori": nama_rincian,
                  "Tahun": str(label_tahun),
                  "Nilai": v,
              })
        time.sleep(0.15)
      except Exception:
        pass

      progress_bar.progress((idx + 1) / len(batches))

  df = pd.DataFrame(records)

  if not df.empty:
    # Filter hanya tahun numerik yang valid dalam rentang
    df = df[df["Tahun"].str.isnumeric()]
    df = df.drop_duplicates().sort_values(
        by=["Rincian / Kategori", "Tahun"], ascending=[True, True]
    )

    st.success(
        f"Berhasil menarik {len(df)} titik observasi dari server BPS!"
    )

    # Visualisasi Deret Waktu
    st.subheader(f"📈 Grafik Tren: {selected_var_label}")

    fig = go.Figure()
    kategori_unik = df["Rincian / Kategori"].unique()

    for kat in kategori_unik:
      sub_df = df[df["Rincian / Kategori"] == kat]
      fig.add_trace(
          go.Scatter(
              x=sub_df["Tahun"],
              y=sub_df["Nilai"],
              mode="lines+markers",
              name=kat,
              connectgaps=False,  # Garis putus jika ada tahun yang kosong
              hovertemplate=(
                  f"Tahun: %{{x}}<br>{kat}: %{{y}}<extra></extra>"
              ),
          )
      )

    fig.update_layout(
        xaxis=dict(title="Tahun", type="category"),
        yaxis=dict(title="Nilai"),
        hovermode="x unified",
        margin=dict(l=20, r=20, t=40, b=20),
    )
    st.plotly_chart(fig, use_container_width=True)

    # Tabel Data
    st.subheader("📋 Tabel Data")
    c_dl1, c_dl2 = st.columns(2)
    c_dl1.download_button(
        "📥 Unduh CSV",
        df.to_csv(index=False).encode("utf-8"),
        f"bps_{domain_code}_{var_id}.csv",
        "text/csv",
    )

    buf = io.BytesIO()
    with pd.ExcelWriter(buf, engine="openpyxl") as writer:
      df.to_excel(writer, index=False, sheet_name="Data BPS")
    c_dl2.download_button(
        "📊 Unduh Excel (.xlsx)",
        buf.getvalue(),
        f"bps_{domain_code}_{var_id}.xlsx",
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )

    # Pivot agar tahun menjadi kolom horizontal
    try:
      df_pivot = df.pivot(
          index="Rincian / Kategori", columns="Tahun", values="Nilai"
      ).reset_index()
      st.dataframe(df_pivot.fillna("-"), use_container_width=True)
    except Exception:
      st.dataframe(df.fillna("-"), use_container_width=True)

  else:
    st.warning(
        f"Server BPS merespons bahwa indikator '{selected_var_label}' tidak"
        f" memiliki data angka pada rentang {tahun_mulai}–{tahun_selesai} untuk"
        f" domain {selected_domain_label}."
    )
    st.info(
        "💡 Saran: Coba pilih halaman katalog lain atau ganti domain wilayah"
        " (misal: Nasional 0000)."
    )

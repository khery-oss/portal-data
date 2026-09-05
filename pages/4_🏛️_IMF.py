import io
import pandas as pd
import plotly.graph_objects as go
import requests
import streamlit as st

st.set_page_config(page_title="IMF Data Explorer - Indonesia", layout="wide")

st.title("🏛️ Portal Data IMF (World Economic Outlook - Indonesia)")
st.write(
    "Eksplorasi indikator makroekonomi, neraca pembayaran, dan proyeksi fiskal resmi **International Monetary Fund (IMF)** "
    "khusus untuk wilayah **Indonesia (IDN)** berdasarkan publikasi resmi **IMF World Economic Outlook (WEO)** (rentang 1980 – 2029)."
)

# Headers lengkap agar request ke API resmi IMF tidak diblokir
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "application/json"
}

# KATALOG LENGKAP RESMI IMF WEO UNTUK INDONESIA
IMF_CATALOG = {
    # --- 1. Output & National Accounts ---
    "Real GDP Growth (Annual %)": {
        "id": "NGDP_RPCH", "unit": "%", "kategori": "1. Output & Pertumbuhan",
        "desc": "Annual percentages of constant price GDP are year-on-year changes based on national currency."
    },
    "Gross Domestic Product, Constant Prices (Trillion IDR)": {
        "id": "NGDP_R", "unit": "Trillion IDR", "kategori": "1. Output & Pertumbuhan",
        "desc": "Gross domestic product expressed in constant national currency (Indonesian Rupiah)."
    },
    "Gross Domestic Product, Current Prices (Trillion IDR)": {
        "id": "NGDP", "unit": "Trillion IDR", "kategori": "1. Output & Pertumbuhan",
        "desc": "Gross domestic product expressed in current national currency (Indonesian Rupiah)."
    },
    "Gross Domestic Product, Current Prices (Billion USD)": {
        "id": "NGDPD", "unit": "Billion USD", "kategori": "1. Output & Pertumbuhan",
        "desc": "Gross domestic product expressed in billions of current U.S. dollars."
    },
    "GDP per Capita, Current Prices (USD)": {
        "id": "NGDPDPC", "unit": "USD", "kategori": "1. Output & Pertumbuhan",
        "desc": "GDP divided by total population, expressed in current U.S. dollars."
    },
    "GDP per Capita, PPP (Current International Dollar)": {
        "id": "PPPPC", "unit": "Current Int $", "kategori": "1. Output & Pertumbuhan",
        "desc": "GDP per capita converted to international dollars using purchasing power parity rates."
    },
    "GDP based on Purchasing-Power-Parity (PPP) Share of World Total": {
        "id": "PPPSH", "unit": "% of World", "kategori": "1. Output & Pertumbuhan",
        "desc": "Indonesia's share of total global GDP based on purchasing power parity valuation."
    },

    # --- 2. Inflation & Prices ---
    "Inflation Rate, Average Consumer Prices (Annual %)": {
        "id": "PCPIPCH", "unit": "%", "kategori": "2. Inflasi & Harga",
        "desc": "Annual percentage change in the average consumer price index."
    },
    "Inflation Rate, End of Period Consumer Prices (Annual %)": {
        "id": "PCPIEPCH", "unit": "%", "kategori": "2. Inflasi & Harga",
        "desc": "End-of-period consumer price index annual percentage change."
    },
    "GDP Deflator (Index Change %)": {
        "id": "NGDP_D", "unit": "% Change", "kategori": "2. Inflasi & Harga",
        "desc": "Ratio of nominal GDP to real GDP expressed as an annual percentage variation."
    },

    # --- 3. Fiscal & Public Finance ---
    "General Government Gross Debt (% of GDP)": {
        "id": "GGXWDG_NGDP", "unit": "% of GDP", "kategori": "3. Fiskal & Keuangan Pemerintah",
        "desc": "Total nominal liabilities and gross debt of general government relative to national GDP."
    },
    "General Government Net Lending/Borrowing (% of GDP)": {
        "id": "GGXCNL_NGDP", "unit": "% of GDP", "kategori": "3. Fiskal & Keuangan Pemerintah",
        "desc": "Overall government budget balance (Fiscal Deficit or Surplus) relative to GDP."
    },
    "General Government Primary Balance (% of GDP)": {
        "id": "GGXONLB_NGDP", "unit": "% of GDP", "kategori": "3. Fiskal & Keuangan Pemerintah",
        "desc": "Primary net lending/borrowing excluding interest expenditure as a percentage of GDP."
    },
    "General Government Revenue (% of GDP)": {
        "id": "GGR_NGDP", "unit": "% of GDP", "kategori": "3. Fiskal & Keuangan Pemerintah",
        "desc": "Total government revenue collected relative to the size of the national economy."
    },
    "General Government Total Expenditure (% of GDP)": {
        "id": "GGX_NGDP", "unit": "% of GDP", "kategori": "3. Fiskal & Keuangan Pemerintah",
        "desc": "Total government outlays and expenses relative to the size of the national economy."
    },

    # --- 4. External Sector & Trade ---
    "Current Account Balance (% of GDP)": {
        "id": "BCA_NGDPD", "unit": "% of GDP", "kategori": "4. Eksternal & Perdagangan",
        "desc": "Net balance of goods, services, primary income, and secondary income as a percentage of GDP."
    },
    "Current Account Balance (Billion USD)": {
        "id": "BCA", "unit": "Billion USD", "kategori": "4. Eksternal & Perdagangan",
        "desc": "Current account balance expressed in billions of current U.S. dollars."
    },
    "Volume of Exports of Goods and Services (% Change)": {
        "id": "TX_RPCH", "unit": "% Change", "kategori": "4. Eksternal & Perdagangan",
        "desc": "Annual percentage change in the constant-price volume of goods and services exported."
    },
    "Volume of Imports of Goods and Services (% Change)": {
        "id": "TM_RPCH", "unit": "% Change", "kategori": "4. Eksternal & Perdagangan",
        "desc": "Annual percentage change in the constant-price volume of goods and services imported."
    },

    # --- 5. Investment, Savings & Labor ---
    "Total Investment (% of GDP)": {
        "id": "NID_NGDP", "unit": "% of GDP", "kategori": "5. Investasi, Tabungan & Tenaga Kerja",
        "desc": "Gross capital formation as a percentage of national GDP."
    },
    "Gross National Savings (% of GDP)": {
        "id": "NGSD_NGDP", "unit": "% of GDP", "kategori": "5. Investasi, Tabungan & Tenaga Kerja",
        "desc": "Total gross national disposable income less consumption expenditure relative to GDP."
    },
    "Unemployment Rate (% of Total Labor Force)": {
        "id": "LUR", "unit": "% of Labor Force", "kategori": "5. Investasi, Tabungan & Tenaga Kerja",
        "desc": "Unemployed persons looking for work as a share of the active civilian labor force."
    },
    "Total Population (Million Persons)": {
        "id": "LP", "unit": "Million Persons", "kategori": "5. Investasi, Tabungan & Tenaga Kerja",
        "desc": "Mid-year estimate of national population based on census authorities and IMF projections."
    }
}

# 1. Pemilihan Indikator
st.subheader("1. Pemilihan Indikator IMF WEO")
col_kat, col_ind = st.columns([1, 1.8])

kategori_list = sorted(list(set(v["kategori"] for v in IMF_CATALOG.values())))
with col_kat:
    pilihan_kategori = st.selectbox("Kategori Bidang:", ["Semua Kategori"] + kategori_list)

indikator_opsi = [
    k for k, v in IMF_CATALOG.items()
    if pilihan_kategori == "Semua Kategori" or v["kategori"] == pilihan_kategori
]

with col_ind:
    selected_name = st.selectbox(f"Nama Indikator ({len(indikator_opsi)} Tersedia):", indikator_opsi)

meta = IMF_CATALOG[selected_name]
kode_imf = meta["id"]

# 2. Filter Rentang Tahun Observasi Asli IMF (1980 - 2029)
st.subheader("2. Rentang Tahun Observasi (Historis & Proyeksi WEO)")
semua_tahun_tersedia = [str(y) for y in range(1980, 2030)]

c_t1, c_t2 = st.columns(2)
with c_t1:
    th_start = st.selectbox("Tahun Mulai:", semua_tahun_tersedia, index=semua_tahun_tersedia.index("1990"))
with c_t2:
    th_end = st.selectbox("Tahun Selesai:", semua_tahun_tersedia, index=len(semua_tahun_tersedia) - 1)

if int(th_start) > int(th_end):
    st.error("Tahun mulai tidak boleh melebihi tahun selesai.")
    st.stop()

# 3. Metadata Resmi IMF
st.divider()
with st.expander("ℹ️ Definisi & Metadata Resmi IMF World Economic Outlook", expanded=True):
    st.markdown(f"**Series Name:** {selected_name}")
    st.markdown(f"**IMF WEO Technical Code:** `{kode_imf}`")
    st.markdown(f"**Kategori / Sektor:** `{meta['kategori']}`")
    st.markdown(f"**Satuan Unit:** `{meta['unit']}`")
    st.markdown(f"**Deskripsi Metodologi:**\n{meta['desc']}")
    st.markdown(
        f"🔗 **Tautan Resmi Database:** [Buka Data di IMF DataMapper Portal](https://www.imf.org/external/datamapper/{kode_imf}@WEO/IDN)"
    )

# 4. Penarikan Data Live via API IMF DataMapper (dengan fallback aman)
@st.cache_data(ttl=86400)
def fetch_imf_data(indicator_code):
    api_url = f"https://www.imf.org/external/datamapper/api/v1/{indicator_code}/IDN"
    try:
        r = requests.get(api_url, headers=HEADERS, timeout=15)
        if r.status_code == 200:
            res_json = r.json()
            val_map = res_json.get("values", {}).get(indicator_code, {}).get("IDN", {})
            return val_map
    except Exception:
        pass
    return None

val_dict = fetch_imf_data(kode_imf)

# Pembentukan DataFrame Runtun Waktu
rentang_tahun_pilihan = [str(y) for y in range(int(th_start), int(th_end) + 1)]
df_grid = pd.DataFrame({"Tahun": rentang_tahun_pilihan})

if val_dict:
    raw_list = [{"Tahun": str(k), f"Indonesia ({meta['unit']})": round(float(v), 2)} for k, v in val_dict.items()]
    raw_df = pd.DataFrame(raw_list)
    df_final = pd.merge(df_grid, raw_df, on="Tahun", how="left").sort_values("Tahun")
else:
    # Penanganan jika server IMF sedang sibuk
    st.warning("Sedang menyelaraskan data dengan server IMF DataMapper...")
    df_final = df_grid
    df_final[f"Indonesia ({meta['unit']})"] = None

# 5. Visualisasi Interaktif Plotly
st.subheader(f"📈 Tren Runtun Waktu: {selected_name}")

val_col = f"Indonesia ({meta['unit']})"
fig = go.Figure()
fig.add_trace(go.Scatter(
    x=df_final["Tahun"],
    y=df_final[val_col],
    mode="lines+markers",
    name="Indonesia (IMF WEO)",
    connectgaps=True,
    line=dict(width=2.5, color="#A6192E"),  # Merah Resmi IMF
    hovertemplate=f"Tahun %{{x}}<br>Nilai: %{{y}} {meta['unit']}<extra></extra>"
))

fig.update_layout(
    xaxis=dict(title="Tahun", tickmode="linear"),
    yaxis=dict(title=meta["unit"]),
    hovermode="x unified",
    margin=dict(l=20, r=20, t=40, b=20)
)
st.plotly_chart(fig, use_container_width=True)

# 6. Tabel Observasi & Ekspor Data
st.subheader("📋 Tabel Data Observasi (Termasuk Proyeksi)")
c_csv, c_xlsx = st.columns(2)

c_csv.download_button(
    "📥 Unduh CSV",
    df_final.to_csv(index=False).encode("utf-8"),
    f"IMF_IDN_{kode_imf}_{th_start}_{th_end}.csv",
    "text/csv"
)

buf = io.BytesIO()
with pd.ExcelWriter(buf, engine="openpyxl") as writer:
    df_final.to_excel(writer, index=False, sheet_name="IMF Data")
c_xlsx.download_button(
    "📊 Unduh Excel (.xlsx)",
    buf.getvalue(),
    f"IMF_IDN_{kode_imf}_{th_start}_{th_end}.xlsx",
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
)

st.dataframe(df_final.fillna("-"), use_container_width=True)
st.caption(
    "💡 **Catatan IMF WEO:** Data mencakup nilai historis resmi dan angka proyeksi World Economic Outlook untuk Indonesia. "
    "Tanda strip (-) menandakan data pada tahun tersebut tidak dicatat dalam seri bersangkutan."
)

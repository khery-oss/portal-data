import re
from pathlib import Path
import requests
import streamlit as st
from style_helper import apply_custom_theme

# 1. Konfigurasi & tema dipanggil SEKALI saja di sini untuk semua halaman
st.set_page_config(
    page_title="IE IndoEcon Explorer",
    page_icon=":material/analytics:",
    layout="wide",
)
apply_custom_theme()

TARGET_EMAIL = "indoecon.project@gmail.com"
PAGES_DIR = Path(__file__).resolve().parent / "pages"


def is_valid_email(email: str) -> bool:
    pattern = r"^[\w\.-]+@[\w\.-]+\.\w+$"
    return re.match(pattern, email) is not None


def find_page(prefix: str):
    """Path halaman berawalan `prefix_`, atau None bila berkasnya tidak ada (app tidak crash)."""
    match = next(PAGES_DIR.glob(f"{prefix}_*.py"), None)
    return f"pages/{match.name}" if match else None


MODUL_INFO = [
    {
        "key": "wb",
        "judul": "1. World Bank (WDI)",
        "icon": ":material/public:",
        "cakupan": "Indikator makroekonomi jangka panjang, pertumbuhan PDB riil/nominal, neraca transaksi berjalan, perdagangan internasional, dan utang.",
        "penyedia": "World Development Indicators (WDI) API.",
    },
    {
        "key": "fred",
        "judul": "2. FRED (Federal Reserve Bank of St. Louis)",
        "icon": ":material/show_chart:",
        "cakupan": "Seri data Indonesia di FRED: nilai tukar, inflasi, suku bunga, uang beredar, dan statistik perdagangan, dengan opsi agregasi frekuensi untuk data harian dan mingguan.",
        "penyedia": "Federal Reserve Economic Data REST API.",
    },
    {
        "key": "unsdg",
        "judul": "3. UN SDGs (United Nations)",
        "icon": ":material/eco:",
        "cakupan": "Indikator tujuan pembangunan berkelanjutan global, kemiskinan ekstrem, ketimpangan (*income share bottom 40%*), dan transisi energi bersih.",
        "penyedia": "United Nations Statistics Division (UNSD) SDG API.",
    },
    {
        "key": "bps",
        "judul": "4. BPS (Badan Pusat Statistik)",
        "icon": ":material/account_balance:",
        "cakupan": "Statistik resmi nasional Indonesia meliputi inflasi, kemiskinan, ketenagakerjaan, pertumbuhan ekonomi, dan indikator sektoral.",
        "penyedia": "Badan Pusat Statistik (BPS) Web API.",
    },
    {
        "key": "who",
        "judul": "5. WHO (World Health Organization)",
        "icon": ":material/local_hospital:",
        "cakupan": "Indikator kesehatan publik, angka harapan hidup, stunting & gizi balita, tenaga medis, jaminan kesehatan semesta (*UHC*), dan modal manusia.",
        "penyedia": "WHO Global Health Observatory (GHO) OData API.",
    },
    {
        "key": "vdem",
        "judul": "6. V-Dem (Varieties of Democracy)",
        "icon": ":material/how_to_vote:",
        "cakupan": "Kualitas demokrasi elektoral, liberal, partisipatif, deliberatif, egaliter, korupsi sektor publik, supremasi hukum, dan kebebasan sipil.",
        "penyedia": "V-Dem Institute Dataset (terintegrasi dengan *Codebook* penjelas).",
    },
    {
        "key": "dse",
        "judul": "7. Digital Society & Economy",
        "icon": ":material/devices:",
        "cakupan": "Inklusi keuangan (Global Findex), infrastruktur dan akses digital (ICT), disinformasi, sensor internet, pemadaman jaringan, dan kebebasan digital (DSP).",
        "penyedia": "World Bank Findex, World Bank WDI (ICT), & Digital Society Project (DSP).",
    },
    {
        "key": "comtrade",
        "judul": "8. UN Comtrade",
        "icon": ":material/directions_boat:",
        "cakupan": "Nilai ekspor dan impor barang Indonesia menurut kode HS (sejak 1989) dan SITC (1962 sampai 1989), serta total perdagangan jangka panjang. Mitra dagang: seluruh dunia (tanpa rincian per negara mitra).",
        "penyedia": "United Nations Comtrade API.",
    },
]


# 2. Seluruh konten halaman utama dibungkus di dalam fungsi beranda()
def beranda() -> None:
    st.markdown(
        '<div class="atlas-eyebrow">INDONESIA MACRO &amp; INSTITUTIONAL DATA · OPEN ACCESS</div>',
        unsafe_allow_html=True,
    )
    st.title(":material/analytics: IE IndoEcon Explorer")
    st.markdown(
        "Portal observasi data makroekonomi, ketenagakerjaan, sosial-pendidikan, kesehatan publik, institusi politik, "
        "dan demokrasi Indonesia yang terintegrasi langsung dengan berbagai institusi resmi internasional dan nasional."
    )

    # =========================================================================
    # CATATAN AKADEMIS & PENGGUNAAN RISET
    # =========================================================================
    with st.container(key="pedoman_neon"):
        with st.expander(":material/menu_book: Pedoman Penggunaan Akademis & Standar Sitasi", expanded=False):
            st.markdown(
                "Website ini dibuat untuk kebutuhan para **peneliti, akademisi, dosen, dan mahasiswa** "
                "dalam mengakses serta mengeksplorasi data resmi Indonesia secara cepat, transparan, dan terbuka.\n\n"
                "- **Rekomendasi Cross-check:** Pengguna sangat disarankan untuk tetap melakukan *cross-check* kembali "
                "ke website utama sumber data resmi seperti yang tercantum pada masing-masing modul.\n"
                "- **Standar Sitasi & Penulisan Sumber:** Dalam penulisan karya ilmiah, skripsi, tesis, jurnal, maupun laporan riset, "
                "penulisan sumber **tetap menggunakan sumber asli** tempat data diterbitkan "
                "(seperti *World Bank, FRED, UN SDGs, BPS, WHO, Comtrade, hingga V-Dem Institute*).\n"
                "- **Koreksi & Masukan:** Apabila terdapat kekeliruan, kesalahan data, atau *error* pada penarikan API/data, "
                "bisa langsung diberitahukan ke email tim pengembang melalui formulir kontak di bawah."
            )

    st.divider()

    st.subheader("Arsitektur Modul Data")
    st.markdown(
        "Pilih modul langsung dari kartu di bawah atau melalui bilah navigasi di sebelah kiri:"
    )

    # Grid 2 kolom; container ber-key berada di dalam kolom agar CSS st-key-card_* menempel di kartu
    for i in range(0, len(MODUL_INFO), 2):
        cols = st.columns(2)
        for col, modul in zip(cols, MODUL_INFO[i:i + 2]):
            with col:
                with st.container(key=f"card_{modul['key']}", border=True):
                    st.markdown(
                        f"### {modul['icon']} {modul['judul']}\n"
                        f"- **Cakupan:** {modul['cakupan']}\n"
                        f"- **Penyedia:** {modul['penyedia']}"
                    )
                    if modul["key"] in PAGES:
                        st.page_link(
                            PAGES[modul["key"]],
                            label="Buka Modul",
                            icon=":material/arrow_forward:",
                        )
                    else:
                        st.caption("Modul belum tersedia.")

    st.divider()

    # =========================================================================
    # PRINSIP INTEGRITAS
    # =========================================================================
    with st.container(key="integritas_neon"):
        st.subheader(":material/verified_user: Prinsip Integritas & Transparansi Data")
        st.markdown(
            "- **Live API & Curated Local Database:** Sebagian besar modul memanfaatkan penarikan *real-time* via API resmi, "
            "sementara modul spesifik berukuran masif (seperti V-Dem dan DSP) menggunakan arsip data terkurasi resmi yang dioptimalkan "
            "secara lokal untuk menjamin kecepatan akses web publik.\n"
            "- **Bebas Manipulasi:** Tidak ada data buatan atau tiruan (*zero hardcoding*). Seluruh angka bersumber dari publikasi lembaga aslinya. "
            "Perlakuan data seperti pembulatan atau agregasi frekuensi, bila ada, dijelaskan pada modul yang bersangkutan.\n"
            "- **Ekspor Terbuka:** Seluruh data yang ditampilkan dapat diunduh seketika dalam format CSV dan Excel (`.xlsx`) "
            "untuk diolah kembali di Stata, R, Python, maupun SPSS.\n"
            "- **Pengembangan Berkelanjutan:** Platform ini terus berada dalam masa pengembangan aktif guna meningkatkan kemudahan "
            "pencarian variabel, memperkaya fitur eksplorasi, serta menyederhanakan pemanfaatan dataset bagi seluruh kalangan akademisi."
        )

    st.divider()

    # =========================================================================
    # KOTAK SARAN, LAPORAN EROR & PERMINTAAN DATA BARU
    # =========================================================================
    with st.container(key="saran_neon"):
        st.subheader(":material/mail: Kotak Saran, Laporan Kendala & Permintaan Data")
        st.markdown(
            "Menemukan kekeliruan data, *error* pada sistem, atau membutuhkan seri indikator baru untuk riset Anda? "
            "Kirimkan masukan langsung ke email pengembang melalui formulir di bawah ini."
        )

        # clear_on_submit dimatikan: isian tidak hilang bila validasi atau pengiriman gagal
        with st.form("feedback_form", clear_on_submit=False, border=False):
            col_f1, col_f2 = st.columns(2)
            with col_f1:
                nama_pengirim = st.text_input(
                    "Nama Lengkap / Instansi Akademik*",
                    placeholder="Contoh: Budi Santoso, M.E. (Universitas Indonesia)",
                )
            with col_f2:
                email_pengirim = st.text_input(
                    "Alamat Email Pengirim*",
                    placeholder="nama@domain.com",
                )

            tipe_pesan = st.selectbox(
                "Kategori Pesan:",
                [
                    "Laporan Kesalahan Data / Sistem Error",
                    "Permintaan Indikator / Dataset Tambahan",
                    "Kritik, Saran & Masukan Metodologi",
                    "Lainnya",
                ],
            )

            isi_pesan = st.text_area(
                "Detail Laporan / Pesan*",
                placeholder="Jelaskan secara spesifik indikator mana yang mengalami kendala, atau sebutkan dataset yang ingin ditambahkan beserta sumber resminya...",
                height=130,
            )

            submitted = st.form_submit_button("Kirim Pesan ke Pengembang", type="primary")

            if submitted:
                if not nama_pengirim.strip() or not email_pengirim.strip() or not isi_pesan.strip():
                    st.error("Mohon lengkapi Nama, Email, dan Detail Pesan sebelum mengirim.")
                elif not is_valid_email(email_pengirim):
                    st.error("Format alamat email tidak valid (pastikan format seperti nama@domain.com).")
                else:
                    with st.spinner("Mengirimkan pesan ke email pengembang..."):
                        # Endpoint /ajax mengembalikan JSON, sehingga keberhasilan bisa diverifikasi
                        endpoint = f"https://formsubmit.co/ajax/{TARGET_EMAIL}"
                        payload = {
                            "name": nama_pengirim,
                            "email": email_pengirim,
                            "category": tipe_pesan,
                            "message": isi_pesan,
                            "_subject": f"[{tipe_pesan}] Pesan dari IE IndoEcon Explorer",
                            "_captcha": "false",
                            "_honey": "",  # honeypot anti-spam
                        }
                        headers = {"User-Agent": "Mozilla/5.0", "Accept": "application/json"}

                        try:
                            res = requests.post(endpoint, data=payload, headers=headers, timeout=10)
                            try:
                                berhasil = res.status_code == 200 and str(res.json().get("success")).lower() == "true"
                            except ValueError:
                                berhasil = False
                            if berhasil:
                                st.success("Terima kasih! Laporan/masukan Anda telah berhasil dikirimkan ke email pengembang.")
                            else:
                                st.warning(
                                    f"Pesan belum terkonfirmasi terkirim (status: {res.status_code}). "
                                    f"Silakan kirimkan laporan Anda secara langsung melalui email: `{TARGET_EMAIL}`"
                                )
                        except requests.RequestException:
                            st.warning(
                                "Koneksi ke server pengiriman laporan dibatasi oleh jaringan. "
                                f"Silakan kirimkan masukan secara langsung melalui email: `{TARGET_EMAIL}`"
                            )

    # =========================================================================
    # FOOTER PROFESIONAL (METADATA & COPYRIGHT)
    # =========================================================================
    st.markdown("---")
    col_foot1, col_foot2, col_foot3 = st.columns(3)
    with col_foot1:
        st.markdown("**IE IndoEcon Explorer**")
        st.markdown("Platform Riset & Observasi Data Publik")
    with col_foot2:
        st.markdown("**Pengembang & Periset**")
        st.markdown("**K. N. Phane**")
    with col_foot3:
        st.markdown("**Arsip Akademik**")
        st.markdown("© 2025–2026 • Pengembangan Aktif")


# 3. Daftarkan halaman sekali saja; halaman yang berkasnya tidak ada dilewati
PAGE_SPEC = {
    "wb": ("1", "World Bank", ":material/public:"),
    "fred": ("2", "FRED", ":material/show_chart:"),
    "unsdg": ("4", "UN SDG", ":material/eco:"),
    "bps": ("5", "BPS", ":material/account_balance:"),
    "who": ("6", "WHO", ":material/local_hospital:"),
    "vdem": ("7", "V-Dem", ":material/how_to_vote:"),
    "dse": ("8", "Digital Society & Economy", ":material/devices:"),
    "comtrade": ("9", "Comtrade", ":material/directions_boat:"),
}

PAGES = {}
for key, (prefix, title, icon) in PAGE_SPEC.items():
    path = find_page(prefix)
    if path:
        PAGES[key] = st.Page(path, title=title, icon=icon)

pg = st.navigation(
    [
        st.Page(beranda, title="Beranda", icon=":material/home:", default=True),
        *PAGES.values(),
    ]
)

pg.run()

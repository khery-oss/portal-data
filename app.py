import io
import re
import requests
import streamlit as st

st.set_page_config(
    page_title="IndoEcon Explorer",
    page_icon="📊",
    layout="wide"
)

st.title("📊 IE IndoEcon Explorer")
st.markdown(
    "Portal observasi data makroekonomi, ketenagakerjaan, sosial-pendidikan, kesehatan publik, institusi politik, "
    "dan demokrasi Indonesia yang terintegrasi langsung dengan berbagai institusi resmi internasional dan nasional."
)

# =============================================================================
# CATATAN AKADEMIS & PENGGUNAAN RISET (DISCLAIMER)
# =============================================================================
st.info(
    "🎯 **Tujuan Platform & Pedoman Penggunaan Akademis:**\n\n"
    "Website ini dibuat untuk kebutuhan para **peneliti, akademisi, dosen, dan mahasiswa** "
    "dalam mengakses serta mengeksplorasi data resmi Indonesia secara cepat, transparan, dan terbuka.\n\n"
    "* **Rekomendasi Cross-check:** Pengguna sangat disarankan untuk tetap melakukan *cross-check* kembali "
    "ke website utama sumber data resmi seperti yang tercantum pada masing-masing modul.\n"
    "* **Standar Sitasi & Penulisan Sumber:** Dalam penulisan karya ilmiah, skripsi, tesis, jurnal, maupun laporan riset, "
    "penulisan sumber **tetap menggunakan sumber asli** tempat data diterbitkan "
    "(seperti *World Bank, FRED, ILO, UN SDGs, UNESCO, WHO, hingga V-Dem Institute*).\n"
    "* **Koreksi & Masukan:** Apabila terdapat kekeliruan, kesalahan data, atau *error* pada penarikan API/data, "
    "bisa langsung diberitahukan ke email tim pengembang melalui formulir kontak di bawah."
)

st.divider()

st.subheader("📚 Arsitektur Modul Data & Akses Cepat")
st.markdown("Pilih modul di bawah ini atau melalui menu navigasi di bilah sisi kiri:")

# Membuat sistem pintasan berbasis kolom interaktif
col_btn1, col_btn2, col_btn3, col_btn4 = st.columns(4)
with col_btn1:
    st.markdown("🌐 **World Bank**")
    st.caption("Makroekonomi & WDI")
with col_btn2:
    st.markdown("📈 **FRED**")
    st.caption("Moneter & Komoditas")
with col_btn3:
    st.markdown("👷 **ILO**")
    st.caption("Ketenagakerjaan")
with col_btn4:
    st.markdown("🇺🇳 **UN SDGs**")
    st.caption("Pembangunan Global")

col_btn5, col_btn6, col_btn7, _ = st.columns(4)
with col_btn5:
    st.markdown("🎓 **UNESCO**")
    st.caption("Pendidikan & Literasi")
with col_btn6:
    st.markdown("🏥 **WHO**")
    st.caption("Kesehatan Publik")
with col_btn7:
    st.markdown("🗳️ **V-Dem**")
    st.caption("Demokrasi & Institusi")

st.divider()

st.subheader("⚙️ Prinsip Integritas & Transparansi Data")
st.markdown("""
* **Live API & Curated Local Database:** Sebagian besar modul memanfaatkan penarikan *real-time* via API resmi, sementara modul spesifik berukuran masif (seperti V-Dem) menggunakan arsip data terkurasi resmi yang dioptimalkan secara lokal untuk menjamin kecepatan akses web publik.
* **Bebas Manipulasi:** Tidak ada data buatan atau tiruan (*zero hardcoding*). Seluruh angka bersumber mutlak dari publikasi lembaga aslinya.
* **Ekspor Terbuka:** Seluruh data yang ditampilkan dapat diunduh seketika dalam format CSV dan Excel (`.xlsx`) untuk diolah kembali di Stata, R, Python, maupun SPSS.
* **Pengembangan Berkelanjutan:** Platform ini terus berada dalam masa pengembangan aktif guna meningkatkan kemudahan pencarian variabel, memperkaya fitur eksplorasi, serta menyederhanakan pemanfaatan dataset bagi seluruh kalangan akademisi.
""")

st.info("💡 Gunakan bilah navigasi di sebelah kiri untuk masuk ke masing-masing modul.")

st.divider()

# =============================================================================
# KOTAK SARAN, LAPORAN EROR & PERMINTAAN DATA BARU (DENGAN VALIDASI KETAT & FALLBACK)
# =============================================================================
st.subheader("📬 Kotak Saran, Laporan Kendala & Permintaan Data")
st.markdown(
    "Menemukan kekeliruan data, *error* pada sistem, atau membutuhkan seri indikator baru untuk riset Anda? "
    "Kirimkan masukan langsung ke email pengembang melalui formulir di bawah ini."
)

TARGET_EMAIL = "indoecon.project@gmail.com"

# Fungsi validasi email ketat dengan regex
def is_valid_email(email):
    pattern = r"^[\w\.-]+@[\w\.-]+\.\w+$"
    return re.match(pattern, email) is not None

with st.form("feedback_form", clear_on_submit=True):
    col_f1, col_f2 = st.columns(2)
    with col_f1:
        nama_pengirim = st.text_input("Nama Lengkap / Instansi Akademik*", placeholder="Contoh: K. N. Phane (Universitas Indonesia)")
    with col_f2:
        email_pengirim = st.text_input("Alamat Email Pengirim*", placeholder="nama@domain.com")
        
    tipe_pesan = st.selectbox(
        "Kategori Pesan:",
        [
            "Laporan Kesalahan Data / Sistem Error",
            "Permintaan Indikator / Dataset Tambahan",
            "Kritik, Saran & Masukan Metodologi",
            "Lainnya"
        ]
    )
    
    isi_pesan = st.text_area(
        "Detail Laporan / Pesan*",
        placeholder="Jelaskan secara spesifik indikator mana yang mengalami kendala, atau sebutkan dataset yang ingin ditambahkan beserta sumber resminya...",
        height=130
    )
    
    submitted = st.form_submit_button("📩 Kirim Pesan ke Pengembang", type="primary")

    if submitted:
        if not nama_pengirim.strip() or not email_pengirim.strip() or not isi_pesan.strip():
            st.error("Mohon lengkapi Nama, Email, dan Detail Pesan sebelum mengirim.")
        elif not is_valid_email(email_pengirim):
            st.error("Format alamat email tidak valid (pastikan format seperti nama@domain.com tanpa karakter terlarang).")
        else:
            with st.spinner("Mengirimkan pesan ke email pengembang..."):
                endpoint = f"https://formsubmit.co/{TARGET_EMAIL}"
                payload = {
                    "name": nama_pengirim,
                    "email": email_pengirim,
                    "category": tipe_pesan,
                    "message": isi_pesan,
                    "_subject": f"[{tipe_pesan}] Pesan dari IE IndoEcon Explorer",
                    "_captcha": "false"
                }
                headers = {"User-Agent": "Mozilla/5.0"}
                
                try:
                    res = requests.post(endpoint, data=payload, headers=headers, timeout=10)
                    if res.status_code in [200, 302]:
                        st.success("🎉 Terima kasih! Laporan/masukan Anda telah berhasil dikirimkan ke email pengembang.")
                    else:
                        # Fallback jika server formsubmit memblokir
                        st.warning(
                            f"Formulir daring sedang mengalami kendala jaringan (Status: {res.status_code}). "
                            f"Silakan kirimkan laporan Anda secara langsung melalui tautan email berikut: "
                            f"[Kirim Email Manual](mailto:{TARGET_EMAIL}?subject=%5B{tipe_pesan}%5D%20IE%20IndoEcon&body=Nama:%20{nama_pengirim}%0D%0AEmail:%20{email_pengirim}%0D%0APesan:%20{isi_pesan})"
                        )
                except Exception as e:
                    # Fallback total jika terjadi exception / network block
                    st.warning(
                        "Koneksi ke server pengiriman laporan dibatasi oleh jaringan. "
                        f"Anda tetap dapat mengirimkan masukan secara langsung lewat tombol di bawah ini:"
                    )
                    st.markdown(f"📧 **Email Langsung Pengembang:** `{TARGET_EMAIL}`")

# =============================================================================
# FOOTER PROFESIONAL (METADATA & COPYRIGHT)
# =============================================================================
st.markdown("---")
col_foot1, col_foot2, col_foot3 = st.columns(3)
with col_foot1:
    st.markdown("**IE IndoEcon Explorer**")
    st.markdown("Platform Riset & Observasi Data Publik")
with col_foot2:
    st.markdown("**Pengembang & Periset**")
    st.markdown("👩‍💻 **K. N. Phane**")
with col_foot3:
    st.markdown("**Arsip Akademik**")
    st.markdown("© 2025–2026 • Pengembangan Aktif")

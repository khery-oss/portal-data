# Kamus Data Terstruktur: Digital Society Project (DSP) & UNCTAD Digital Economy

Kamus data ini disusun berdasarkan dokumen metodologi dan codebook yang terdapat pada sumber notebook, yaitu **DSP-Codebook-v8.pdf** dan **UNCTAD_DE.pdf**. Dokumen ini dirancang khusus untuk referensi teoretis dan teknis dalam pengembangan aplikasi analisis makroekonomi dan kebijakan publik.

---

## BAGIAN 1: DIGITAL SOCIETY PROJECT (DSP)

Digital Society Project (DSP) mengumpulkan data menggunakan survei berbasis penilaian ahli (*expert-coded surveys*) [8]. Semua variabel DSP adalah variabel **Tipe C** (*Type C*), yang dinilai oleh para Ahli Negara (*Country Experts*)—biasanya akademisi atau profesional dengan pengetahuan mendalam tentang negara tersebut [11]. Model pengukuran V-Dem kemudian menggabungkan penilaian para ahli ini dengan memperhitungkan ketidaksepakatan dan kesalahan pengukuran guna menghasilkan estimasi titik akhir (*model estimates*) pada skala interval terstandar (biasanya antara -5 dan 5) [12].

Berikut adalah kamus data untuk variabel-variabel kunci yang diminta:

### 1. Government Dissemination of False Information Domestic (`v2smgovdom`)
*   **Nama Variabel:** Government dissemination of false information domestic (C) [3]
*   **Pertanyaan Kuesioner Asli:**
    > *"How often do the government and its agents use social media to disseminate misleading viewpoints or false information to influence its own population?"* [45]
*   **Skala Pengukuran:** Ordinal (dikonversi menjadi interval melalui model pengukuran Bayesian IRT) [46]. Variabel asli memiliki rentang nilai kategori **0 s.d. 4** [45].
*   **Arti Skor (Kategori):**
    *   **0 (Extremely often):** Pemerintah menyebarkan informasi palsu pada semua isu politik utama (*all key political issues*) [45].
    *   **1 (Often):** Pemerintah menyebarkan informasi palsu pada banyak isu politik utama (*many key political issues*) [45].
    *   **2 (About half the time):** Pemerintah menyebarkan informasi palsu pada sebagian isu politik utama, tetapi tidak pada isu lainnya [45].
    *   **3 (Rarely):** Pemerintah menyebarkan informasi palsu hanya pada sedikit isu politik utama (*only a few key political issues*) [45].
    *   **4 (Never, or almost never):** Pemerintah tidak pernah atau hampir tidak pernah menyebarkan informasi palsu pada isu-isus politik utama [45].

### 2. Party Dissemination of False Information Domestic (`v2smpardom`)
*   **Nama Variabel:** Party dissemination of false information domestic (C) [3]
*   **Pertanyaan Kuesioner Asli:**
    > *"How often do major political parties and candidates for office use social media to disseminate misleading viewpoints or false information to influence their own population?"* [48-49]
*   **Skala Pengukuran:** Ordinal (dikonversi menjadi interval oleh model pengukuran) [50]. Skala asli bernilai **0 s.d. 4** [49].
*   **Arti Skor (Kategori):**
    *   **0 (Extremely often):** Partai-partai politik utama dan kandidat menyebarkan informasi palsu pada semua isu politik utama [49].
    *   **1 (Often):** Partai-partai politik utama dan kandidat menyebarkan informasi palsu pada banyak isu politik utama [49].
    *   **2 (About half the time):** Partai-partai politik utama dan kandidat menyebarkan informasi palsu pada sebagian isu politik utama, tetapi tidak pada isu lainnya [49].
    *   **3 (Rarely):** Partai-partai politik utama dan kandidat menyebarkan informasi palsu hanya pada sedikit isu politik utama [49].
    *   **4 (Never, or almost never):** Partai-partai politik utama dan kandidat tidak pernah atau hampir tidak pernah menyebarkan informasi palsu pada isu-isu politik utama [49].

### 3. Government Internet Filtering Capacity (`v2smgovfilcap`)
*   **Nama Variabel:** Government Internet filtering capacity (C) [4]
*   **Pertanyaan Kuesioner Asli:**
    > *"Independent of whether it actually does so in practice, does the government have the technical capacity to censor information (text, audio, images, or video) on the Internet by filtering (blocking access to certain websites) if it decided to?"* [56-57]
*   **Skala Pengukuran:** Ordinal (0 s.d. 3), dikonversi menjadi interval [58].
*   **Arti Skor (Kategori):**
    *   **0:** Pemerintah sama sekali tidak memiliki kapasitas teknis untuk memblokir akses ke situs apa pun di Internet [57].
    *   **1:** Pemerintah memiliki kapasitas terbatas untuk memblokir akses ke beberapa situs (*a few sites*) di Internet [57].
    *   **2:** Pemerintah memiliki kapasitas yang memadai untuk memblokir akses ke sebagian besar, tetapi tidak semua, situs tertentu di Internet jika diinginkan [57-58].
    *   **3:** Pemerintah memiliki kapasitas penuh untuk memblokir akses ke situs mana pun di Internet jika diinginkan [58].

### 4. Government Internet Shutdowns (`v2smgovshut`)
*   **Nama Variabel:** Government Internet shut down in practice (C) [4]
*   **Pertanyaan Kuesioner Asli:**
    > *"How often does the government shut down domestic access to the Internet?"* [62]
*   **Skala Pengukuran:** Ordinal (0 s.d. 4), dikonversi menjadi interval [64].
*   **Arti Skor (Kategori):**
    *   **0 (Extremely often):** Merupakan praktik rutin bagi pemerintah untuk mematikan akses domestik ke Internet [63].
    *   **1 (Often):** Pemerintah mematikan akses domestik ke Internet berkali-kali (*numerous times*) tahun ini [63].
    *   **2 (Sometimes):** Pemerintah mematikan akses domestik ke Internet beberapa kali (*several times*) tahun ini [63].
    *   **3 (Rarely):** Jarang terjadi, tetapi ada beberapa kesempatan sepanjang tahun ketika pemerintah mematikan akses domestik ke Internet [63].
    *   **4 (Never, or almost never):** Pemerintah biasanya tidak mencampuri atau mengganggu akses domestik ke Internet [63].

### 5. Privacy Protection by Law Exists (`v2smprivex`)
*   **Catatan Klarifikasi Metodologis:** Berdasarkan kode resmi dalam DSP Codebook, variabel `v2smprivex` merujuk pada **"Keberadaan kerangka hukum perlindungan privasi pengguna internet"** (*Privacy protection by law exists*), bukan perlindungan terhadap pelecehan sektor swasta (*private sector online harassment*) [5, 78, 209]. Pelecehan kelompok secara daring dicatat dalam variabel terpisah seperti `v2smhargr` (*Online harassment groups*) [7, 94].
*   **Nama Variabel:** Privacy protection by law exists (C) [5]
*   **Pertanyaan Kuesioner Asli:**
    > *"Does a legal framework to protect Internet users’ privacy and their data exist?"* [78, 209]
*   **Skala Pengukuran:** Dikotomis (*Yes/No* atau skala biner **0 s.d. 1**) [79, 210].
*   **Arti Skor:**
    *   **0 (No):** Tidak ada kerangka hukum perlindungan privasi (jika bernilai 0, maka pengisian kuesioner otomatis melompat melewati pertanyaan konten perlindungan privasi `v2smprivcon` langsung menuju `v2smregcap`) [79, 210].
    *   **1 (Yes):** Ada kerangka hukum yang melindungi privasi dan data pengguna Internet [79, 210].

### 6. Defamation and Hate Speech Protection (`v2smlawpr`)
*   **Nama Variabel:** Defamation protection (C) [6]
*   **Pertanyaan Kuesioner Asli:**
    > *"Does the legal framework provide protection against defamatory online content, or hate speech?"* [85-86, 216-217]
*   **Skala Pengukuran:** Ordinal (0 s.d. 4), dikonversi menjadi interval [87, 218].
*   **Arti Skor (Kategori):**
    *   **0 (No):** Hukum tidak memberikan perlindungan sama sekali terhadap pencemaran nama baik (*defamation*) dan ujaran kebencian (*hate speech*) di Internet [86, 217].
    *   **1 (Not really):** Hukum memberikan perlindungan yang lemah dan hanya dalam keadaan yang sangat terbatas [86, 217].
    *   **2 (Somewhat):** Hukum memberikan perlindungan tertentu, tetapi dalam keadaan terbatas atau hanya untuk kelompok masyarakat tertentu saja [86, 217].
    *   **3 (Mostly):** Hukum memberikan perlindungan dalam banyak keadaan dan bagi sebagian besar kelompok masyarakat [86, 217].
    *   **4 (Yes):** Hukum memberikan perlindungan komprehensif terhadap pencemaran nama baik dan ujaran kebencian di Internet [86, 217].

---

## BAGIAN 2: UNCTAD DIGITAL ECONOMY (UNCTAD_DE)

Informasi berikut disusun berdasarkan dokumen metodologi dan ringkasan dataset **UNCTAD_DE.pdf**:

### 1. Definisi dan Cakupan Utama Indikator Kesiapan Ekonomi Digital
*   **Definisi Umum:** UNCTAD Digital Economy Database adalah repositori data khusus yang dikelola oleh Konferensi PBB mengenai Perdagangan dan Pembangunan (UNCTAD). Basis data ini menyediakan statistik global, regional, dan tingkat negara mengenai ekonomi digital, dengan fokus perhatian khusus pada negara-negara berkembang untuk mendukung pembuatan kebijakan terkait e-commerce, perdagangan digital, infrastruktur TIK, dan transformasi digital secara luas [123, 385].
*   **Cakupan Indikator Utama yang Tersedia:**
    *   **Konektivitas (*Connectivity* - `P5_000001`):** Profil infrastruktur telekomunikasi dan akses internet dasar [125, 387].
    *   **Adopsi Digital (*Digital Adoption* - `P5_000023`):** Penggunaan teknologi informasi oleh masyarakat dan bisnis [125, 387].
    *   **Layanan Digital (*Digital Services* - `P5_000004`):** Ekosistem dan penyediaan jasa berbasis internet [124, 386].
    *   **Industri TIK (*ICT Industry* - `P5_000016`):** Kinerja sektor industri penghasil barang dan jasa teknologi informasi [125, 387].
    *   **Industri dan Pekerjaan Digital (*Digital Industry and Jobs* - `P5_000003`):** Pasar tenaga kerja dan peluang kerja di sektor digital [124, 386].
*   **Dataset Terkait dalam Lingkup UNCTADstat:** Perdagangan barang internasional, perdagangan jasa internasional, investasi asing langsung (FDI), tren ekonomi, komoditas, transportasi laut, ekonomi digital, serta populasi dan angkatan kerja [123, 385].

### 2. Satuan Pengukuran Standar
*   **Keterbatasan Dokumen Sumber:** File PDF `UNCTAD_DE.pdf` yang disediakan dalam notebook ini **merupakan dokumen ringkasan metadata (dataset profile)** dan tidak merinci satuan pengukuran untuk masing-masing indikator individual secara spesifik (seperti persentase populasi, nilai nominal USD, indeks, atau rasio) [123-131, 385-393].
*   **Karakteristik Teknis Data:**
    *   **Format Database:** Tipe proyek data ini berupa basis data deret waktu (*timeseries-db*) [123, 385].
    *   **Rentang Waktu Coverage:** Mencakup data tahunan (*annual update*) untuk periode tahun **2010 hingga 2023** [124, 130, 386, 391].

### 3. Batasan Metodologis dan Catatan Penting Peneliti
Peneliti yang mengutip atau menggunakan data dari subset database UNCTAD_DE ini wajib memperhatikan beberapa poin penting berikut:
1.  **Subset Data Terbatas:** Koleksi database di sumber notebook ini **hanya mencakup subset (sebagian kecil) indikator** dari keseluruhan dataset sumber asli UNCTADstat [124, 386]. Peneliti harus waspada bahwa beberapa indikator makro mungkin memerlukan pencarian data pelengkap langsung ke portal UNCTADstat.
2.  **Batasan Rentang Waktu:** Data yang tersedia dibatasi pada tren historis antara tahun **2010 s.d. 2023** [130, 391].
3.  **Ketentuan Hak Cipta & Lisensi:** Seluruh data didistribusikan di bawah lisensi **Creative Commons Attribution 3.0 IGO (CC BY-3.0 IGO)** [130, 392]. Peneliti bebas menyalin, menyebarluaskan, dan mendistribusikan data ini selama mencantumkan sitasi dan atribusi yang benar kepada United Nations Conference on Trade and Development [130, 392].
4.  **Persyaratan Atribusi Sitasi Standar:** Untuk menjaga validitas ilmiah, peneliti wajib menggunakan format sitasi berikut saat mempublikasikan hasil riset:
    > *United Nations Conference on Trade and Development (UNCTAD). UNCTADstat Database. Accessed [date]. For specific publications or datasets, include the title and year (e.g., UNCTAD Handbook of Statistics, 2024).* [131, 262, 393]

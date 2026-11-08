import base64
import html
from io import BytesIO

import matplotlib.pyplot as plt
import pandas as pd
import streamlit as st

# ==========================================
# KONFIGURASI APLIKASI
# ==========================================

APP_VERSION = "2.0.0"

st.set_page_config(
    page_title="Audit COBIT 5 Indomaret",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Streamlit versi baru memakai width="stretch", versi lama use_container_width.
try:
    from packaging.version import Version
    _API_BARU = Version(st.__version__) >= Version("1.50.0")
except Exception:
    _API_BARU = False

STRETCH = {"width": "stretch"} if _API_BARU else {"use_container_width": True}

# ==========================================
# DESIGN TOKENS
# ==========================================

WARNA = {
    "navy": "#142D4E",
    "emerald": "#16845B",
    "bg": "#F4F7F9",
    "card": "#FFFFFF",
    "border": "#E2E8F0",
    "text": "#1E293B",
    "muted": "#64748B",
    "success": "#10B981",
    "warning": "#F59E0B",
    "danger": "#EF4444",
}

AMBANG_TINGGI = 80
AMBANG_SEDANG = 50

DOMAIN = ["EDM", "APO", "BAI", "DSS", "MEA"]

NAMA_DOMAIN = {
    "EDM": "Evaluate, Direct and Monitor",
    "APO": "Align, Plan and Organise",
    "BAI": "Build, Acquire and Implement",
    "DSS": "Deliver, Service and Support",
    "MEA": "Monitor, Evaluate and Assess",
}

PILIHAN = ["Belum diisi", "Ya", "Sebagian", "Tidak", "TDV", "TR"]

WARNA_JAWABAN = {
    "Ya": WARNA["success"],
    "Sebagian": WARNA["warning"],
    "Tidak": WARNA["danger"],
    "TDV": "#94A3B8",
    "TR": "#CBD5E1",
    "Belum diisi": WARNA["border"],
}

MENU = [
    "Dashboard",
    "Kuesioner Audit",
    "Hasil Penilaian",
    "Temuan dan Rekomendasi",
    "Laporan Audit"
]

IKON_MENU = [
    "<rect x='3' y='3' width='7' height='7'/><rect x='14' y='3' width='7' height='7'/><rect x='14' y='14' width='7' height='7'/><rect x='3' y='14' width='7' height='7'/>",
    "<path d='M16 4h2a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2V6a2 2 0 0 1 2-2h2'/><rect x='8' y='2' width='8' height='4' rx='1' ry='1'/><path d='M9 14l2 2 4-4'/>",
    "<line x1='18' y1='20' x2='18' y2='10'/><line x1='12' y1='20' x2='12' y2='4'/><line x1='6' y1='20' x2='6' y2='14'/>",
    "<path d='M4 15s1-1 4-1 5 2 8 2 4-1 4-1V3s-1 1-4 1-5-2-8-2-4 1-4 1z'/><line x1='4' y1='22' x2='4' y2='15'/>",
    "<path d='M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z'/><polyline points='14 2 14 8 20 8'/><line x1='16' y1='13' x2='8' y2='13'/><line x1='16' y1='17' x2='8' y2='17'/>",
]

CSS_TEMPLATE = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

:root {
  --navy: __NAVY__; --emerald: __EMERALD__; --bg: __BG__; --card: __CARD__;
  --border: __BORDER__; --text: __TEXT__; --muted: __MUTED__;
}

/* ---------- Dasar ---------- */
.stApp, .stApp p, .stApp label, .stApp input, .stApp textarea, .stApp button,
.stApp h1, .stApp h2, .stApp h3, .stApp td, .stApp th {
  font-family: 'Inter', -apple-system, 'Segoe UI', Roboto, sans-serif;
}
.stApp { background: var(--bg); color: var(--text); }
header[data-testid="stHeader"] { background: transparent; }
footer, [data-testid="stDecoration"] { visibility: hidden; height: 0; }
.block-container { padding: 2rem 2.5rem 4rem; max-width: 1280px; }

/* ---------- Sidebar ---------- */
section[data-testid="stSidebar"] { background: var(--navy) !important; border-right: none; }
section[data-testid="stSidebar"] > div { background: var(--navy) !important; }

/* Paksa teks di sidebar jadi putih/terang */
section[data-testid="stSidebar"] p, 
section[data-testid="stSidebar"] div, 
section[data-testid="stSidebar"] span {
    color: rgba(255, 255, 255, 0.85) !important;
}

section[data-testid="stSidebar"][aria-expanded="true"] {
  width: 288px !important; min-width: 288px !important; max-width: 288px !important;
}
section[data-testid="stSidebar"] [data-testid="stSidebarCollapseButton"] button,
section[data-testid="stSidebar"] [data-testid="stSidebarCollapseButton"] svg {
  color: rgba(255,255,255,.7) !important;
}
.brand {
  display: flex; align-items: center; gap: 12px;
  padding: 4px 6px 20px; margin-bottom: 20px;
  border-bottom: 1px solid rgba(255,255,255,.12);
}
.brand-logo {
  width: 42px; height: 42px; flex: none; border-radius: 12px;
  background: var(--emerald); display: flex; align-items: center; justify-content: center;
}
.brand-title { color: #ffffff !important; font-weight: 700; font-size: 1.05rem; letter-spacing: .05em; line-height: 1.2; }
.brand-sub { color: rgba(255,255,255,.6) !important; font-size: .74rem; line-height: 1.3; margin-top: 2px; }
.nav-caption {
  color: rgba(255,255,255,.45) !important; font-size: .68rem; letter-spacing: .14em;
  font-weight: 600; padding: 0 10px 8px;
}
section[data-testid="stSidebar"] [data-testid="stRadio"] > label { display: none; }
section[data-testid="stSidebar"] div[role="radiogroup"] { gap: 6px; }
section[data-testid="stSidebar"] div[role="radiogroup"] > label {
  position: relative; display: flex; align-items: center; gap: 12px;
  padding: 12px 14px; margin: 0; border-radius: 10px; cursor: pointer;
  transition: all .2s ease;
  background: transparent !important;
}
section[data-testid="stSidebar"] div[role="radiogroup"] > label > div:first-child:not(:has([data-testid="stMarkdownContainer"])) {
  display: none;
}
section[data-testid="stSidebar"] div[role="radiogroup"] > label p {
  font-size: .92rem; font-weight: 500; margin: 0;
}

/* Ikon Menu Sidebar (DIPERBAIKI MENGGUNAKAN BACKGROUND-IMAGE 100% SUPPORT) */
section[data-testid="stSidebar"] div[role="radiogroup"] > label::before {
  content: ""; width: 20px; height: 20px; flex: none; 
  background-image: var(--ico);
  background-size: contain;
  background-repeat: no-repeat;
  background-position: center;
  opacity: 0.6;
  transition: all 0.2s ease;
}

/* Efek Hover */
section[data-testid="stSidebar"] div[role="radiogroup"] > label:hover { 
    background: rgba(255,255,255,.08) !important; 
}
section[data-testid="stSidebar"] div[role="radiogroup"] > label:hover p { 
    color: #ffffff !important; 
}
section[data-testid="stSidebar"] div[role="radiogroup"] > label:hover::before { 
    opacity: 1; 
}

/* Menu Aktif */
section[data-testid="stSidebar"] div[role="radiogroup"] > label:has(input:checked) { 
    background: rgba(255,255,255,.15) !important; 
}
section[data-testid="stSidebar"] div[role="radiogroup"] > label:has(input:checked) p { 
    font-weight: 600 !important; color: #ffffff !important; 
}
section[data-testid="stSidebar"] div[role="radiogroup"] > label:has(input:checked)::before { 
    opacity: 1; 
}
section[data-testid="stSidebar"] div[role="radiogroup"] > label:has(input:checked)::after {
  content: ""; position: absolute; left: 0; top: 10px; bottom: 10px; width: 4px;
  border-radius: 0 4px 4px 0; background: var(--emerald);
}

.sb-footer {
  position: fixed; left: 0; bottom: 0; width: 288px; box-sizing: border-box;
  padding: 14px 24px 18px; border-top: 1px solid rgba(255,255,255,.1);
  color: rgba(255,255,255,.5) !important; font-size: .72rem; line-height: 1.55; background: var(--navy);
}
.sb-footer b { color: rgba(255,255,255,.8) !important; font-weight: 600; }

/* ---------- Header halaman ---------- */
.page-head {
  display: flex; justify-content: space-between; align-items: flex-end; gap: 16px;
  margin-bottom: 24px; padding-bottom: 18px; border-bottom: 1px solid var(--border);
}
.crumb { font-size: .74rem; color: var(--muted); letter-spacing: .05em; margin-bottom: 6px; text-transform: uppercase; }
.crumb b { color: var(--emerald); font-weight: 600; }
.page-title { font-size: 1.75rem; font-weight: 700; color: var(--navy); margin: 0; padding: 0; line-height: 1.2; letter-spacing: -.02em; }
.page-sub { color: var(--muted); font-size: .95rem; margin-top: 6px; }
.chip {
  display: inline-flex; align-items: center; gap: 8px; padding: 6px 14px; border-radius: 999px;
  background: #fff; border: 1px solid var(--border); font-size: .78rem; color: var(--text);
  white-space: nowrap; font-weight: 600; box-shadow: 0 1px 2px rgba(0,0,0,0.05);
}
.chip i { width: 8px; height: 8px; border-radius: 50%; background: var(--emerald); display: inline-block; }

/* ---------- Kartu & Bayangan (Pop-up Effect) ---------- */
div[class*="st-key-card_"], .kpi {
  background: #ffffff; 
  border: 1px solid var(--border); 
  border-radius: 12px;
  padding: 22px 24px; 
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05), 0 2px 4px -1px rgba(0, 0, 0, 0.03);
  transition: box-shadow 0.2s ease, transform 0.2s ease;
}
div[class*="st-key-card_"]:hover, .kpi:hover {
  box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.08), 0 4px 6px -2px rgba(0, 0, 0, 0.04);
  transform: translateY(-2px);
}
.section-title { font-size: 1.05rem; font-weight: 600; color: var(--navy); margin: 0 0 4px; }
.section-sub { font-size: .85rem; color: var(--muted); margin: 0 0 16px; }

.kpi-label { font-size: .72rem; font-weight: 700; letter-spacing: .08em; text-transform: uppercase; color: var(--muted); }
.kpi-value { font-size: 2.2rem; font-weight: 700; color: var(--navy); line-height: 1.15; margin-top: 8px; }
.kpi-value small { font-size: 1rem; color: var(--muted); font-weight: 500; margin-left: 4px; }
.kpi-sub { font-size: .8rem; color: var(--muted); margin-top: 8px; min-height: 1.2em; display: flex; align-items: center; }
.bar { height: 6px; background: #EEF2F6; border-radius: 999px; overflow: hidden; margin-top: 14px; }
.bar > span { display: block; height: 100%; background: var(--emerald); border-radius: 999px; }

.badge { display: inline-block; padding: 4px 10px; border-radius: 6px; font-size: .72rem; font-weight: 600; }
.badge.success { background: #ECFDF5; color: #047857; border: 1px solid #A7F3D0; }
.badge.warning { background: #FFFBEB; color: #B45309; border: 1px solid #FDE68A; }
.badge.danger  { background: #FEF2F2; color: #B91C1C; border: 1px solid #FECACA; }
.badge.neutral { background: #F1F5F9; color: #64748B; border: 1px solid #E2E8F0; }

.dom-row { display: flex; align-items: center; gap: 14px; padding: 12px 0; border-bottom: 1px solid var(--border); }
.dom-row:last-child { border-bottom: none; }
.dom-code { width: 44px; flex: none; font-weight: 700; color: var(--navy); font-size: .9rem; }
.dom-main { flex: 1; min-width: 0; }
.dom-name { font-size: .8rem; color: var(--muted); display: flex; justify-content: space-between; gap: 8px; }
.dom-count { font-size: .8rem; color: var(--navy); font-weight: 700; white-space: nowrap; }

.stack { display: flex; height: 14px; border-radius: 999px; overflow: hidden; background: #EEF2F6; }
.stack > span { display: block; height: 100%; transition: flex 0.3s ease; }
.legend { display: flex; flex-wrap: wrap; gap: 10px 20px; margin-top: 14px; font-size: .85rem; color: var(--text); }
.legend i { display: inline-block; width: 10px; height: 10px; border-radius: 50%; margin-right: 6px; }
.legend b { font-weight: 700; margin-left: 4px; color: var(--navy); }

.empty {
  border: 2px dashed var(--border); border-radius: 12px; padding: 40px 20px;
  text-align: center; color: var(--muted); font-size: .9rem; background: #F8FAFC;
}

/* ---------- Kuesioner ---------- */
.q-head { display: flex; align-items: flex-start; gap: 14px; margin-bottom: 8px; }
.q-num {
  flex: none; width: 32px; height: 32px; border-radius: 8px; background: var(--navy); color: #fff;
  font-weight: 700; font-size: .85rem; display: flex; align-items: center; justify-content: center;
  box-shadow: 0 2px 4px rgba(20,45,78,0.2);
}
.q-body { flex: 1; min-width: 0; }
.q-meta { display: flex; flex-wrap: wrap; gap: 8px; margin-bottom: 8px; }
.tag { font-size: .7rem; font-weight: 600; padding: 4px 10px; border-radius: 6px; background: #F1F5F9; color: var(--navy); border: 1px solid var(--border); }
.tag.proc { background: #ECFDF5; color: #047857; border-color: #A7F3D0; }
.q-aspek { font-weight: 700; color: var(--navy); font-size: 1rem; }
.q-text { color: var(--text); font-size: .95rem; line-height: 1.6; margin-top: 4px; }
.dom-head { margin: 20px 0 16px; border-bottom: 2px solid var(--emerald); padding-bottom: 8px; display: inline-block; }
.dom-head b { color: var(--navy); font-size: 1.1rem; }
.dom-head span { color: var(--muted); font-size: .85rem; margin-left: 10px; }

/* ---------- Ringkasan laporan / temuan ---------- */
.kv { display: flex; justify-content: space-between; gap: 16px; padding: 12px 0; border-bottom: 1px dashed var(--border); font-size: .9rem; }
.kv:last-child { border-bottom: none; }
.kv span { color: var(--muted); }
.kv b { color: var(--text); font-weight: 600; text-align: right; }
.finding-label { font-size: .75rem; font-weight: 700; letter-spacing: .08em; text-transform: uppercase; color: var(--emerald); margin: 16px 0 4px; }
.finding-text { font-size: .95rem; line-height: 1.6; color: var(--text); background: #F8FAFC; padding: 12px; border-radius: 8px; border: 1px solid var(--border); }

/* ---------- Komponen Streamlit ---------- */
[data-testid="stForm"] { border: none; padding: 0; background: transparent; }
[data-testid="stWidgetLabel"] p { font-size: .8rem; font-weight: 600; color: var(--navy); }
div[data-baseweb="input"] > div, div[data-baseweb="textarea"] > div, div[data-baseweb="select"] > div {
  border-radius: 8px; border-color: var(--border); background: #F8FAFC; transition: border 0.2s, box-shadow 0.2s;
}
div[data-baseweb="input"] > div:focus-within, div[data-baseweb="textarea"] > div:focus-within, div[data-baseweb="select"] > div:focus-within {
  border-color: var(--emerald); box-shadow: 0 0 0 1px var(--emerald); background: #fff;
}
[data-testid="stAlert"] { border-radius: 10px; border: 1px solid var(--border); box-shadow: 0 2px 4px rgba(0,0,0,0.02); }
[data-testid="stDataFrame"] { border: 1px solid var(--border); border-radius: 12px; overflow: hidden; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05); }

div[data-baseweb="tab-list"] { gap: 8px; border-bottom: 2px solid var(--border); }
button[data-baseweb="tab"] { height: 48px; padding: 0 24px; background: transparent; }
button[data-baseweb="tab"] p { color: var(--muted); font-weight: 600; font-size: .9rem; transition: color 0.2s; }
button[data-baseweb="tab"]:hover p { color: var(--navy); }
button[data-baseweb="tab"][aria-selected="true"] p { color: var(--emerald); }
div[data-baseweb="tab-highlight"] { background-color: var(--emerald) !important; height: 3px; border-radius: 3px 3px 0 0; }

button[kind="primary"], button[kind="primaryFormSubmit"],
[data-testid="stBaseButton-primary"], [data-testid="stBaseButton-primaryFormSubmit"],
[data-testid="stDownloadButton"] button {
  background: var(--emerald); border: 1px solid var(--emerald); color: #fff;
  border-radius: 8px; font-weight: 600; min-height: 48px; font-size: .95rem;
  box-shadow: 0 4px 6px -1px rgba(16, 185, 129, 0.2); transition: all 0.2s;
}
button[kind="primary"]:hover, button[kind="primaryFormSubmit"]:hover,
[data-testid="stBaseButton-primary"]:hover, [data-testid="stBaseButton-primaryFormSubmit"]:hover,
[data-testid="stDownloadButton"] button:hover {
  background: #047857; border-color: #047857; color: #fff;
  box-shadow: 0 6px 8px -1px rgba(16, 185, 129, 0.3); transform: translateY(-1px);
}

@media (max-width: 1100px) {
  .block-container { padding: 1.5rem 1rem 3rem; }
  .page-head { flex-direction: column; align-items: flex-start; }
}
</style>
"""

# ==========================================
# DATA KUESIONER COBIT 5
# ==========================================

data = [
    ("EDM", "EDM03", "Ensure Risk Optimisation", "Pengawasan risiko persediaan",
     "Apakah terdapat mekanisme pada tingkat tata kelola untuk meninjau risiko TI yang dapat mengganggu pencatatan, ketersediaan, atau keakuratan data persediaan?"),
    ("EDM", "EDM03", "Ensure Risk Optimisation", "Arahan toleransi risiko",
     "Apakah arahan atau batas toleransi risiko terkait gangguan layanan dan ketidaktepatan data persediaan telah ditetapkan oleh pihak yang berwenang?"),
    ("EDM", "EDM03", "Ensure Risk Optimisation", "Penetapan tanggung jawab pengawasan",
     "Apakah tanggung jawab pihak yang mengawasi risiko sistem informasi persediaan telah ditetapkan dan didokumentasikan?"),
    ("EDM", "EDM03", "Ensure Risk Optimisation", "Evaluasi respons risiko",
     "Apakah pihak yang berwenang menerima dan mengevaluasi laporan mengenai respons atas risiko utama sistem persediaan?"),
    ("EDM", "EDM03", "Ensure Risk Optimisation", "Pemantauan risiko residual",
     "Apakah risiko residual setelah tindakan pengendalian sistem persediaan ditinjau dan dilaporkan secara berkala kepada pihak pengarah/pengawas?"),

    ("APO", "APO12", "Manage Risk", "Identifikasi risiko",
     "Apakah risiko pada siklus data persediaan—mulai penerimaan, penyimpanan, distribusi, penjualan, retur, hingga penyesuaian—diidentifikasi dan dicatat?"),
    ("APO", "APO12", "Manage Risk", "Analisis dan penilaian risiko",
     "Apakah risiko selisih stok, transaksi tidak lengkap, akses tidak sah, dan gangguan sistem dianalisis berdasarkan kemungkinan serta dampaknya?"),
    ("APO", "APO12", "Manage Risk", "Rencana perlakuan risiko",
     "Apakah risiko sistem persediaan yang telah dinilai mempunyai rencana perlakuan, penanggung jawab, dan target penyelesaian?"),
    ("APO", "APO13", "Manage Security", "Kebijakan keamanan informasi",
     "Apakah kebijakan keamanan informasi yang mencakup perlindungan data persediaan ditetapkan, disetujui, dikomunikasikan, dan ditinjau?"),
    ("APO", "APO13", "Manage Security", "Perencanaan sistem manajemen keamanan",
     "Apakah ruang lingkup, sasaran, dan tanggung jawab pengelolaan keamanan informasi untuk sistem persediaan telah ditentukan?"),

    ("BAI", "BAI06", "Manage Changes", "Permintaan dan pencatatan perubahan",
     "Apakah setiap perubahan aplikasi, konfigurasi, atau parameter yang memengaruhi data persediaan dicatat melalui permintaan perubahan yang dapat ditelusuri?"),
    ("BAI", "BAI06", "Manage Changes", "Penilaian dampak perubahan",
     "Apakah dampak perubahan terhadap transaksi, saldo stok, integrasi, dan laporan persediaan dinilai sebelum perubahan disetujui?"),
    ("BAI", "BAI06", "Manage Changes", "Pengujian sebelum penerapan",
     "Apakah perubahan sistem persediaan diuji terlebih dahulu dan hasil pengujiannya didokumentasikan sebelum diterapkan?"),
    ("BAI", "BAI09", "Manage Assets", "Inventaris aset TI",
     "Apakah aset TI yang mendukung sistem persediaan dicatat dalam inventaris dengan identitas, lokasi, pemilik, dan statusnya?"),
    ("BAI", "BAI09", "Manage Assets", "Pemeliharaan dan siklus hidup aset",
     "Apakah kondisi, pemeliharaan, dan status penggunaan aset TI pendukung persediaan ditinjau serta diperbarui secara berkala?"),

    ("DSS", "DSS01", "Manage Operations", "Pemantauan operasi sistem",
     "Apakah operasi layanan atau infrastruktur yang mendukung sistem persediaan dipantau untuk mendeteksi kegagalan dan penurunan kinerja?"),
    ("DSS", "DSS01", "Manage Operations", "Penanganan gangguan operasional",
     "Apakah gangguan yang memengaruhi transaksi persediaan dicatat, diklasifikasikan, ditangani, dan ditutup dengan dokumentasi?"),
    ("DSS", "DSS05", "Manage Security Services", "Pengelolaan hak akses",
     "Apakah pemberian, perubahan, dan pencabutan hak akses pengguna ke sistem/data persediaan didasarkan pada otorisasi dan kebutuhan tugas?"),
    ("DSS", "DSS05", "Manage Security Services", "Peninjauan akses dan aktivitas",
     "Apakah hak akses dan aktivitas pengguna yang berisiko terhadap perubahan data persediaan ditinjau secara berkala?"),
    ("DSS", "DSS06", "Manage Business Process Controls", "Validasi dan otorisasi transaksi",
     "Apakah sistem/prosedur pengendalian memvalidasi kelengkapan dan otorisasi transaksi penerimaan, pengeluaran, retur, serta penyesuaian stok?"),

    ("MEA", "MEA01", "Monitor, Evaluate and Assess Performance and Conformance", "Penetapan indikator kinerja",
     "Apakah indikator kinerja sistem persediaan, seperti akurasi stok, selisih, barang kosong, dan ketepatan pencatatan, ditetapkan beserta definisinya?"),
    ("MEA", "MEA01", "Monitor, Evaluate and Assess Performance and Conformance", "Pengumpulan dan validasi data kinerja",
     "Apakah data untuk mengukur kinerja sistem persediaan dikumpulkan dan diperiksa keandalan serta konsistensinya sebelum dilaporkan?"),
    ("MEA", "MEA01", "Monitor, Evaluate and Assess Performance and Conformance", "Pelaporan kinerja dan kesesuaian",
     "Apakah hasil pemantauan kinerja dan kesesuaian pengendalian persediaan dilaporkan kepada pihak yang berwenang secara berkala?"),
    ("MEA", "MEA01", "Monitor, Evaluate and Assess Performance and Conformance", "Analisis penyimpangan",
     "Apakah penyimpangan terhadap target kinerja atau ketentuan pengendalian persediaan dianalisis untuk mengetahui penyebabnya?"),
    ("MEA", "MEA01", "Monitor, Evaluate and Assess Performance and Conformance", "Tindak lanjut hasil pemantauan",
     "Apakah tindakan korektif atas penyimpangan kinerja sistem persediaan ditetapkan, dipantau, dan dievaluasi penyelesaiannya?")
]

df = pd.DataFrame(
    data,
    columns=["Domain", "Kode Proses", "Nama Proses", "Aspek", "Pertanyaan"]
)

N = len(df)

# ==========================================
# INISIALISASI SESSION
# ==========================================

if "jawaban" not in st.session_state:
    st.session_state.jawaban = {
        i: "Belum diisi" for i in range(N)
    }

if "bukti" not in st.session_state:
    st.session_state.bukti = {i: "" for i in range(N)}

if "catatan" not in st.session_state:
    st.session_state.catatan = {i: "" for i in range(N)}

if "jenis_data" not in st.session_state:
    st.session_state.jenis_data = "Belum dinilai"

# ==========================================
# FUNGSI PERHITUNGAN
# ==========================================

konversi = {
    "Ya": 2,
    "Sebagian": 1,
    "Tidak": 0,
    "TDV": None,
    "TR": None
}

def buat_hasil():
    baris = []
    for domain in DOMAIN:
        indeks = df.index[df["Domain"] == domain].tolist()
        jawaban_domain = [st.session_state.jawaban[i] for i in indeks]
        dinilai = [konversi[j] for j in jawaban_domain if j in konversi and konversi[j] is not None]
        
        skor = sum(dinilai)
        maksimal = len(dinilai) * 2

        baris.append({
            "Domain": domain,
            "Jumlah Pertanyaan": len(indeks),
            "Ya": jawaban_domain.count("Ya"),
            "Sebagian": jawaban_domain.count("Sebagian"),
            "Tidak": jawaban_domain.count("Tidak"),
            "TDV": jawaban_domain.count("TDV"),
            "TR": jawaban_domain.count("TR"),
            "Skor Aktual": skor,
            "Skor Maksimal": maksimal,
            "Persentase (%)": (skor / maksimal * 100 if maksimal > 0 else None)
        })
    return pd.DataFrame(baris)

def simpan_kuesioner():
    for i in range(N):
        st.session_state.jawaban[i] = st.session_state[f"jawaban_form_{i}"]

        # Fitur File Uploader
        file_bukti = st.session_state.get(f"bukti_upload_{i}")
        if file_bukti is not None:
            st.session_state.bukti[i] = file_bukti.name
        else:
            st.session_state.bukti[i] = st.session_state.get(f"bukti_teks_{i}", "")

        st.session_state.catatan[i] = st.session_state[f"catatan_form_{i}"]

    st.session_state.jenis_data = "Input pengguna"
    st.session_state["flash_kuesioner"] = True

hasil = buat_hasil()

# ==========================================
# KOMPONEN TAMPILAN
# ==========================================

def esc(teks):
    return html.escape(str(teks))

def css_ikon():
    aturan = []
    for n, isi in enumerate(IKON_MENU, start=1):
        # PERBAIKAN: Mengatur stroke warna putih pada SVG dan menggunakan background-image agar terbaca di semua browser
        svg = (
            "<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' "
            "stroke='white' stroke-width='2.2' stroke-linecap='round' stroke-linejoin='round'>"
            + isi + "</svg>"
        )
        b64_svg = base64.b64encode(svg.encode('utf-8')).decode('utf-8')
        aturan.append(
            f'section[data-testid="stSidebar"] div[role="radiogroup"] > label:nth-of-type({n}) '
            f'{{ --ico: url("data:image/svg+xml;base64,{b64_svg}"); }}'
        )
    return "\n".join(aturan)

def terapkan_css():
    css = CSS_TEMPLATE
    peta = {
        "__NAVY__": WARNA["navy"], "__EMERALD__": WARNA["emerald"],
        "__BG__": WARNA["bg"], "__CARD__": WARNA["card"],
        "__BORDER__": WARNA["border"], "__TEXT__": WARNA["text"],
        "__MUTED__": WARNA["muted"]
    }
    for kunci, nilai in peta.items():
        css = css.replace(kunci, nilai)
    css = css.replace("/*ICONS*/", css_ikon())
    st.markdown(css, unsafe_allow_html=True)

def card(nama):
    try:
        return st.container(key=f"card_{nama}")
    except TypeError:
        return st.container(border=True)

def page_header(judul, subjudul):
    st.markdown(
        '<div class="page-head"><div>'
        f'<div class="crumb">Audit COBIT 5 &nbsp;/&nbsp; <b>{esc(judul)}</b></div>'
        f'<h1 class="page-title">{esc(judul)}</h1>'
        f'<div class="page-sub">{esc(subjudul)}</div>'
        '</div><div class="chip"><i></i>PT Indomarco Prismatama</div></div>',
        unsafe_allow_html=True
    )

def section(judul, sub=""):
    teks = f'<div class="section-title">{esc(judul)}</div>'
    if sub:
        teks += f'<div class="section-sub">{esc(sub)}</div>'
    st.markdown(teks, unsafe_allow_html=True)

def status_pemenuhan(persen):
    if persen is None or pd.isna(persen):
        return "Belum dinilai", "neutral"
    if persen >= AMBANG_TINGGI:
        return "Tinggi", "success"
    if persen >= AMBANG_SEDANG:
        return "Sedang", "warning"
    return "Rendah", "danger"

def badge(label, jenis):
    return f'<span class="badge {jenis}">{esc(label)}</span>'

def kpi(label, nilai, satuan="", sub="", progres=None):
    bar = ""
    if progres is not None:
        bar = f'<div class="bar"><span style="width:{max(0, min(100, progres)):.1f}%"></span></div>'
    kecil = f"<small>{esc(satuan)}</small>" if satuan else ""
    st.markdown(
        '<div class="kpi">'
        f'<div class="kpi-label">{esc(label)}</div>'
        f'<div class="kpi-value">{esc(nilai)}{kecil}</div>'
        f'<div class="kpi-sub">{sub}</div>{bar}</div>',
        unsafe_allow_html=True
    )

def stack_bar(hitung):
    segmen = "".join(
        f'<span style="flex:{n};background:{WARNA_JAWABAN[k]}" title="{esc(k)}: {n}"></span>'
        for k, n in hitung.items() if n > 0
    )
    return f'<div class="stack">{segmen}</div>'

def legenda(hitung):
    item = "".join(
        f'<span><i style="background:{WARNA_JAWABAN[k]}"></i>{esc(k)}<b>{hitung.get(k, 0)}</b></span>'
        for k in PILIHAN
    )
    return f'<div class="legend">{item}</div>'

def hitung_jawaban(indeks):
    hitung = {k: 0 for k in PILIHAN}
    for i in indeks:
        hitung[st.session_state.jawaban[i]] += 1
    return hitung

def tampilkan_tabel(h):
    tabel = h.copy()
    tabel["Persentase (%)"] = pd.to_numeric(tabel["Persentase (%)"], errors="coerce")
    tabel["Status"] = [status_pemenuhan(v)[0] for v in tabel["Persentase (%)"]]
    st.dataframe(
        tabel, hide_index=True,
        column_config={
            "Jumlah Pertanyaan": st.column_config.NumberColumn("Pertanyaan"),
            "Persentase (%)": st.column_config.ProgressColumn(
                "Pemenuhan", format="%.1f%%", min_value=0, max_value=100
            ),
        },
        **STRETCH
    )

def gambar_chart_domain(plot_data):
    x = list(plot_data["Domain"])
    y = [float(v) for v in plot_data["Persentase (%)"]]

    fig, ax = plt.subplots(figsize=(7.4, 3.5))
    fig.patch.set_facecolor("white")
    ax.set_facecolor("white")

    ax.bar(x, [100] * len(x), color="#F1F5F9", width=0.52, zorder=1)
    ax.bar(x, y, color=WARNA["emerald"], width=0.52, zorder=2)

    for xi, yi in zip(x, y):
        ax.text(xi, yi + 2.5, f"{yi:.0f}%", ha="center", va="bottom",
                fontsize=10, fontweight="bold", color=WARNA["navy"], zorder=3)

    ax.set_ylim(0, 114)
    ax.set_yticks([0, 25, 50, 75, 100])
    ax.set_yticklabels(["0", "25", "50", "75", "100"])
    ax.tick_params(axis="both", length=0, labelsize=9, colors=WARNA["muted"])
    ax.tick_params(axis="x", labelsize=10, colors=WARNA["navy"])
    ax.grid(axis="y", color="#F1F5F9", linewidth=1.2, zorder=0)
    ax.set_axisbelow(True)
    for sisi in ax.spines.values():
        sisi.set_visible(False)

    fig.tight_layout()
    return fig

# ==========================================
# SIDEBAR
# ==========================================

terapkan_css()

st.sidebar.markdown(
    '<div class="brand"><div class="brand-logo">'
    '<svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="#fff" stroke-width="2.5" '
    'stroke-linecap="round" stroke-linejoin="round">'
    '<path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/><path d="M9 12l2 2 4-4"/></svg>'
    '</div><div><div class="brand-title">AUDIT COBIT 5</div>'
    '<div class="brand-sub">Information System Audit</div></div></div>'
    '<div class="nav-caption">MENU NAVIGASI</div>',
    unsafe_allow_html=True
)

menu = st.sidebar.radio("Navigasi Aplikasi", MENU, label_visibility="collapsed", key="menu_nav")

st.sidebar.markdown(
    '<div class="sb-footer">PT Indomarco Prismatama<br>'
    f'Kerangka Kerja: <b>COBIT 5</b> &nbsp;·&nbsp; Versi {APP_VERSION}</div>',
    unsafe_allow_html=True
)

# ==========================================
# DASHBOARD
# ==========================================

if menu == "Dashboard":

    page_header("Dashboard", "Audit Sistem Informasi Persediaan Barang · Implementasi COBIT 5 — Indomaret")

    st.info("Aplikasi ini merupakan implementasi akademik. Data simulasi tidak mewakili hasil audit aktual perusahaan.")

    total_terisi = sum(j != "Belum diisi" for j in st.session_state.jawaban.values())
    total_skor = hasil["Skor Aktual"].sum()
    total_maksimal = hasil["Skor Maksimal"].sum()
    persentase = (total_skor / total_maksimal * 100 if total_maksimal > 0 else 0)

    label_status, jenis_status = status_pemenuhan(persentase if total_maksimal > 0 else None)

    a, b, c, d = st.columns(4, gap="medium")

    with a:
        kpi("Total Pertanyaan", N, sub=f"{len(DOMAIN)} domain · {df['Kode Proses'].nunique()} proses COBIT 5")
    with b:
        kpi("Jawaban Terisi", total_terisi, satuan=f"/ {N}", sub="Pertanyaan yang sudah dijawab", progres=total_terisi / N * 100)
    with c:
        kpi("Skor Aktual", int(total_skor), satuan=f"/ {int(total_maksimal)}", sub="Dari skor maksimal yang dapat dinilai")
    with d:
        kpi("Pemenuhan", f"{persentase:.1f}%", sub=badge(label_status, jenis_status), progres=persentase if total_maksimal > 0 else 0)

    st.write("")
    kiri, kanan = st.columns([3, 2], gap="medium")

    with kiri:
        with card("chart"):
            section("Persentase Pemenuhan per Domain", "Skor aktual dibagi skor maksimal dari jawaban yang dapat dinilai")
            if total_maksimal > 0:
                plot_data = hasil.dropna(subset=["Persentase (%)"])
                fig = gambar_chart_domain(plot_data)
                st.pyplot(fig)
                plt.close(fig)
            else:
                st.markdown(
                    '<div class="empty">Belum ada jawaban yang dapat dinilai.<br>'
                    'Isi kuesioner pada menu <b>Kuesioner Audit</b> untuk menampilkan grafik.</div>',
                    unsafe_allow_html=True
                )

    with kanan:
        with card("progres"):
            section("Progres Pengisian", "Jumlah pertanyaan terjawab per domain")
            baris = ""
            for domain in DOMAIN:
                indeks = df.index[df["Domain"] == domain].tolist()
                terisi = sum(st.session_state.jawaban[i] != "Belum diisi" for i in indeks)
                persen = terisi / len(indeks) * 100
                baris += (
                    '<div class="dom-row">'
                    f'<div class="dom-code">{domain}</div>'
                    '<div class="dom-main">'
                    f'<div class="dom-name"><span>{esc(NAMA_DOMAIN[domain])}</span>'
                    f'<span class="dom-count">{terisi}/{len(indeks)}</span></div>'
                    f'<div class="bar" style="margin-top:6px"><span style="width:{persen:.1f}%"></span></div>'
                    '</div></div>'
                )
            st.markdown(baris, unsafe_allow_html=True)

    st.write("")
    with card("ringkasan"):
        section("Ringkasan Lima Domain COBIT 5", "Rekap jawaban dan skor untuk setiap domain")
        tampilkan_tabel(hasil)

# ==========================================
# KUESIONER AUDIT
# ==========================================

elif menu == "Kuesioner Audit":

    page_header("Kuesioner Audit", f"{N} pertanyaan berdasarkan instrumen Tugas 1")

    tersimpan = sum(j != "Belum diisi" for j in st.session_state.jawaban.values())

    with card("panduan"):
        kolom_a, kolom_b = st.columns([3, 2], gap="large")
        with kolom_a:
            section("Panduan Pengisian", "Pilih satu jawaban untuk setiap pertanyaan. TDV dan TR tidak mendapatkan skor.")
            st.markdown(
                '<div class="legend" style="margin-top:0">'
                f'<span><i style="background:{WARNA_JAWABAN["Ya"]}"></i>Ya<b>= 2</b></span>'
                f'<span><i style="background:{WARNA_JAWABAN["Sebagian"]}"></i>Sebagian<b>= 1</b></span>'
                f'<span><i style="background:{WARNA_JAWABAN["Tidak"]}"></i>Tidak<b>= 0</b></span>'
                f'<span><i style="background:{WARNA_JAWABAN["TDV"]}"></i>TDV<b>tanpa skor</b></span>'
                f'<span><i style="background:{WARNA_JAWABAN["TR"]}"></i>TR<b>tanpa skor</b></span>'
                '</div>', unsafe_allow_html=True
            )
        with kolom_b:
            kpi("Jawaban Tersimpan", tersimpan, satuan=f"/ {N}", sub="Klik Simpan Jawaban Audit di bawah", progres=tersimpan / N * 100)

    st.write("")

    with st.form("form_audit"):
        tab_domain = st.tabs([f"{d}  ·  {int((df['Domain'] == d).sum())}" for d in DOMAIN])

        for tab, domain in zip(tab_domain, DOMAIN):
            with tab:
                bagian = df[df["Domain"] == domain]
                kode = ", ".join(bagian["Kode Proses"].drop_duplicates())

                st.markdown(
                    f'<div class="dom-head"><b>{domain}</b><span>{esc(NAMA_DOMAIN[domain])} · {esc(kode)}</span></div>',
                    unsafe_allow_html=True
                )

                for i, row in bagian.iterrows():
                    with card(f"q{i}"):
                        st.markdown(
                            '<div class="q-head">'
                            f'<div class="q-num">{i + 1}</div>'
                            '<div class="q-body">'
                            '<div class="q-meta">'
                            f'<span class="tag proc">{esc(row["Kode Proses"])}</span>'
                            f'<span class="tag">{esc(row["Nama Proses"])}</span></div>'
                            f'<div class="q-aspek">{esc(row["Aspek"])}</div>'
                            f'<div class="q-text">{esc(row["Pertanyaan"])}</div>'
                            '</div></div>', unsafe_allow_html=True
                        )

                        k1, k2, k3 = st.columns([1, 2, 2], gap="medium")

                        with k1:
                            st.selectbox("Jawaban", PILIHAN, key=f"jawaban_form_{i}", index=PILIHAN.index(st.session_state.jawaban[i]))

                        with k2:
                            st.text_input("Nama Bukti (Teks)", value=st.session_state.bukti[i], key=f"bukti_teks_{i}", placeholder="Ketik nama dokumen...")
                            st.file_uploader("Atau Upload File", type=["pdf", "png", "jpg", "jpeg", "docx", "xlsx"], key=f"bukti_upload_{i}")

                        with k3:
                            st.text_input("Catatan auditor", value=st.session_state.catatan[i], key=f"catatan_form_{i}", placeholder="Catatan hasil pemeriksaan")

        st.form_submit_button("Simpan Jawaban Audit", type="primary", on_click=simpan_kuesioner, **STRETCH)

    if st.session_state.pop("flash_kuesioner", False):
        st.success("Jawaban berhasil disimpan!")

# ==========================================
# HASIL PENILAIAN
# ==========================================

elif menu == "Hasil Penilaian":

    page_header("Hasil Penilaian", "Rekap skor dan distribusi jawaban per domain COBIT 5")

    belum = sum(j == "Belum diisi" for j in st.session_state.jawaban.values())

    if belum > 0:
        st.warning(f"Masih terdapat {belum} pertanyaan yang belum diisi.")
    else:
        st.success(f"Seluruh {N} pertanyaan telah memiliki jawaban.")

    st.write("")

    with card("rekap"):
        section("Rekapitulasi Skor per Domain",
                "Indikator Status: Tinggi ≥ "
                f"{AMBANG_TINGGI}%, Sedang {AMBANG_SEDANG}–{AMBANG_TINGGI - 1}%, "
                f"Rendah < {AMBANG_SEDANG}%. Bersifat visual, bukan capability level.")
        tampilkan_tabel(hasil)

    st.write("")

    with card("distribusi"):
        section("Distribusi Jawaban", "Sebaran jawaban keseluruhan dan per domain")
        total_hitung = hitung_jawaban(range(N))
        st.markdown(stack_bar(total_hitung) + legenda(total_hitung), unsafe_allow_html=True)

        baris = '<div style="margin-top:20px">'
        for domain in DOMAIN:
            indeks = df.index[df["Domain"] == domain].tolist()
            hitung = hitung_jawaban(indeks)
            baris += (
                '<div class="dom-row">'
                f'<div class="dom-code">{domain}</div>'
                f'<div class="dom-main">{stack_bar(hitung)}</div>'
                f'<div class="dom-count">{len(indeks)} soal</div></div>'
            )
        baris += "</div>"
        st.markdown(baris, unsafe_allow_html=True)

    st.caption("Persentase dihitung dari skor aktual dibagi skor maksimal dari jawaban yang dapat dinilai.")

# ==========================================
# TEMUAN DAN REKOMENDASI
# ==========================================

elif menu == "Temuan dan Rekomendasi":

    page_header("Temuan dan Rekomendasi", "Dokumentasikan temuan audit berdasarkan bukti pemeriksaan")
    st.warning("Isi bagian ini berdasarkan bukti pemeriksaan. Jangan membuat temuan aktual dari data simulasi.")

    with card("form_temuan"):
        with st.form("form_temuan"):
            t1, t2 = st.columns([1, 2], gap="medium")
            domain_temuan = t1.selectbox("Domain COBIT 5", DOMAIN)
            judul = t2.text_input("Judul Temuan")

            t3, t4 = st.columns(2, gap="medium")
            kondisi = t3.text_area("Kondisi", height=130)
            kriteria = t4.text_area("Kriteria", height=130)

            t5, t6 = st.columns(2, gap="medium")
            sebab = t5.text_area("Penyebab", height=130)
            dampak = t6.text_area("Dampak", height=130)

            rekomendasi = st.text_area("Rekomendasi", height=130)
            simpan_temuan = st.form_submit_button("Simpan Temuan", type="primary")

    if simpan_temuan:
        st.session_state["temuan_tersimpan"] = {
            "Domain": domain_temuan, "Judul": judul, "Kondisi": kondisi,
            "Kriteria": kriteria, "Penyebab": sebab, "Dampak": dampak, "Rekomendasi": rekomendasi
        }
        st.success("Temuan berhasil disimpan selama sesi aplikasi.")

    if "temuan_tersimpan" in st.session_state:
        st.write("")
        temuan = st.session_state.temuan_tersimpan

        def teks(kunci):
            nilai = esc(temuan[kunci]).replace("\n", "<br>")
            return nilai if nilai.strip() else "—"

        with card("temuan_tersimpan"):
            section("Temuan Tersimpan")
            st.markdown(
                '<div class="q-meta">'
                f'<span class="tag proc">{esc(temuan["Domain"])}</span></div>'
                f'<div class="q-aspek" style="font-size:1.1rem">{teks("Judul")}</div>'
                + "".join(
                    f'<div class="finding-label">{k}</div><div class="finding-text">{teks(k)}</div>'
                    for k in ["Kondisi", "Kriteria", "Penyebab", "Dampak", "Rekomendasi"]
                ), unsafe_allow_html=True
            )

# ==========================================
# LAPORAN AUDIT
# ==========================================

elif menu == "Laporan Audit":

    page_header("Laporan Audit", "Ekspor hasil audit COBIT 5 ke berkas Excel")

    hasil_laporan = buat_hasil()
    df_laporan = df.copy()
    df_laporan["Jawaban"] = [st.session_state.jawaban[i] for i in range(N)]
    df_laporan["Skor"] = [konversi.get(st.session_state.jawaban[i]) for i in range(N)]
    df_laporan["Bukti Pendukung"] = [st.session_state.bukti[i] for i in range(N)]
    df_laporan["Catatan Auditor"] = [st.session_state.catatan[i] for i in range(N)]

    ringkasan = pd.DataFrame({
        "Keterangan": ["Objek Audit", "Fokus Audit", "Framework", "Status Data", "Total Pertanyaan", "Skor Aktual", "Skor Maksimal", "Persentase Pemenuhan"],
        "Hasil": [
            "PT Indomarco Prismatama (Indomaret)", "Sistem Informasi Persediaan Barang", "COBIT 5",
            st.session_state.jenis_data, N, int(hasil_laporan["Skor Aktual"].sum()), int(hasil_laporan["Skor Maksimal"].sum()),
            (f"{hasil_laporan['Skor Aktual'].sum() / hasil_laporan['Skor Maksimal'].sum() * 100:.2f}%" if hasil_laporan["Skor Maksimal"].sum() > 0 else "Belum dapat dihitung")
        ]
    })

    output = BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        df_laporan.to_excel(writer, sheet_name="Data_Kuesioner", index=False)
        hasil_laporan.to_excel(writer, sheet_name="Rekap_Domain", index=False)
        ringkasan.to_excel(writer, sheet_name="Ringkasan_Audit", index=False)
        if "temuan_tersimpan" in st.session_state:
            pd.DataFrame([st.session_state.temuan_tersimpan]).to_excel(writer, sheet_name="Temuan_Audit", index=False)

    kiri, kanan = st.columns([2, 3], gap="medium")

    with kiri:
        with card("isi_laporan"):
            section("Isi Berkas Excel", "Lembar kerja yang akan diekspor")
            lembar = [("Data_Kuesioner", "Jawaban, bukti, dan catatan per pertanyaan"), ("Rekap_Domain", "Skor dan persentase per domain"), ("Ringkasan_Audit", "Identitas dan ringkasan audit")]
            if "temuan_tersimpan" in st.session_state:
                lembar.append(("Temuan_Audit", "Temuan dan rekomendasi tersimpan"))
            st.markdown("".join(f'<div class="kv"><b style="text-align:left">{esc(n)}</b><span>{esc(k)}</span></div>' for n, k in lembar), unsafe_allow_html=True)
            if "temuan_tersimpan" not in st.session_state:
                st.caption("Lembar Temuan_Audit muncul setelah temuan disimpan.")

    with kanan:
        with card("ringkasan_laporan"):
            section("Ringkasan Audit", "Pratinjau lembar Ringkasan_Audit")
            st.markdown("".join(f'<div class="kv"><span>{esc(k)}</span><b>{esc(v)}</b></div>' for k, v in zip(ringkasan["Keterangan"], ringkasan["Hasil"])), unsafe_allow_html=True)

    st.write("")
    st.download_button("Download Laporan Excel", data=output.getvalue(), file_name="HASIL_AUDIT_COBIT5_INDOMARET.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", **STRETCH)
    st.success("Laporan Excel siap diunduh.")
from datetime import datetime
import pandas as pd
import streamlit as st

# =====================================================
# KONFIGURASI HALAMAN & THEME (HIJAU MUDA)
# =====================================================
st.set_page_config(
    page_title="Kalkulator PICU Score", layout="centered"
)

st.markdown(
    """
    <style>
    .stApp {
        background-color: #F4FBF7 !important;
        color: #000000 !important;
        font-family: 'Helvetica', sans-serif;
    }
    h1, h2, h3, h4 {
        color: #1E5128 !important;
        font-weight: 700 !important;
    }
    
    /* Styling khusus agar label teks login & form berwarna hijau tua */
    label, .stTextInput label, .stSelectbox label, .stNumberInput label {
        color: #1E5128 !important;
        font-weight: 700 !important;
    }

    div.stButton > button, div[data-testid="stFormSubmitButton"] > button {
        background-color: #4E9F3D !important;
        color: #ffffff !important;
        border: none !important;
        border-radius: 8px !important;
        padding: 0.6em 1.2em !important;
        font-weight: 600 !important;
        transition: all 0.3s ease !important;
    }
    div.stButton > button:hover, div[data-testid="stFormSubmitButton"] > button:hover {
        background-color: #1E5128 !important;
        color: #ffffff !important;
        transform: translateY(-2px);
    }
    .navy-label {
        color: #1E5128;
        font-weight: 700;
        margin-bottom: 6px;
        display: block;
        font-size: 0.95rem;
    }
    .welcome-box {
        background-color: #D8F3DC;
        color: #1E5128;
        padding: 12px;
        border-radius: 8px;
        border-left: 4px solid #4E9F3D;
        font-weight: 600;
        margin-bottom: 15px;
    }
    .nav-wrapper {
        display: flex;
        justify-content: center;
        align-items: center;
        margin-bottom: 8px;
        border-radius: 8px;
        overflow: hidden;
    }
    </style>
""",
    unsafe_allow_html=True,
)

# =====================================================
# 1️⃣ KAMUS BOBOT SKOR (SCORE WEIGHT) TETAP
# =====================================================
SCORE_WEIGHTS = {
    "STATUS GIZI": -75.15,
    "LOKASI TUMOR": -36.65,
    "RIW. RESEKSI TUMOR": 100.00,
    "VOLUME PERDARAHAN INTRAOP": 16.48,
    "VOLUME TRANSFUSI INTRAOP": 57.77,
    "STATUS INTUBASI": 59.08,
    "STATUS VP EVD": -39.26,
    "KOMP. AKUT PASCA OP": 94.68,
    "STATUS HEMODINAMIK": 62.70,
}

THRESHOLD_SCORE = 50.19

# =====================================================
# 2️⃣ SESSION INITIALIZATION
# =====================================================
if "users" not in st.session_state:
  st.session_state["users"] = {
      "abdulchairy": {
          "name": "dr. Abdul Chairy",
          "instansi": "RS Cipto Mangunkusumo",
          "email": "abdul.chairy@rs-cipto.go.id",
          "phone": "081234567890",
          "password": "123456",
          "jadwal": "Senin - Jumat. 08:00 - 14:00",
      }
  }

if "logged_in" not in st.session_state:
  st.session_state["logged_in"] = False
  st.session_state["username"] = None

if "history" not in st.session_state:
  st.session_state["history"] = []

if "page" not in st.session_state:
  st.session_state["page"] = "home"


def go_to(page):
  st.session_state["page"] = page


def dashboard_nav():
  cols = st.columns(4)
  labels = [
      ("Home", "dashboard"),
      ("Profile", "profile"),
      ("Diagnosis", "diagnosis"),
      ("Riwayat", "history"),
  ]
  for c, (label, page_name) in zip(cols, labels):
    with c:
      if st.button(label, key=f"nav_{page_name}"):
        go_to(page_name)


# =====================================================
# 3️⃣ ROUTING HALAMAN
# =====================================================

# --- HOME ---
if st.session_state["page"] == "home":
  st.title("🏥 Kalkulator PICU Score")
  st.markdown("### Sistem Penilaian Risiko Berbasis Aturan & Bobot Skor Tetap")
  st.write("Silakan masuk menggunakan akun tenaga medis.")
  if st.button("Mulai Aplikasi", key="btn_home_start"):
    go_to("login")

# --- LOGIN ---
elif st.session_state["page"] == "login":
  st.header("🔐 Login Tenaga Medis")
  with st.form("login_form"):
    username = st.text_input("Username", key="login_username")
    password = st.text_input("Password", type="password", key="login_password")
    submitted = st.form_submit_button("Masuk")

  if submitted:
    user = st.session_state["users"].get(username)
    if user and user["password"] == password:
      st.session_state["logged_in"] = True
      st.session_state["username"] = username
      go_to("dashboard")
      st.rerun()
    else:
      st.error("Username atau password salah.")

  if st.button("Kembali ke Beranda", key="btn_login_back"):
    go_to("home")

# --- DASHBOARD ---
elif st.session_state["page"] == "dashboard":
  if not st.session_state["logged_in"]:
    st.warning("Silakan login terlebih dahulu.")
    go_to("login")
  else:
    user = st.session_state["users"].get(st.session_state["username"], {})
    st.title("Dashboard Utama")
    dashboard_nav()
    st.markdown("---")

    st.markdown(
        f'<div class="welcome-box">Selamat datang, {user.get("name", "-")}!</div>',
        unsafe_allow_html=True,
    )

    col1, col2 = st.columns([2, 3])
    with col1:
      st.write("**Nama:**", user.get("name", "-"))
      st.write("**Instansi:**", user.get("instansi", "-"))
      st.write("**Jadwal Praktek:**", user.get("jadwal", "-"))
    with col2:
      st.write("**Riwayat Diagnosis Terbaru**")
      if len(st.session_state["history"]) == 0:
        st.info("Belum ada riwayat diagnosis.")
      else:
        df_recent = pd.DataFrame(st.session_state["history"]).tail(5)
        st.dataframe(df_recent, use_container_width=True)

    st.markdown("---")
    if st.button("Log Out", key="btn_logout"):
      st.session_state["logged_in"] = False
      st.session_state["username"] = None
      go_to("login")
      st.rerun()

# --- PROFILE ---
elif st.session_state["page"] == "profile":
  if not st.session_state["logged_in"]:
    st.warning("Silakan login terlebih dahulu.")
    go_to("login")
  else:
    user = st.session_state["users"].get(st.session_state["username"], {})
    st.title("Profil Pengguna")
    dashboard_nav()
    st.markdown("---")
    st.write("**Nama:**", user.get("name", "-"))
    st.write("**Instansi:**", user.get("instansi", "-"))
    st.write("**Jadwal Praktek:**", user.get("jadwal", "-"))
    st.write("**Email:**", user.get("email", "-"))
    st.write("**No HP:**", user.get("phone", "-"))
    st.markdown("---")
    if st.button("Kembali ke Dashboard", key="btn_profile_back"):
      go_to("dashboard")

# --- DIAGNOSIS (SCORING SYSTEM) ---
elif st.session_state["page"] == "diagnosis":
  if not st.session_state["logged_in"]:
    st.warning("Silakan login terlebih dahulu.")
    go_to("login")
  else:
    st.title("Diagnosis - Input Data Pasien")
    dashboard_nav()
    st.markdown("---")

    with st.form("diagnosis_form"):
      input_data = {}

      # 1. STATUS GIZI
      st.markdown(
          '<label class="navy-label">STATUS GIZI</label>',
          unsafe_allow_html=True,
      )
      input_data["STATUS GIZI"] = st.selectbox(
          "Status Gizi",
          options=[1.0, 2.0, 3.0],
          format_func=lambda x: {
              1.0: "1 (Gizi Baik)",
              2.0: "2 (Gizi Buruk)",
              3.0: "3 (Stunting)",
          }[x],
          key="input_status_gizi",
          label_visibility="collapsed",
      )

      # 2. LOKASI TUMOR
      st.markdown(
          '<label class="navy-label">LOKASI TUMOR</label>',
          unsafe_allow_html=True,
      )
      input_data["LOKASI TUMOR"] = st.selectbox(
          "Lokasi Tumor",
          options=[1.0, 2.0, 3.0],
          format_func=lambda x: {
              1.0: "1 (Supratentorial)",
              2.0: "2 (Infratentorial)",
              3.0: "3 (Suprasella)",
          }[x],
          key="input_lokasi_tumor",
          label_visibility="collapsed",
      )

      # 3. RIW. RESEKSI TUMOR
      st.markdown(
          '<label class="navy-label">RIW. RESEKSI TUMOR</label>',
          unsafe_allow_html=True,
      )
      input_data["RIW. RESEKSI TUMOR"] = st.selectbox(
          "Riwayat Reseksi Tumor",
          options=[0.0, 1.0],
          format_func=lambda x: (
              "0 (Operasi pertama kali)"
              if x == 0.0
              else "1 (Pernah operasi >=1)"
          ),
          key="input_riw_reseksi",
          label_visibility="collapsed",
      )

      # 4. VOLUME PERDARAHAN INTRAOP
      st.markdown(
          '<label class="navy-label">VOLUME PERDARAHAN INTRAOP</label>',
          unsafe_allow_html=True,
      )
      input_data["VOLUME PERDARAHAN INTRAOP"] = st.number_input(
          "Volume Perdarahan Intraop",
          min_value=0.0,
          value=100.0,
          step=10.0,
          key="input_vol_perdarahan",
          label_visibility="collapsed",
      )

      # 5. VOLUME TRANSFUSI INTRAOP
      st.markdown(
          '<label class="navy-label">VOLUME TRANSFUSI INTRAOP</label>',
          unsafe_allow_html=True,
      )
      input_data["VOLUME TRANSFUSI INTRAOP"] = st.number_input(
          "Volume Transfusi Intraop",
          min_value=0.0,
          value=0.0,
          step=10.0,
          key="input_vol_transfusi",
          label_visibility="collapsed",
      )

      # 6. STATUS INTUBASI
      st.markdown(
          '<label class="navy-label">STATUS INTUBASI</label>',
          unsafe_allow_html=True,
      )
      input_data["STATUS INTUBASI"] = st.selectbox(
          "Status Intubasi",
          options=[0.0, 1.0],
          format_func=lambda x: (
              "0 (Ekstubasi <= 6 jam)" if x == 0.0 else "1 (Terintubasi > 6 jam)"
          ),
          key="input_status_intubasi",
          label_visibility="collapsed",
      )

      # 7. STATUS VP EVD
      st.markdown(
          '<label class="navy-label">STATUS VP EVD</label>',
          unsafe_allow_html=True,
      )
      input_data["STATUS VP EVD"] = st.selectbox(
          "Status VP EVD",
          options=[0.0, 1.0, 2.0],
          format_func=lambda x: f"Nilai {int(x)}",
          key="input_status_vp_evd",
          label_visibility="collapsed",
      )

      # 8. KOMP. AKUT PASCA OP
      st.markdown(
          '<label class="navy-label">KOMP. AKUT PASCA OP</label>',
          unsafe_allow_html=True,
      )
      input_data["KOMP. AKUT PASCA OP"] = st.selectbox(
          "Komplikasi Akut Pasca Operasi",
          options=[0.0, 1.0],
          format_func=lambda x: (
              "0 (Tidak ada komplikasi)"
              if x == 0.0
              else "1 (Ada Komplikasi >= 1 kejadian)"
          ),
          key="input_komp_akut",
          label_visibility="collapsed",
      )

      # 9. STATUS HEMODINAMIK
      st.markdown(
          '<label class="navy-label">STATUS HEMODINAMIK</label>',
          unsafe_allow_html=True,
      )
      input_data["STATUS HEMODINAMIK"] = st.selectbox(
          "Status Hemodinamik",
          options=[0.0, 1.0],
          format_func=lambda x: (
              "0 (Stabil)" if x == 0.0 else "1 (Tidak stabil)"
          ),
          key="input_status_hemodinamik",
          label_visibility="collapsed",
      )

      submitted = st.form_submit_button("Diagnosis")

    if submitted:
      total_score = 0.0

      for feat, weight_val in SCORE_WEIGHTS.items():
        val_input = float(input_data.get(feat, 0.0))
        contrib = val_input * weight_val
        total_score += contrib

      prediction_label = (
          "> 24 Jam" if total_score >= THRESHOLD_SCORE else "< 24 Jam"
      )

      st.markdown("---")
      st.subheader("📊 Hasil Penilaian Risiko PICU")

      col_res1, col_res2 = st.columns(2)
      with col_res1:
        st.markdown(f"**TOTAL SKOR:** `{total_score:.2f}`")
        st.markdown(f"**Youden Index Threshold:** `{THRESHOLD_SCORE}`")
      with col_res2:
        if total_score >= THRESHOLD_SCORE:
          st.success(f"**Kategori Risiko:** {prediction_label}")
        else:
          st.warning(f"**Kategori Risiko:** {prediction_label}")

      # Simpan ke riwayat
      record = {
          "Timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
          **input_data,
          "Total Skor": f"{total_score:.2f}",
          "Kategori Risiko": prediction_label,
      }
      st.session_state["history"].append(record)

      st.markdown("---")
      col_a, col_b = st.columns(2)
      with col_a:
        if st.button("Diagnosis Pasien Lain", key="btn_diag_again"):
          st.rerun()
      with col_b:
        if st.button("Lihat Riwayat", key="btn_diag_to_history"):
          go_to("history")
          st.rerun()

# --- RIWAYAT ---
elif st.session_state["page"] == "history":
  if not st.session_state["logged_in"]:
    st.warning("Silakan login terlebih dahulu.")
    go_to("login")
  else:
    st.title("📋 Riwayat Diagnosis")
    dashboard_nav()
    st.markdown("---")

    if len(st.session_state["history"]) == 0:
      st.info("Belum ada riwayat diagnosis tersimpan.")
    else:
      df_hist = pd.DataFrame(st.session_state["history"])
      st.dataframe(df_hist, use_container_width=True)

    col1, col2 = st.columns(2)
    with col1:
      if st.button("Lakukan Diagnosis Baru", key="btn_hist_new"):
        go_to("diagnosis")
        st.rerun()
    with col2:
      if st.button("Logout", key="btn_hist_logout"):
        st.session_state["logged_in"] = False
        go_to("login")
        st.rerun()

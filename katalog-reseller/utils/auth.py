"""Authentication utilities for Katalog Reseller.
Supports: Email/Password, Phone OTP (SMS/WhatsApp), Google OAuth.
"""

import streamlit as st
import hashlib
import time
from data.resellers import (
    get_reseller_by_email,
    get_reseller_by_phone,
    get_reseller_by_google_id,
    register_reseller,
    verify_reseller,
    generate_otp,
    verify_otp,
    delete_otp,
    get_marketing_by_code,
    get_marketing_users,
)

# ── Demo users (legacy) ──
USERS = {
    "admin": {
        "password": hashlib.sha256("admin123".encode()).hexdigest(),
        "nama": "Admin Toko",
        "role": "admin",
    },
    "reseller1": {
        "password": hashlib.sha256("reseller123".encode()).hexdigest(),
        "nama": "Budi Reseller",
        "role": "reseller",
    },
    "demo": {
        "password": hashlib.sha256("demo123".encode()).hexdigest(),
        "nama": "Demo User",
        "role": "reseller",
    },
    "marketing": {
        "password": hashlib.sha256("marketing123".encode()).hexdigest(),
        "nama": "Tim Marketing",
        "role": "marketing",
    },
}


def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()


# ── Session Init ──
def init_auth_session():
    """Initialize all auth-related session state."""
    defaults = {
        "logged_in": False,
        "user": None,
        "role": None,
        "username": None,
        "show_register": False,
        "register_step": "method",
        "register_method": None,
        "register_role": "",
        "register_phone": "",
        "register_otp": "",
        "register_email": "",
        "register_name": "",
        "register_password": "",
        "google_auth_url": "",
    }
    for key, val in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = val


# ── Main Entry ──
def check_login():
    """Check if user is logged in. Returns True/False without blocking."""
    init_auth_session()

    # Handle Google OAuth callback
    if not st.session_state.logged_in:
        _handle_google_callback()

    return st.session_state.logged_in


def show_auth_page():
    """Show login or register page (called as a tab/page, not blocking)."""
    init_auth_session()

    # Handle Google OAuth callback
    if not st.session_state.logged_in:
        _handle_google_callback()

    if st.session_state.logged_in:
        # Already logged in - show profile
        _show_profile_page()
    elif st.session_state.show_register:
        show_register_page()
    else:
        show_login_page()


def _show_profile_page():
    """Show user profile when already logged in."""
    st.markdown(LIGHT_CSS, unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 3, 1])
    with col2:
        st.markdown('<div class="auth-card">', unsafe_allow_html=True)
        _render_brand_header()

        st.markdown(f"""
        <div class="success-box">
            <div style="font-size:2rem;margin-bottom:0.5rem;">👋</div>
            <div style="font-size:1rem;font-weight:600;color:#2E7D32;margin-bottom:0.3rem;">
                Anda sudah login
            </div>
            <div style="font-size:0.82rem;color:#757575;">
                Selamat datang, <b>{st.session_state.user}</b>!<br>
                Role: <b>{st.session_state.role}</b>
            </div>
        </div>
        """, unsafe_allow_html=True)

        if st.button("🚪 Logout", use_container_width=True, type="primary"):
            logout()

        st.markdown('</div>', unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════
# ── SHARED DARK CSS ──
# ═══════════════════════════════════════════════════════════════

LIGHT_CSS = """
<style>
/* ── Clean White Background ── */
.stApp {
    background: #F5F5F5 !important;
}
.stApp header[data-testid="stHeader"] {
    background: transparent !important;
}

/* ── Card ── */
.auth-card {
    background: #FFFFFF;
    border: 1px solid rgba(0,0,0,0.06);
    border-radius: 20px;
    padding: 2.5rem 2.2rem;
    box-shadow:
        0 4px 24px rgba(0,0,0,0.06),
        0 1px 4px rgba(0,0,0,0.04);
    position: relative;
    overflow: hidden;
}
.auth-card::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 3px;
    background: linear-gradient(90deg,
        transparent 0%,
        #E53935 30%,
        #E53935 70%,
        transparent 100%
    );
}

/* ── Brand Header ── */
.brand-header {
    text-align: center;
    margin-bottom: 2rem;
    position: relative;
}
.brand-icon {
    display: inline-flex;
    align-items: center; justify-content: center;
    width: 60px; height: 60px;
    border-radius: 16px;
    background: linear-gradient(135deg, #E53935, #C62828);
    margin-bottom: 1rem;
    box-shadow: 0 8px 24px rgba(229,57,53,0.25);
}
.brand-icon svg { width: 32px; height: 32px; fill: white; }

.brand-title {
    font-family: 'Plus Jakarta Sans', sans-serif;
    font-size: 1.7rem; font-weight: 700;
    letter-spacing: 2px;
    margin: 0 0 0.25rem 0; text-transform: uppercase;
    color: #E53935;
}
.brand-subtitle {
    font-family: 'Plus Jakarta Sans', sans-serif;
    font-size: 0.78rem; font-weight: 500;
    letter-spacing: 3px; color: #9E9E9E;
    text-transform: uppercase; margin: 0;
}
.brand-divider {
    width: 50px; height: 2px;
    background: linear-gradient(90deg, transparent, #E53935, transparent);
    margin: 1rem auto; border-radius: 1px;
}

/* ── Form Area ── */
.auth-form-area { padding: 0 0.3rem; }

/* ── Input Labels ── */
.auth-form-area label,
div[data-testid="stTextInput"] label {
    color: #616161 !important;
    font-size: 0.82rem !important;
    font-weight: 500 !important;
    letter-spacing: 0.5px;
}

/* ── Input Fields ── */
[data-testid="stTextInput"] [data-baseweb="input"] input,
[data-testid="stTextInput"] input[aria-label],
div[data-testid="stTextInput"] input {
    background-color: #FAFAFA !important;
    background: #FAFAFA !important;
    border: 1px solid #E0E0E0 !important;
    border-radius: 10px !important;
    color: #212121 !important;
    -webkit-text-fill-color: #212121 !important;
    padding: 0.65rem 1rem !important;
    font-size: 0.9rem !important;
    transition: all 0.3s ease !important;
}
[data-testid="stTextInput"] [data-baseweb="input"] input:focus,
div[data-testid="stTextInput"] input:focus {
    border-color: #E53935 !important;
    box-shadow: 0 0 0 3px rgba(229,57,53,0.1) !important;
    background-color: #FFFFFF !important;
    background: #FFFFFF !important;
}
[data-testid="stTextInput"] [data-baseweb="input"] input::placeholder,
div[data-testid="stTextInput"] input::placeholder {
    color: #BDBDBD !important;
    -webkit-text-fill-color: #BDBDBD !important;
}

[data-testid="stTextInput"] [data-baseweb="input"],
[data-testid="stTextInput"] [data-baseweb="base-input"] {
    background-color: #FAFAFA !important;
    border-radius: 10px !important;
}

/* Autofill */
[data-testid="stTextInput"] input:-webkit-autofill,
[data-testid="stTextInput"] input:-webkit-autofill:hover,
[data-testid="stTextInput"] input:-webkit-autofill:focus,
[data-testid="stTextInput"] [data-baseweb="input"] input:-webkit-autofill {
    -webkit-box-shadow: 0 0 0 30px #FAFAFA inset !important;
    -webkit-text-fill-color: #212121 !important;
    transition: background-color 5000s ease-in-out 0s;
}

/* ── Primary Button ── */
div[data-testid="stButton"] button {
    background: linear-gradient(135deg, #E53935, #C62828) !important;
    color: white !important;
    border: none !important;
    border-radius: 10px !important;
    padding: 0.65rem !important;
    font-size: 0.9rem !important;
    font-weight: 600 !important;
    letter-spacing: 1px !important;
    text-transform: uppercase !important;
    transition: all 0.3s ease !important;
    box-shadow: 0 4px 20px rgba(229,57,53,0.25) !important;
}
div[data-testid="stButton"] button:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 8px 30px rgba(229,57,53,0.35) !important;
    background: linear-gradient(135deg, #EF5350, #E53935) !important;
}
div[data-testid="stButton"] button:active {
    transform: translateY(0) !important;
}

/* ── Secondary / Outlined Buttons ── */
div[data-testid="stButton"] button[kind="secondary"] {
    background: #FFFFFF !important;
    border: 1px solid #E0E0E0 !important;
    color: #616161 !important;
    box-shadow: none !important;
    letter-spacing: 0.5px !important;
    transition: all 0.3s ease !important;
}
button[kind="secondary"]:hover {
    background: #FFF5F5 !important;
    border-color: #E53935 !important;
    color: #E53935 !important;
    transform: translateY(-1px) !important;
}

/* ── Method Selection Cards ── */
.method-card {
    background: #FAFAFA;
    border: 1px solid #E0E0E0;
    border-radius: 14px;
    padding: 1.5rem 1rem;
    text-align: center;
    cursor: pointer;
    transition: all 0.3s ease;
}
.method-card:hover {
    background: #FFF5F5;
    border-color: #E53935;
    transform: translateY(-3px);
    box-shadow: 0 8px 25px rgba(229,57,53,0.15);
}
.method-card-icon { font-size: 2rem; margin-bottom: 0.75rem; }
.method-card-title {
    color: #212121;
    font-size: 0.85rem; font-weight: 600;
    margin-bottom: 0.25rem;
}
.method-card-desc {
    color: #9E9E9E;
    font-size: 0.7rem;
}

/* ── OTP Display ── */
.otp-display {
    background: #FFF3E0;
    border: 2px dashed rgba(229,57,53,0.3);
    border-radius: 12px;
    padding: 1rem;
    text-align: center;
    margin: 1rem 0;
}
.otp-code {
    font-size: 2.2rem; font-weight: 700;
    letter-spacing: 8px; color: #E53935;
    font-family: 'Courier New', monospace;
}
.otp-label {
    font-size: 0.72rem;
    color: #9E9E9E;
    margin-top: 0.25rem;
}

/* ── Info Cards ── */
.otp-info-card {
    background: #F5F5F5;
    border: 1px solid #E0E0E0;
    border-radius: 10px;
    padding: 12px 16px;
    margin: 0.8rem 0;
    font-size: 0.75rem;
    color: #757575;
    text-align: center;
    line-height: 1.5;
}

/* ── Footer Links ── */
.auth-footer-links {
    text-align: center;
    margin-top: 1.3rem;
    font-size: 0.78rem;
}
.auth-footer-links a {
    color: #9E9E9E;
    text-decoration: none;
    transition: color 0.2s;
    padding: 0 0.4rem;
}
.auth-footer-links a:hover { color: #E53935; }
.auth-footer-links span { color: #E0E0E0; }

/* ── Back Link ── */
.back-link {
    text-align: center;
    margin-top: 1rem;
    font-size: 0.78rem;
}
.back-link a {
    color: #9E9E9E;
    text-decoration: none;
    transition: color 0.2s;
}
.back-link a:hover { color: #E53935; }

/* ── Error Message ── */
div[data-testid="stAlert"] {
    background: #FFEBEE !important;
    border: 1px solid #FFCDD2 !important;
    border-radius: 10px !important;
    color: #C62828 !important;
}

/* ── Success Box ── */
.success-box {
    background: #E8F5E9;
    border: 1px solid #C8E6C9;
    border-radius: 10px;
    padding: 14px 18px;
    margin: 0.8rem 0;
    font-size: 0.82rem;
    color: #2E7D32;
    text-align: center;
}

/* ── Demo / Info Box ── */
.info-box {
    background: #FFF8E1;
    border: 1px solid #FFE082;
    border-radius: 10px;
    padding: 14px 18px;
    margin-top: 1.2rem;
    font-size: 0.76rem;
    color: #795548;
    text-align: center;
}
.info-box b { color: #5D4037; }
.info-box code {
    background: rgba(229,57,53,0.08);
    color: #E53935;
    padding: 2px 8px;
    border-radius: 4px;
    font-size: 0.73rem;
}

/* ── WhatsApp Notice ── */
.whatsapp-notice {
    background: #E8F5E9;
    border: 1px solid #C8E6C9;
    border-radius: 10px;
    padding: 10px 14px;
    margin: 0.8rem 0;
    font-size: 0.73rem;
    color: #2E7D32;
    display: flex;
    align-items: center;
    gap: 8px;
}
.whatsapp-notice svg { flex-shrink: 0; }

/* ── responsive ── */
@media (max-width: 768px) {
    .auth-card {
        padding: 1.8rem 1.2rem;
        border-radius: 16px;
    }
    .brand-title {
        font-size: 1.3rem;
        letter-spacing: 1.5px;
    }
    .brand-subtitle {
        font-size: 0.68rem;
        letter-spacing: 2px;
    }
    .otp-code {
        font-size: 1.6rem;
        letter-spacing: 5px;
    }
}
</style>
"""


def _render_brand_header():
    """Render the KATALOG SUPPLIER brand header."""
    st.markdown("""
    <div class="brand-header">
        <div class="brand-icon">
            <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="M3 9L12 3L21 9V20C21 20.5304 20.7893 21.0391 20.4142 21.4142C20.0391 21.7893 19.5304 22 19 22H5C4.46957 22 3.96086 21.7893 3.58579 21.4142C3.21071 21.0391 3 20.5304 3 20V9Z" stroke="white" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                <path d="M9 22V12H15V22" stroke="white" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
        </div>
        <h1 class="brand-title">KATALOG SUPPLIER</h1>
        <p class="brand-subtitle">Construction Hardware &amp; Accessories Store</p>
        <div class="brand-divider"></div>
    </div>
    """, unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════
# ── LOGIN PAGE ──
# ═══════════════════════════════════════════════════════════════

def show_login_page():
    """Display login page with elegant dark-themed design."""
    st.markdown(LIGHT_CSS, unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 3, 1])
    with col2:
        st.markdown('<div class="auth-card">', unsafe_allow_html=True)
        _render_brand_header()

        st.markdown('<div class="auth-form-area">', unsafe_allow_html=True)

        username = st.text_input(
            "Email / Username Reseller",
            key="login_user",
            placeholder="Masukkan email atau username",
        )
        password = st.text_input(
            "Kata Sandi",
            type="password",
            key="login_pass",
            placeholder="Masukkan kata sandi",
        )

        col_btn1, col_btn2, col_btn3 = st.columns([1, 2, 1])
        with col_btn2:
            if st.button("Masuk", use_container_width=True, type="primary"):
                _do_login(username, password)

        st.markdown('</div>', unsafe_allow_html=True)

        # ── Footer Links ──
        st.markdown("""
        <div class="auth-footer-links">
            <a href="#">Lupa Kata Sandi</a>
            <span>|</span>
            <a href="javascript:void(0)">Daftar Reseller Baru</a>
        </div>
        """, unsafe_allow_html=True)

        # ── Register Button ──
        col_r1, col_r2, col_r3 = st.columns([1, 2, 1])
        with col_r2:
            if st.button("📝 Daftar Reseller Baru", key="goto_register",
                         use_container_width=True, type="secondary"):
                st.session_state.show_register = True
                st.session_state.register_step = "method"
                st.rerun()

        # ── Demo Credentials ──
        st.markdown('<div class="info-box">'
                     '<b>🔑 Demo Login:</b><br>'
                     'Username: <code>demo</code> &nbsp;|&nbsp; '
                     'Password: <code>demo123</code>'
                     '</div>', unsafe_allow_html=True)

        st.markdown('</div>', unsafe_allow_html=True)


def _do_login(username: str, password: str):
    """Attempt login with username/email/password."""
    # 1) Legacy users
    if username in USERS:
        if USERS[username]["password"] == hash_password(password):
            _set_login_session(username, USERS[username]["nama"],
                               USERS[username]["role"])
            return
        else:
            st.error("Password salah!")
            return

    # 2) Registered reseller by email
    reseller = get_reseller_by_email(username)
    if reseller and reseller.get("password"):
        if reseller["password"] == hash_password(password):
            if not reseller.get("is_verified", True):
                st.warning("Akun belum diverifikasi. Silakan verifikasi terlebih dahulu.")
                return
            _set_login_session(reseller["id"], reseller["nama"], reseller["role"])
            return
        else:
            st.error("Password salah!")
            return

    # 3) By phone
    reseller = get_reseller_by_phone(username)
    if reseller and reseller.get("password"):
        if reseller["password"] == hash_password(password):
            if not reseller.get("is_verified", True):
                st.warning("Akun belum diverifikasi.")
                return
            _set_login_session(reseller["id"], reseller["nama"], reseller["role"])
            return
        else:
            st.error("Password salah!")
            return

    st.error("Username / Email tidak ditemukan!")


def _set_login_session(uid: str, name: str, role: str):
    """Set session state for logged-in user."""
    st.session_state.logged_in = True
    st.session_state.user = name
    st.session_state.role = role
    st.session_state.username = uid
    st.rerun()


# ═══════════════════════════════════════════════════════════════
# ── REGISTER PAGE ──
# ═══════════════════════════════════════════════════════════════

def show_register_page():
    """Display registration page based on current step."""
    st.markdown(LIGHT_CSS, unsafe_allow_html=True)

    step = st.session_state.register_step

    col1, col2, col3 = st.columns([1, 3, 1])
    with col2:
        st.markdown('<div class="auth-card">', unsafe_allow_html=True)

        if step == "method":
            _show_register_method_selection()
        elif step == "otp_input":
            _show_otp_verification()
        elif step == "register_form":
            _show_register_form()
        elif step == "success":
            _show_register_success()

        st.markdown('</div>', unsafe_allow_html=True)


def _show_register_method_selection():
    """Step 1: Choose role and registration method."""
    _render_brand_header()

    # ── Role Selection ──
    st.markdown("""
    <p style="text-align:center;color:#757575;font-size:0.85rem;
    margin-bottom:1rem;">Pilih peran Anda</p>
    """, unsafe_allow_html=True)

    role_col1, role_col2 = st.columns(2)

    with role_col1:
        st.markdown("""
        <div class="method-card" style="border:2px solid #E53935;background:#FFF5F5;">
            <div class="method-card-icon">🛒</div>
            <div class="method-card-title" style="color:#E53935;">Reseller</div>
            <div class="method-card-desc">Beli produk dengan<br>harga reseller</div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("🛒 Saya Reseller", key="role_reseller",
                     use_container_width=True, type="primary"):
            st.session_state.register_role = "reseller"
            st.rerun()

    with role_col2:
        st.markdown("""
        <div class="method-card">
            <div class="method-card-icon">🤝</div>
            <div class="method-card-title">Marketing</div>
            <div class="method-card-desc">Punya downline reseller<br>& dapatkan komisi</div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("🤝 Saya Marketing", key="role_marketing",
                     use_container_width=True, type="secondary"):
            st.session_state.register_role = "marketing"
            st.rerun()

    # If role already selected, show methods
    selected_role = st.session_state.get("register_role", "")

    if selected_role:
        st.markdown(f"""
        <p style="text-align:center;color:#E53935;font-size:0.8rem;font-weight:600;
        margin:1.5rem 0 0.8rem 0;">
            {'🛒' if selected_role == 'reseller' else '🤝'} Daftar sebagai <b>{selected_role.upper()}</b>
        </p>
        """, unsafe_allow_html=True)

        if selected_role == "reseller":
            _show_reseller_methods()
        else:
            _show_marketing_methods()

    # ── Back ──
    st.markdown("""
    <div class="back-link" style="margin-top:1.5rem;">
        Sudah punya akun? <a href="javascript:void(0)">Masuk di sini</a>
    </div>
    """, unsafe_allow_html=True)
    if st.button("← Kembali ke Login", key="back_to_login_1",
                 use_container_width=True, type="secondary"):
        st.session_state.show_register = False
        st.session_state.register_step = "method"
        st.session_state.register_role = ""
        st.rerun()


def _show_reseller_methods():
    """Show registration methods for resellers."""
    col_a, col_b, col_c = st.columns(3)

    with col_a:
        st.markdown("""
        <div class="method-card">
            <div class="method-card-icon">📱</div>
            <div class="method-card-title">No HP / WhatsApp</div>
            <div class="method-card-desc">Verifikasi via SMS<br>atau WhatsApp</div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("📱 Daftar via HP", key="method_phone",
                     use_container_width=True, type="secondary"):
            st.session_state.register_method = "phone"
            st.session_state.register_step = "otp_input"
            st.rerun()

    with col_b:
        st.markdown("""
        <div class="method-card">
            <div class="method-card-icon">✉️</div>
            <div class="method-card-title">Email</div>
            <div class="method-card-desc">Daftar menggunakan<br>alamat email</div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("✉️ Daftar via Email", key="method_email",
                     use_container_width=True, type="secondary"):
            st.session_state.register_method = "email"
            st.session_state.register_step = "register_form"
            st.rerun()

    with col_c:
        st.markdown("""
        <div class="method-card">
            <div class="method-card-icon">
                <svg width="28" height="28" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                    <path d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92a5.06 5.06 0 01-2.2 3.32v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.1z" fill="#4285F4"/>
                    <path d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z" fill="#34A853"/>
                    <path d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z" fill="#FBBC05"/>
                    <path d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z" fill="#EA4335"/>
                </svg>
            </div>
            <div class="method-card-title">Google</div>
            <div class="method-card-desc">Daftar cepat dengan<br>akun Google</div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("🔵 Daftar via Google", key="method_google",
                     use_container_width=True, type="secondary"):
            _start_google_oauth()


def _show_marketing_methods():
    """Show registration methods for marketing users (HP/Email only)."""
    col_a, col_b = st.columns(2)

    with col_a:
        st.markdown("""
        <div class="method-card">
            <div class="method-card-icon">📱</div>
            <div class="method-card-title">No HP / WhatsApp</div>
            <div class="method-card-desc">Verifikasi via SMS<br>atau WhatsApp</div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("📱 Daftar via HP", key="mkt_method_phone",
                     use_container_width=True, type="secondary"):
            st.session_state.register_method = "phone"
            st.session_state.register_step = "otp_input"
            st.rerun()

    with col_b:
        st.markdown("""
        <div class="method-card">
            <div class="method-card-icon">✉️</div>
            <div class="method-card-title">Email</div>
            <div class="method-card-desc">Daftar menggunakan<br>alamat email</div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("✉️ Daftar via Email", key="mkt_method_email",
                     use_container_width=True, type="secondary"):
            st.session_state.register_method = "email"
            st.session_state.register_step = "register_form"
            st.rerun()


# ═══════════════════════════════════════════════════════════════
# ── PHONE OTP FLOW ──
# ═══════════════════════════════════════════════════════════════

def _show_otp_verification():
    """Step 2 for phone: Enter phone number, receive OTP."""
    _render_brand_header()

    st.markdown("""
    <p style="text-align:center;color:rgba(255,255,255,0.6);font-size:0.85rem;
    margin-bottom:0.5rem;">📱 Daftar dengan No HP</p>
    """, unsafe_allow_html=True)

    # WhatsApp notice
    st.markdown("""
    <div class="whatsapp-notice">
        <svg width="18" height="18" viewBox="0 0 24 24" fill="#25D366"><path d="M17.472 14.382c-.297-.149-1.758-.867-2.03-.967-.273-.099-.471-.148-.67.15-.197.297-.767.966-.94 1.164-.173.199-.347.223-.644.075-.297-.15-1.255-.463-2.39-1.475-.883-.788-1.48-1.761-1.653-2.059-.173-.297-.018-.458.13-.606.134-.133.298-.347.446-.52.149-.174.198-.298.298-.497.099-.198.05-.371-.025-.52-.075-.149-.669-1.612-.916-2.207-.242-.579-.487-.5-.669-.51-.173-.008-.371-.01-.57-.01-.198 0-.52.074-.792.372-.272.297-1.04 1.016-1.04 2.479 0 1.462 1.065 2.875 1.213 3.074.149.198 2.096 3.2 5.077 4.487.709.306 1.262.489 1.694.625.712.227 1.36.195 1.871.118.571-.085 1.758-.719 2.006-1.413.248-.694.248-1.289.173-1.413-.074-.124-.272-.198-.57-.347m-5.421 7.403h-.004a9.87 9.87 0 01-5.031-1.378l-.361-.214-3.741.982.998-3.648-.235-.374a9.86 9.86 0 01-1.51-5.26c.001-5.45 4.436-9.884 9.888-9.884 2.64 0 5.122 1.03 6.988 2.898a9.825 9.825 0 012.893 6.994c-.003 5.45-4.437 9.884-9.885 9.884m8.413-18.297A11.815 11.815 0 0012.05 0C5.495 0 .16 5.335.157 11.892c0 2.096.547 4.142 1.588 5.945L.057 24l6.305-1.654a11.882 11.882 0 005.683 1.448h.005c6.554 0 11.89-5.335 11.893-11.893a11.821 11.821 0 00-3.48-8.413z"/></svg>
        <span>Kode OTP akan dikirim melalui <b>WhatsApp</b> ke nomor Anda</span>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="auth-form-area">', unsafe_allow_html=True)

    phone = st.text_input(
        "Nomor HP / WhatsApp",
        key="register_phone_input",
        placeholder="Contoh: 081234567890",
        value=st.session_state.get("register_phone", ""),
    )

    col_btn1, col_btn2, col_btn3 = st.columns([1, 2, 1])
    with col_btn2:
        if st.button("📤 Kirim Kode OTP", use_container_width=True, type="primary"):
            if not phone or len(phone.strip()) < 10:
                st.error("Masukkan nomor HP yang valid (minimal 10 digit)")
            else:
                existing = get_reseller_by_phone(phone.strip())
                if existing:
                    st.error("Nomor HP ini sudah terdaftar. Silakan login.")
                else:
                    otp_code = generate_otp(phone.strip())
                    st.session_state.register_phone = phone.strip()
                    st.session_state.register_otp = otp_code

                    # In dev mode: show OTP in-app
                    st.markdown(f"""
                    <div class="otp-display">
                        <div style="font-size:0.7rem;color:rgba(255,255,255,0.4);margin-bottom:0.5rem;">
                            ⚠️ DEVELOPMENT MODE — Kode OTP
                        </div>
                        <div class="otp-code">{otp_code}</div>
                        <div class="otp-label">Kode berlaku 5 menit</div>
                    </div>
                    """, unsafe_allow_html=True)

                    st.success("✅ Kode OTP telah dikirim ke WhatsApp Anda!")
                    st.info("Silakan masukkan kode OTP di bawah:")

    # OTP Input
    if st.session_state.get("register_otp"):
        otp_input = st.text_input(
            "Masukkan Kode OTP (6 digit)",
            key="otp_code_input",
            placeholder="Masukkan 6 digit kode",
            max_chars=6,
        )

        col_v1, col_v2, col_v3 = st.columns([1, 2, 1])
        with col_v2:
            if st.button("✅ Verifikasi OTP", use_container_width=True, type="primary"):
                if verify_otp(st.session_state.register_phone, otp_input.strip()):
                    delete_otp(st.session_state.register_phone)
                    st.session_state.register_step = "register_form"
                    st.rerun()
                else:
                    st.error("Kode OTP salah atau sudah kadaluarsa!")

            if st.button("🔄 Kirim Ulang Kode", use_container_width=True, type="secondary"):
                new_otp = generate_otp(st.session_state.register_phone)
                st.session_state.register_otp = new_otp
                st.rerun()

    st.markdown('</div>', unsafe_allow_html=True)

    if st.button("← Pilih Metode Lain", key="back_to_method_otp",
                 use_container_width=True, type="secondary"):
        st.session_state.register_step = "method"
        st.session_state.register_otp = ""
        st.rerun()


# ═══════════════════════════════════════════════════════════════
# ── REGISTER FORM (after OTP / for Email) ──
# ═══════════════════════════════════════════════════════════════

def _show_register_form():
    """Step 3: Fill in registration details."""
    method = st.session_state.register_method
    role = st.session_state.get("register_role", "reseller")

    if role == "marketing":
        title = "🤝 Daftar Marketing"
        subtitle = "Dapatkan kode referral & komisi dari reseller"
    elif method == "phone":
        title = "📱 Lengkapi Data Diri"
        subtitle = f"Nomor HP: {st.session_state.register_phone}"
    else:
        title = "✉️ Daftar Reseller"
        subtitle = "Lengkapi data diri Anda"

    _render_brand_header()

    st.markdown(f"""
    <p style="text-align:center;color:#757575;font-size:0.85rem;
    margin-bottom:0.25rem;">{title}</p>
    <p style="text-align:center;color:#9E9E9E;font-size:0.75rem;
    margin-bottom:1.2rem;">{subtitle}</p>
    """, unsafe_allow_html=True)

    st.markdown('<div class="auth-form-area">', unsafe_allow_html=True)

    name = st.text_input(
        "Nama Lengkap",
        key="reg_name",
        placeholder="Masukkan nama lengkap Anda",
    )
    email_reg = st.text_input(
        "Email" if method == "email" else "Email (Opsional)",
        key="reg_email_opt",
        placeholder="Masukkan alamat email",
    )

    # Referral code input for resellers
    upline_code = ""
    if role == "reseller":
        st.markdown("""
        <p style="font-size:0.75rem;color:#757575;margin:0.5rem 0 0.2rem 0;">
        🔗 Kode Referral Marketing (opsional)
        </p>
        """, unsafe_allow_html=True)
        upline_input = st.text_input(
            "Kode Referral",
            key="reg_referral",
            placeholder="Masukkan kode referral (jika ada)",
            label_visibility="collapsed",
        )
        if upline_input.strip():
            marketing = get_marketing_by_code(upline_input.strip())
            if marketing:
                st.success(f"✅ Marketing: **{marketing['nama']}** — Komisi: {marketing.get('commission_rate', 5)}%")
                upline_code = upline_input.strip()
            else:
                st.warning("⚠️ Kode referral tidak ditemukan. Akan didaftarkan tanpa marketing.")

    # Marketing commission info
    if role == "marketing":
        st.markdown("""
        <div class="otp-info-card" style="text-align:left;">
            <b>💡 Keuntungan Marketing:</b><br>
            • Dapatkan kode referral unik<br>
            • Komisi <b>5%</b> dari setiap pembelian reseller Anda<br>
            • Pantau downline dan komisi di dashboard
        </div>
        """, unsafe_allow_html=True)

    password_reg = st.text_input(
        "Buat Kata Sandi",
        type="password",
        key="reg_password",
        placeholder="Minimal 6 karakter",
    )
    confirm_password = st.text_input(
        "Konfirmasi Kata Sandi",
        type="password",
        key="reg_confirm_password",
        placeholder="Ketik ulang kata sandi",
    )

    col_btn1, col_btn2, col_btn3 = st.columns([1, 2, 1])
    with col_btn2:
        btn_label = "🎉 Daftar Marketing" if role == "marketing" else "🎉 Daftar Sekarang"
        if st.button(btn_label, use_container_width=True, type="primary"):
            if not name.strip():
                st.error("Nama lengkap harus diisi!")
            elif method == "email" and not email_reg.strip():
                st.error("Email harus diisi!")
            elif not password_reg or len(password_reg) < 6:
                st.error("Kata sandi minimal 6 karakter!")
            elif password_reg != confirm_password:
                st.error("Konfirmasi kata sandi tidak cocok!")
            else:
                if method == "email" and email_reg.strip():
                    existing = get_reseller_by_email(email_reg.strip())
                    if existing:
                        st.error("Email ini sudah terdaftar. Silakan login.")
                        st.stop()

                phone_val = st.session_state.register_phone if method == "phone" else ""

                reseller = register_reseller(
                    email=email_reg.strip() if email_reg else "",
                    phone=phone_val,
                    password=password_reg,
                    name=name.strip(),
                    register_method=method,
                    upline_code=upline_code,
                    role=role,
                )

                if method == "phone":
                    verify_reseller(reseller["id"])

                st.session_state.register_step = "success"
                st.session_state.register_name = name.strip()
                st.rerun()

    st.markdown('</div>', unsafe_allow_html=True)

    back_step = "otp_input" if method == "phone" else "method"
    back_label = "← Kembali ke Verifikasi OTP" if method == "phone" else "← Pilih Metode Lain"

    if st.button(back_label, key="back_to_prev",
                 use_container_width=True, type="secondary"):
        st.session_state.register_step = back_step
        st.rerun()


def _show_register_success():
    """Registration success page."""
    _render_brand_header()

    name = st.session_state.get("register_name", "Reseller")

    st.markdown(f"""
    <div class="success-box">
        <div style="font-size:2.5rem;margin-bottom:0.5rem;">🎉</div>
        <div style="font-size:1rem;font-weight:600;color:#A5D6A7;margin-bottom:0.3rem;">
            Pendaftaran Berhasil!
        </div>
        <div style="font-size:0.82rem;color:rgba(255,255,255,0.5);">
            Selamat datang, <b>{name}</b>!<br>
            Akun Anda telah berhasil dibuat.
        </div>
    </div>
    """, unsafe_allow_html=True)

    col_btn1, col_btn2, col_btn3 = st.columns([1, 2, 1])
    with col_btn2:
        if st.button("🔑 Masuk Sekarang", use_container_width=True, type="primary"):
            st.session_state.show_register = False
            st.session_state.register_step = "method"
            st.session_state.register_otp = ""
            st.rerun()


# ═══════════════════════════════════════════════════════════════
# ── GOOGLE OAUTH ──
# ═══════════════════════════════════════════════════════════════

GOOGLE_CLIENT_ID = "YOUR_GOOGLE_CLIENT_ID.apps.googleusercontent.com"
GOOGLE_CLIENT_SECRET = "YOUR_GOOGLE_CLIENT_SECRET"
GOOGLE_REDIRECT_URI = "http://localhost:8501"


def _start_google_oauth():
    """Start Google OAuth flow."""
    try:
        from google_auth_oauthlib.flow import Flow

        flow = Flow.from_client_config(
            {
                "web": {
                    "client_id": GOOGLE_CLIENT_ID,
                    "client_secret": GOOGLE_CLIENT_SECRET,
                    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                    "token_uri": "https://oauth2.googleapis.com/token",
                    "redirect_uris": [GOOGLE_REDIRECT_URI],
                }
            },
            scopes=[
                "openid",
                "https://www.googleapis.com/auth/userinfo.email",
                "https://www.googleapis.com/auth/userinfo.profile",
            ],
        )
        flow.redirect_uri = GOOGLE_REDIRECT_URI

        auth_url, _ = flow.authorization_url(
            access_type="offline",
            include_granted_scopes="true",
            prompt="consent",
        )

        st.session_state.google_auth_url = auth_url

        st.markdown(f"""
        <meta http-equiv="refresh" content="0;url={auth_url}">
        <p style="text-align:center;color:rgba(255,255,255,0.5);">
            Mengarahkan ke Google...<br>
            <a href="{auth_url}" style="color:#4285F4;">Klik di sini jika tidak otomatis</a>
        </p>
        """, unsafe_allow_html=True)
        st.stop()

    except ImportError:
        st.error(
            "Library Google OAuth tidak tersedia.\n\n"
            "Install dengan: `pip install google-auth-oauthlib google-auth requests`"
        )
    except Exception as e:
        st.error(f"Gagal memulai Google OAuth: {e}")


def _handle_google_callback():
    """Handle Google OAuth callback with authorization code."""
    query_params = st.query_params
    code = query_params.get("code")
    if not code:
        return

    try:
        from google_auth_oauthlib.flow import Flow
        import requests

        flow = Flow.from_client_config(
            {
                "web": {
                    "client_id": GOOGLE_CLIENT_ID,
                    "client_secret": GOOGLE_CLIENT_SECRET,
                    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                    "token_uri": "https://oauth2.googleapis.com/token",
                    "redirect_uris": [GOOGLE_REDIRECT_URI],
                }
            },
            scopes=[
                "openid",
                "https://www.googleapis.com/auth/userinfo.email",
                "https://www.googleapis.com/auth/userinfo.profile",
            ],
        )
        flow.redirect_uri = GOOGLE_REDIRECT_URI
        flow.fetch_token(code=code)

        credentials = flow.credentials

        user_info = requests.get(
            "https://www.googleapis.com/oauth2/v3/userinfo",
            headers={"Authorization": f"Bearer {credentials.token}"},
            timeout=10,
        ).json()

        google_id = user_info.get("sub")
        google_email = user_info.get("email", "")
        google_name = user_info.get("name", "")

        if not google_id or not google_email:
            st.error("Gagal mendapatkan data dari Google.")
            return

        existing = get_reseller_by_google_id(google_id)
        if not existing:
            existing = get_reseller_by_email(google_email)

        if existing:
            _set_login_session(existing["id"], existing["nama"], existing["role"])
            return

        reseller = register_reseller(
            google_id=google_id,
            google_email=google_email,
            google_name=google_name,
            register_method="google",
        )

        st.query_params.clear()
        _set_login_session(reseller["id"], reseller["nama"], reseller["role"])

    except ImportError:
        st.error("Library Google OAuth tidak tersedia.")
    except Exception as e:
        st.error(f"Gagal autentikasi Google: {e}")


# ── Logout ──
def logout():
    """Logout user and clear session."""
    st.session_state.logged_in = False
    st.session_state.user = None
    st.session_state.role = None
    st.session_state.username = None
    st.session_state.show_register = False
    st.session_state.register_step = "method"
    if "cart" in st.session_state:
        st.session_state.cart = []
    st.rerun()

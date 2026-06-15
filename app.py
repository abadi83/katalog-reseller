"""KATALOG RESELLER - Streamlit PWA
Aplikasi Katalog Barang dengan SKU untuk Reseller Toko.
Mobile-friendly & installable as PWA.
"""

import streamlit as st
import streamlit.components.v1 as components
from utils.auth import check_login, logout, show_auth_page
from utils.cart import (
    init_cart, add_to_cart, remove_from_cart,
    update_cart_qty, get_cart_total, get_cart_count, clear_cart
)
from utils.helpers import (
    format_rupiah, search_products, filter_products,
    show_product_card, show_product_detail, show_cart_sidebar
)
from utils.admin import (
    page_admin, get_products, get_categories,
    get_subcategories, get_brands_from_products,
    ensure_products_in_state
)
from utils.chat import page_chat, init_chat, get_unread_count
from data.commissions import add_commission, get_commissions_for_marketing, get_total_commission, get_pending_commission
from data.resellers import get_reseller_by_email, get_downline_list, get_all_resellers

# ── Page Config ──────────────────────────────────────────────
st.set_page_config(
    page_title="Katalog Reseller",
    page_icon="📦",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        "Get Help": None,
        "Report a bug": None,
        "About": "Katalog Reseller v1.0 - Aplikasi Katalog SKU untuk Reseller",
    },
)

# ── PWA Injection ────────────────────────────────────────────
def inject_pwa():
    """Inject PWA manifest and service worker into Streamlit."""
    components.html("""
    <script>
        // Register Service Worker
        if ('serviceWorker' in navigator) {
            window.addEventListener('load', function() {
                navigator.serviceWorker.register('./service-worker.js')
                    .then(function(reg) {
                        console.log('SW registered:', reg.scope);
                    })
                    .catch(function(err) {
                        console.log('SW failed:', err);
                    });
            });
        }
    </script>
    <link rel="manifest" href="./manifest.json">
    <meta name="theme-color" content="#E53935">
    <meta name="apple-mobile-web-app-capable" content="yes">
    <meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
    <meta name="apple-mobile-web-app-title" content="Katalog Reseller">
    <link rel="apple-touch-icon" href="https://placehold.co/192x192/E53935/FFF?text=KR">
    """, height=0)


# ── WhatsApp Floating Button ─────────────────────────────────
# Ganti nomor di bawah dengan nomor WhatsApp Admin (format: 628xxxxxxxxxx)
ADMIN_WA_NUMBER = "6285211112525"
ADMIN_WA_NAME = "Admin Katalog"


def inject_3d_viewer():
    """Inject Google model-viewer script for 3D product preview."""
    components.html("""
    <script type="module" src="https://unpkg.com/@google/model-viewer/dist/model-viewer.min.js"></script>
    """, height=0)

def inject_whatsapp_float():
    """Inject floating WhatsApp button on all pages."""
    wa_link = f"https://wa.me/{ADMIN_WA_NUMBER}?text=Halo%20Admin%20Katalog%2C%20saya%20mau%20tanya..."
    st.markdown(f"""
    <div class="wa-float">
        <div class="wa-float-label">💬 Chat Admin via WhatsApp</div>
        <a href="{wa_link}" target="_blank" class="wa-float-btn" title="Chat via WhatsApp">
            <svg viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                <path d="M17.472 14.382c-.297-.149-1.758-.867-2.03-.967-.273-.099-.471-.148-.67.15-.197.297-.767.966-.94 1.164-.173.199-.347.223-.644.075-.297-.15-1.255-.463-2.39-1.475-.883-.788-1.48-1.761-1.653-2.059-.173-.297-.018-.458.13-.606.134-.133.298-.347.446-.52.149-.174.198-.298.298-.497.099-.198.05-.371-.025-.52-.075-.149-.669-1.612-.916-2.207-.242-.579-.487-.5-.669-.51-.173-.008-.371-.01-.57-.01-.198 0-.52.074-.792.372-.272.297-1.04 1.016-1.04 2.479 0 1.462 1.065 2.875 1.213 3.074.149.198 2.096 3.2 5.077 4.487.709.306 1.262.489 1.694.625.712.227 1.36.195 1.871.118.571-.085 1.758-.719 2.006-1.413.248-.694.248-1.289.173-1.413-.074-.124-.272-.198-.57-.347m-5.421 7.403h-.004a9.87 9.87 0 0 1-5.031-1.378l-.361-.214-3.741.982.998-3.648-.235-.374a9.86 9.86 0 0 1-1.51-5.26c.001-5.45 4.436-9.884 9.888-9.884 2.64 0 5.122 1.03 6.988 2.898a9.825 9.825 0 0 1 2.893 6.994c-.003 5.45-4.437 9.884-9.885 9.884m8.413-18.297A11.815 11.815 0 0 0 12.05 0C5.495 0 .16 5.335.157 11.892c0 2.096.547 4.142 1.588 5.945L.057 24l6.305-1.654a11.882 11.882 0 0 0 5.683 1.448h.005c6.554 0 11.89-5.335 11.893-11.893a11.821 11.821 0 0 0-3.48-8.413z"/>
            </svg>
        </a>
    </div>
    """, unsafe_allow_html=True)


# ── Custom CSS ────────────────────────────────────────────────
def inject_css():
    st.markdown("""
    <style>
    /* ── Global ── */
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700&display=swap');

    * {
        font-family: 'Plus Jakarta Sans', sans-serif;
    }

    /* ── Hide Streamlit branding (keep hamburger menu visible) ── */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header[data-testid="stHeader"] {
        background: transparent;
    }
    /* Hide deploy button & star but keep hamburger */
    button[data-testid="stBaseButton-header"] {display: none;}
    button[data-testid="stBaseButton-headerNoPadding"] {display: none;}

    /* ── Top Navbar ── */
    .navbar {
        background: linear-gradient(135deg, #E53935, #C62828);
        color: white;
        padding: 12px 20px;
        display: flex;
        align-items: center;
        justify-content: space-between;
        position: sticky;
        top: 0;
        z-index: 999;
        box-shadow: 0 2px 12px rgba(0,0,0,0.15);
        flex-wrap: wrap;
        gap: 8px;
    }
    .navbar-brand {
        font-size: 1.3rem;
        font-weight: 700;
        letter-spacing: -0.5px;
    }
    .navbar-user {
        font-size: 0.85rem;
        opacity: 0.9;
    }
    .navbar-menu {
        display: flex;
        gap: 8px;
        flex-wrap: wrap;
        font-size: 0.8rem;
    }
    .navbar-menu a {
        color: white;
        text-decoration: none;
        padding: 6px 12px;
        border-radius: 20px;
        background: rgba(255,255,255,0.15);
        transition: background 0.2s;
    }
    .navbar-menu a:hover {
        background: rgba(255,255,255,0.3);
    }

    /* ── Category Pills ── */
    .cat-pill {
        display: inline-block;
        padding: 6px 16px;
        margin: 4px;
        border-radius: 20px;
        background: #F5F5F5;
        color: #616161;
        font-size: 0.8rem;
        font-weight: 500;
        cursor: pointer;
        transition: all 0.2s;
        border: 1px solid #E0E0E0;
    }
    .cat-pill:hover {
        background: #FFEBEE;
        color: #E53935;
        border-color: #E53935;
    }
    .cat-pill.active {
        background: #E53935;
        color: white;
        border-color: #E53935;
    }

    /* ── Product Grid ── */
    .product-grid {
        display: grid;
        grid-template-columns: repeat(auto-fill, minmax(220px, 1fr));
        gap: 16px;
    }

    /* ── Mobile responsive ── */
    @media (max-width: 768px) {
        .navbar {
            padding: 8px 12px;
            flex-direction: column;
            align-items: flex-start;
        }
        .navbar-brand {
            font-size: 1.1rem;
        }
        .navbar-menu {
            font-size: 0.75rem;
            width: 100%;
        }
        .navbar-menu a {
            flex: 1;
            text-align: center;
            padding: 6px 8px;
        }
        .product-grid {
            grid-template-columns: repeat(auto-fill, minmax(160px, 1fr));
            gap: 10px;
        }
    }

    /* ── Buttons ── */
    .stButton > button {
        border-radius: 10px !important;
        font-weight: 600 !important;
        transition: all 0.2s !important;
    }
    .stButton > button:hover {
        transform: translateY(-1px);
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
    }

    /* ── Checkout Card ── */
    .checkout-card {
        background: white;
        border-radius: 12px;
        padding: 20px;
        box-shadow: 0 2px 12px rgba(0,0,0,0.08);
        margin-bottom: 12px;
    }

    /* ── Toast Style ── */
    .toast {
        position: fixed;
        bottom: 20px;
        right: 20px;
        background: #4CAF50;
        color: white;
        padding: 12px 20px;
        border-radius: 12px;
        box-shadow: 0 4px 16px rgba(0,0,0,0.2);
        z-index: 9999;
        font-weight: 600;
        animation: slideIn 0.3s ease;
    }
    @keyframes slideIn {
        from { transform: translateY(100px); opacity: 0; }
        to { transform: translateY(0); opacity: 1; }
    }

    /* ── Empty state ── */
    .empty-state {
        text-align: center;
        padding: 60px 20px;
        color: #BDBDBD;
    }
    .empty-state h3 {
        font-size: 1.5rem;
        color: #9E9E9E;
    }
    .empty-state p {
        font-size: 0.9rem;
    }

    /* ── Margin badge ── */
    .badge-sale {
        background: #E53935;
        color: white;
        padding: 2px 8px;
        border-radius: 4px;
        font-size: 0.7rem;
        font-weight: 700;
    }

    /* ── WhatsApp Floating Button ── */
    .wa-float {
        position: fixed;
        bottom: 24px;
        right: 24px;
        z-index: 9999;
        display: flex;
        flex-direction: column;
        align-items: flex-end;
        gap: 8px;
    }
    .wa-float-btn {
        width: 60px;
        height: 60px;
        border-radius: 50%;
        background: #25D366;
        box-shadow: 0 4px 16px rgba(37, 211, 102, 0.4);
        display: flex;
        align-items: center;
        justify-content: center;
        cursor: pointer;
        transition: all 0.3s ease;
        text-decoration: none;
        position: relative;
        animation: wa-pulse 2s infinite;
    }
    .wa-float-btn:hover {
        transform: scale(1.1);
        box-shadow: 0 6px 24px rgba(37, 211, 102, 0.6);
    }
    .wa-float-btn svg {
        width: 32px;
        height: 32px;
        fill: white;
    }
    .wa-float-label {
        background: white;
        color: #333;
        padding: 8px 16px;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: 600;
        box-shadow: 0 2px 8px rgba(0,0,0,0.15);
        white-space: nowrap;
        opacity: 0;
        transform: translateX(20px);
        transition: all 0.3s ease;
        pointer-events: none;
    }
    .wa-float:hover .wa-float-label {
        opacity: 1;
        transform: translateX(0);
    }
    @keyframes wa-pulse {
        0% { box-shadow: 0 4px 16px rgba(37, 211, 102, 0.4); }
        50% { box-shadow: 0 4px 28px rgba(37, 211, 102, 0.7); }
        100% { box-shadow: 0 4px 16px rgba(37, 211, 102, 0.4); }
    }
    @media (max-width: 768px) {
        .wa-float { bottom: 16px; right: 16px; }
        .wa-float-btn { width: 52px; height: 52px; }
        .wa-float-btn svg { width: 28px; height: 28px; }
    }
    </style>
    """, unsafe_allow_html=True)


# ── Navigation Bar ───────────────────────────────────────────
def show_navbar():
    cols = st.columns([3, 2, 1])
    with cols[0]:
        st.markdown(
            '<div class="navbar-brand">📦 KATALOG RESELLER</div>',
            unsafe_allow_html=True
        )
    with cols[1]:
        st.markdown(
            f'<div class="navbar-user">👋 {st.session_state.user} '
            f'({st.session_state.role.upper()})</div>',
            unsafe_allow_html=True
        )
    with cols[2]:
        if st.button("🚪 Logout", use_container_width=True, key="logout_btn"):
            logout()


# ── Category Pills ───────────────────────────────────────────
def show_category_pills():
    selected_cat = st.session_state.get("selected_category", "Semua Kategori")
    categories = get_categories()
    cols = st.columns(min(len(categories) + 2, 8))
    cats = ["Semua Kategori"] + categories

    for i, cat in enumerate(cats):
        col_idx = i % 8
        with cols[col_idx]:
            if cat == "SALE":
                label = f"🔥 {cat}"
            else:
                label = cat.replace("FASHION ", "")
            is_active = selected_cat == cat
            btn_type = "primary" if is_active else "secondary"
            if st.button(
                label, key=f"cat_{cat}",
                use_container_width=True,
                type=btn_type,
            ):
                st.session_state.selected_category = cat
                if cat == "Semua Kategori":
                    st.session_state.selected_brand = "Semua Brand"
                st.rerun()


# ── Filters Sidebar ──────────────────────────────────────────
def show_filters():
    with st.sidebar:
        st.markdown("### 🔍 Filter Produk")

        # Search
        search_query = st.text_input(
            "🔎 Kata kunci",
            placeholder="Cari nama, SKU, brand...",
            key="search_input"
        )

        st.markdown("---")

        # Category
        selected_cat = st.selectbox(
            "📂 Kategori",
            ["Semua Kategori"] + get_categories(),
            key="filter_category"
        )

        # Brand
        selected_brand = st.selectbox(
            "🏷️ Brand",
            ["Semua Brand"] + get_brands_from_products(),
            key="filter_brand"
        )

        # Subcategory
        selected_subcat = st.selectbox(
            "📌 Subkategori",
            ["Semua Subkategori"] + get_subcategories(),
            key="filter_subcat"
        )

        st.markdown("---")

        # Toggles
        available_only = st.checkbox("📦 Tersedia (Cek Stok)", value=False,
                                     key="filter_available")
        can_return = st.checkbox("↩️ Bisa Retur", value=False,
                                 key="filter_return")

        st.markdown("---")

        # Sort
        sort_by = st.selectbox(
            "📊 Urutkan",
            ["Default", "Harga Terendah", "Harga Tertinggi",
             "Stok Terbanyak", "Margin Terbesar"],
            key="sort_by"
        )

        # Reset
        if st.button("🔄 Reset Filter", use_container_width=True):
            st.session_state.filter_category = "Semua Kategori"
            st.session_state.filter_brand = "Semua Brand"
            st.session_state.filter_subcat = "Semua Subkategori"
            st.session_state.filter_available = False
            st.session_state.filter_return = False
            st.session_state.sort_by = "Default"
            st.session_state.search_input = ""
            st.rerun()

        # Cart summary
        st.markdown("---")
        show_cart_sidebar()

    return {
        "search": search_query,
        "category": selected_cat,
        "brand": selected_brand,
        "subcategory": selected_subcat,
        "available_only": available_only,
        "can_return": can_return,
        "sort_by": sort_by,
    }


# ── Product Detail Page ─────────────────────────────────────
def page_product_detail():
    """Full product detail page like Shopee."""
    products = get_products()
    sku = st.session_state.get("selected_product_sku")
    product = next((p for p in products if p["sku"] == sku), None)

    if not product:
        st.session_state.selected_product_sku = None
        st.rerun()

    # ── Back + Action Bar ──
    col_back, col_title, col_actions = st.columns([1, 5, 2])
    with col_back:
        if st.button("← Kembali", key="back_to_catalog", use_container_width=True):
            st.session_state.selected_product_sku = None
            st.rerun()
    with col_title:
        st.markdown(f"### {product['name']}")
    with col_actions:
        if st.session_state.get("logged_in", False):
            st.caption(f"Stok: **{product['stock']}** pcs")
        else:
            st.caption("🔑 Login untuk beli")

    st.markdown("---")

    # ── Main Content: Image Gallery + Info ──
    col_img, col_info = st.columns([1, 1])

    images = product.get("images", [])
    if not images and product.get("image"):
        images = [product["image"]]
    if not images:
        images = ["https://placehold.co/600x600/E53935/FFF?text=NO+FOTO"]

    with col_img:
        # Main image
        img_key = f"detail_main_{sku}"
        if f"{img_key}_idx" not in st.session_state:
            st.session_state[f"{img_key}_idx"] = 0

        current_idx = st.session_state[f"{img_key}_idx"]
        st.markdown(f"""
        <div style="aspect-ratio:1; overflow:hidden; border-radius:16px;
                    background:#F5F5F5; border: 1px solid #E0E0E0;">
            <img src="{images[current_idx]}"
                 style="width:100%; height:100%; object-fit:cover;"
                 alt="{product['name']}">
        </div>
        """, unsafe_allow_html=True)

        # Thumbnails
        if len(images) > 1:
            st.caption(f"📷 {len(images)} foto — klik untuk pilih")
            thumb_cols = st.columns(min(len(images), 5))
            for i, img in enumerate(images):
                col_idx = i % 5
                if i < len(thumb_cols):
                    with thumb_cols[col_idx]:
                        border = "3px solid #E53935" if i == current_idx else "2px solid #E0E0E0"
                        st.markdown(f"""
                        <div style="aspect-ratio:1; border-radius:8px; overflow:hidden;
                                    border:{border}; cursor:pointer;
                                    opacity:{1 if i == current_idx else 0.5};">
                            <img src="{img}" style="width:100%; height:100%; object-fit:cover;">
                        </div>
                        """, unsafe_allow_html=True)
                        if st.button(f"Foto {i+1}", key=f"thumb_{sku}_{i}"):
                            st.session_state[f"{img_key}_idx"] = i
                            st.rerun()

    with col_info:
        # SKU & Brand
        st.markdown(f"""
        <div style="background:#FFF3E0; padding:8px 12px; border-radius:8px; margin-bottom:12px;">
            <span style="color:#E65100; font-weight:600; font-size:0.85rem;">SKU: {product['sku']}</span>
            <span style="float:right; color:#757575; font-size:0.8rem;">{product['brand']}</span>
        </div>
        """, unsafe_allow_html=True)

        # Category
        st.markdown(f"📂 {product['category']} › {product['subcategory']}")

        # Price section
        margin = product["price_retail"] - product["price_reseller"]
        margin_pct = round((margin / product["price_retail"]) * 100)

        st.markdown(f"""
        <div style="background:#FFF5F5; padding:16px; border-radius:12px;
                    border:1px solid #FFCDD2; margin:12px 0;">
            <div style="font-size:1.6rem; font-weight:700; color:#E53935;">
                {format_rupiah(product['price_reseller'])}
            </div>
            <div style="font-size:0.9rem; color:#9E9E9E; text-decoration:line-through;">
                {format_rupiah(product['price_retail'])}
            </div>
            <div style="margin-top:8px; font-size:0.85rem; color:#2E7D32; font-weight:600;">
                💰 Margin {margin_pct}% — Untung {format_rupiah(margin)} / pcs
            </div>
        </div>
        """, unsafe_allow_html=True)

        # Stock & Order info
        col_s1, col_s2, col_s3 = st.columns(3)
        with col_s1:
            st.metric("📦 Stok", f"{product['stock']} pcs")
        with col_s2:
            st.metric("📏 Min. Order", f"{product['min_order']} pcs")
        with col_s3:
            st.metric("⚖️ Berat", product.get("weight", "-"))

        # Colors & Sizes
        if product.get("colors"):
            st.markdown(f"🎨 **Warna:** {', '.join(product['colors'])}")
        if product.get("sizes"):
            st.markdown(f"📏 **Ukuran:** {', '.join(product['sizes'])}")

        # Return policy
        if product.get("can_return"):
            st.success("✅ Produk ini **BISA RETUR** dalam 7 hari")

        # ── Add to Cart ──
        if st.session_state.get("logged_in", False):
            st.markdown("---")
            qty_col, btn_col, _ = st.columns([1, 2, 1])
            with qty_col:
                order_qty = st.number_input(
                    "Jumlah",
                    min_value=product["min_order"],
                    max_value=product["stock"],
                    value=product["min_order"],
                    step=1,
                    key=f"detail_qty_{sku}"
                )
            with btn_col:
                subtotal = order_qty * product["price_reseller"]
                if st.button(f"🛒 Tambah ke Keranjang — {format_rupiah(subtotal)}",
                             key=f"detail_add_{sku}",
                             use_container_width=True, type="primary"):
                    add_to_cart(sku, product["name"], product["price_reseller"], order_qty)
                    st.toast(f"✅ {product['name'][:40]} ×{order_qty} ditambahkan!", icon="🛒")
                    st.rerun()
        else:
            st.info("🔑 **Login terlebih dahulu** untuk menambah ke keranjang")

    # ── Description ──
    st.markdown("---")
    st.markdown("### 📝 Deskripsi Produk")
    st.markdown(f"""
    <div style="background:white; padding:16px; border-radius:12px;
                border:1px solid #E0E0E0; line-height:1.8;">
        {product.get('description', 'Tidak ada deskripsi.')}
    </div>
    """, unsafe_allow_html=True)

    # ── Navigation ──
    st.markdown("---")
    if st.button("← Kembali ke Katalog", key="back_catalog_bottom",
                 use_container_width=True, type="secondary"):
        st.session_state.selected_product_sku = None
        st.rerun()


# ── Product Catalog Page ─────────────────────────────────────
def page_catalog():
    """Main catalog page with product grid. Shows detail page if product selected."""
    # If a product is selected, show detail page
    if st.session_state.get("selected_product_sku"):
        page_product_detail()
        return

    st.markdown("## 📋 Daftar Produk")

    # Show category pills
    show_category_pills()

    # Get filters
    filters = show_filters()

    # Apply filters
    products = filter_products(
        category=filters["category"],
        brand=filters["brand"],
        subcategory=filters["subcategory"],
        available_only=filters["available_only"],
        can_return_only=filters["can_return"],
    )

    # Apply search
    if filters["search"]:
        products = [
            p for p in products
            if (filters["search"].lower() in p["name"].lower()
                or filters["search"].lower() in p["sku"].lower()
                or filters["search"].lower() in p["brand"].lower()
                or filters["search"].lower() in p["subcategory"].lower())
        ]

    # Sort
    if filters["sort_by"] == "Harga Terendah":
        products = sorted(products, key=lambda p: p["price_reseller"])
    elif filters["sort_by"] == "Harga Tertinggi":
        products = sorted(products, key=lambda p: p["price_reseller"],
                          reverse=True)
    elif filters["sort_by"] == "Stok Terbanyak":
        products = sorted(products, key=lambda p: p["stock"], reverse=True)
    elif filters["sort_by"] == "Margin Terbesar":
        products = sorted(
            products,
            key=lambda p: p["price_retail"] - p["price_reseller"],
            reverse=True
        )

    # Show result count
    st.caption(f"Menampilkan {len(products)} dari {len(get_products())} produk")
    st.markdown("---")

    if not products:
        st.markdown("""
        <div class="empty-state">
            <h3>😕 Produk tidak ditemukan</h3>
            <p>Coba ubah filter atau kata kunci pencarian</p>
        </div>
        """, unsafe_allow_html=True)
        return

    # Product grid
    cols_per_row = 4
    for i in range(0, len(products), cols_per_row):
        cols = st.columns(cols_per_row)
        for j in range(cols_per_row):
            idx = i + j
            if idx < len(products):
                product = products[idx]
                with cols[j]:
                    show_product_card(product)

                    # "Lihat Detail" button
                    col_see, col_add = st.columns([1, 1])
                    with col_see:
                        if st.button("🔍 Lihat Detail", key=f"see_{product['sku']}",
                                     use_container_width=True):
                            st.session_state.selected_product_sku = product["sku"]
                            st.rerun()
                    with col_add:
                        if st.session_state.get("logged_in", False):
                            qty = st.number_input(
                                "Qty", min_value=1,
                                max_value=product["stock"],
                                value=product["min_order"],
                                step=1,
                                key=f"qty_{product['sku']}",
                                label_visibility="collapsed"
                            )
                            if st.button("🛒 Tambah", key=f"add_{product['sku']}",
                                         use_container_width=True):
                                add_to_cart(
                                    product["sku"],
                                    product["name"],
                                    product["price_reseller"],
                                    qty
                                )
                                st.toast(f"✅ {product['name'][:40]}... ditambahkan!",
                                         icon="🛒")
                                st.rerun()
                        else:
                            st.caption("🔑 Login untuk memesan")


# ── Cart Page ────────────────────────────────────────────────
def page_cart():
    """Shopping cart page."""
    st.markdown("## 🛒 Keranjang Belanja")

    init_cart()

    if not st.session_state.cart:
        st.markdown("""
        <div class="empty-state">
            <h3>🛒 Keranjang kosong</h3>
            <p>Tambahkan produk dari katalog</p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("🔙 Kembali ke Katalog", use_container_width=True):
            st.session_state.nav = "Katalog"
            st.rerun()
        return

    # Cart items
    total = 0
    for item in st.session_state.cart:
        subtotal = item["price"] * item["qty"]
        total += subtotal

        with st.container():
            st.markdown('<div class="checkout-card">', unsafe_allow_html=True)
            col1, col2, col3, col4, col5 = st.columns(
                [3, 1.5, 1.5, 1, 0.5]
            )

            with col1:
                st.markdown(f"**{item['name'][:50]}**")
                st.caption(f"SKU: `{item['sku']}`")

            with col2:
                st.markdown(f"{format_rupiah(item['price'])}")

            with col3:
                new_qty = st.number_input(
                    "Qty", min_value=1, max_value=999,
                    value=item["qty"], step=1,
                    key=f"cart_qty_{item['sku']}",
                    label_visibility="collapsed"
                )
                if new_qty != item["qty"]:
                    update_cart_qty(item["sku"], new_qty)
                    st.rerun()

            with col4:
                st.markdown(f"**{format_rupiah(subtotal)}**")

            with col5:
                if st.button("🗑️", key=f"del_{item['sku']}"):
                    remove_from_cart(item["sku"])
                    st.rerun()

            st.markdown('</div>', unsafe_allow_html=True)

    # Cart summary
    st.markdown("---")
    col1, col2, col3 = st.columns([2, 1, 1])
    with col1:
        if st.button("🗑️ Kosongkan Keranjang", use_container_width=True):
            clear_cart()
            st.rerun()
    with col2:
        st.markdown(f"### Total: {format_rupiah(total)}")
        total_items = sum(item["qty"] for item in st.session_state.cart)
        st.caption(f"{total_items} item(s)")
    with col3:
        if st.button("✅ Checkout", use_container_width=True, type="primary"):
            st.session_state.nav = "Checkout"
            st.rerun()


# ── Checkout Page ────────────────────────────────────────────
def page_checkout():
    """Checkout page."""
    st.markdown("## 📝 Checkout")

    init_cart()

    if not st.session_state.cart:
        st.warning("Keranjang kosong! Silakan tambahkan produk terlebih dahulu.")
        if st.button("🔙 Kembali ke Katalog"):
            st.session_state.nav = "Katalog"
            st.rerun()
        return

    # Order summary
    st.markdown("### 📋 Ringkasan Pesanan")
    total = 0
    total_qty = 0
    for item in st.session_state.cart:
        subtotal = item["price"] * item["qty"]
        total += subtotal
        total_qty += item["qty"]
        st.markdown(
            f"- **{item['name'][:50]}** ×{item['qty']} — "
            f"{format_rupiah(subtotal)}"
            f"  `{item['sku']}`"
        )

    st.markdown(f"**Total ({total_qty} item): {format_rupiah(total)}**")

    st.markdown("---")
    st.markdown("### 📍 Informasi Pemesan")

    col1, col2 = st.columns(2)
    with col1:
        nama = st.text_input("Nama Lengkap *", key="co_name")
        whatsapp = st.text_input("WhatsApp *", key="co_wa",
                                 placeholder="0812-3456-7890")
    with col2:
        email = st.text_input("Email", key="co_email")
        kota = st.text_input("Kota / Kabupaten *", key="co_city")

    alamat = st.text_area("Alamat Lengkap *", key="co_addr",
                          placeholder="Jl. ...")

    st.markdown("---")
    st.markdown("### 🚚 Metode Pengiriman")
    shipping = st.selectbox(
        "Pilih Ekspedisi",
        ["JNE Reguler", "J&T Express", "SiCepat REG",
         "Pos Indonesia", "AnterAja", "GoSend (Same Day)"],
        key="co_shipping"
    )

    notes = st.text_area("Catatan Pesanan (opsional)", key="co_notes",
                         placeholder="Warna, ukuran, atau permintaan khusus...")

    st.markdown("---")
    col1, col2, col3 = st.columns([1, 1, 1])
    with col1:
        if st.button("🔙 Kembali", use_container_width=True):
            st.session_state.nav = "Keranjang"
            st.rerun()
    with col3:
        if st.button("📤 Kirim Pesanan", use_container_width=True,
                     type="primary"):
            if not nama or not whatsapp or not kota or not alamat:
                st.error("❌ Mohon isi semua field yang bertanda *")
            else:
                # Calculate commission for marketing upline
                commission_msg = ""
                if logged_in and st.session_state.role == "reseller":
                    uid = st.session_state.get("username", "")
                    all_resellers = get_all_resellers()
                    if uid in all_resellers:
                        upline_id = all_resellers[uid].get("upline_id", "")
                        if upline_id and upline_id in all_resellers:
                            marketing = all_resellers[upline_id]
                            add_commission(
                                marketing_id=upline_id,
                                marketing_name=marketing.get("nama", "Marketing"),
                                reseller_id=uid,
                                reseller_name=st.session_state.get("user", ""),
                                order_amount=total,
                                commission_rate=marketing.get("commission_rate", 5),
                            )
                            commission_msg = f"\n\n💰 Komisi {marketing.get('commission_rate', 5)}% untuk Marketing **{marketing.get('nama', '')}**"

                st.success("✅ Pesanan berhasil dikirim!")
                st.balloons()
                st.markdown(f"""
                ### 🎉 Terima kasih, {nama}!

                Pesanan Anda sedang diproses. Tim kami akan menghubungi
                melalui WhatsApp di **{whatsapp}** untuk konfirmasi.

                **Total Pembayaran:** {format_rupiah(total)}
                **Pengiriman:** {shipping}{commission_msg}
                """)
                clear_cart()


# ── Marketing Dashboard ─────────────────────────────────────
def page_marketing():
    """Marketing dashboard: referral code, downline, commissions."""
    st.markdown("## 📊 Dashboard Marketing")

    marketing_id = st.session_state.get("username", "")

    # Referral Code
    all_resellers = get_all_resellers()
    my_data = all_resellers.get(marketing_id, {})
    referral_code = my_data.get("referral_code", "-")
    commission_rate = my_data.get("commission_rate", 5)

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("🔗 Kode Referral", referral_code)
    with col2:
        total_com = get_total_commission(marketing_id)
        st.metric("💰 Total Komisi", format_rupiah(total_com))
    with col3:
        pending_com = get_pending_commission(marketing_id)
        st.metric("⏳ Komisi Pending", format_rupiah(pending_com))

    st.markdown(f"""
    <div class="info-box">
        📢 Bagikan kode referral <code>{referral_code}</code> ke reseller Anda!
        <br>Anda mendapatkan <b>{commission_rate}%</b> komisi dari setiap pembelian reseller.
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")

    # Tabs: Downline & Commissions
    tab1, tab2 = st.tabs(["👥 Downline Reseller", "💵 Riwayat Komisi"])

    with tab1:
        downline = get_downline_list(marketing_id)
        if not downline:
            st.info("Belum ada reseller yang mendaftar dengan kode Anda.")
            st.markdown("""
            **Cara mendapatkan downline:**
            1. Bagikan kode referral Anda ke calon reseller
            2. Reseller memasukkan kode referral saat mendaftar
            3. Setiap pembelian reseller = komisi untuk Anda!
            """)
        else:
            st.markdown(f"**Total Downline: {len(downline)} reseller**")
            for dl in downline:
                st.markdown(f"""
                <div style="background:white;padding:12px;border-radius:8px;
                margin:8px 0;border:1px solid #E0E0E0;">
                    <b>{dl['nama']}</b> &nbsp;
                    <span style="color:#9E9E9E;font-size:0.8rem;">
                    {dl.get('email', dl.get('phone', '-'))}
                    </span><br>
                    <span style="font-size:0.75rem;color:#757575;">
                    Daftar: {dl.get('created_at', '-')[:10]}
                    {' ✅ Verified' if dl.get('is_verified') else ' ⚠️ Unverified'}
                    </span>
                </div>
                """, unsafe_allow_html=True)

    with tab2:
        commissions = get_commissions_for_marketing(marketing_id)
        if not commissions:
            st.info("Belum ada komisi. Komisi akan muncul saat reseller Anda melakukan pembelian.")
        else:
            for c in commissions:
                status_color = "#4CAF50" if c.get("status") == "paid" else "#FF9800"
                st.markdown(f"""
                <div style="background:white;padding:12px;border-radius:8px;
                margin:8px 0;border:1px solid #E0E0E0;">
                    <div style="display:flex;justify-content:space-between;">
                        <b>{c['reseller_name']}</b>
                        <span style="color:{status_color};font-size:0.8rem;font-weight:600;">
                        {c.get('status', 'pending').upper()}
                        </span>
                    </div>
                    <span style="font-size:0.8rem;color:#757575;">
                    Order: {format_rupiah(c['order_amount'])} →
                    Komisi {c['commission_rate']}%: <b style="color:#E53935;">{format_rupiah(c['commission_amount'])}</b>
                    </span><br>
                    <span style="font-size:0.7rem;color:#9E9E9E;">
                    {c.get('created_at', '-')[:16]}
                    </span>
                </div>
                """, unsafe_allow_html=True)


# ── About Page ───────────────────────────────────────────────
def page_about():
    """About / Help page."""
    st.markdown("## 📖 Panduan & Tentang")

    tab1, tab2, tab3 = st.tabs(
        ["📘 Cara Transaksi", "❓ FAQ", "ℹ️ Tentang"]
    )

    with tab1:
        st.markdown("""
        ### 📘 Cara Bertransaksi

        1. **Pilih Produk** — Browse katalog dan klik produk yang diinginkan
        2. **Tambah ke Keranjang** — Atur quantity lalu klik "Tambah"
        3. **Checkout** — Buka keranjang dan klik "Checkout"
        4. **Isi Data** — Lengkapi informasi pemesan dan alamat
        5. **Kirim Pesanan** — Tim kami akan konfirmasi via WhatsApp

        > 💡 **Tips:** Cek stok terlebih dahulu dan perhatikan minimum order!
        """)

    with tab2:
        st.markdown("""
        ### ❓ FAQ

        **Q: Berapa minimal pembelian?**
        Setiap produk memiliki minimum order berbeda (1-6 pcs).

        **Q: Apakah bisa retur?**
        Produk dengan label "Bisa Retur" dapat diretur dalam 7 hari.

        **Q: Berapa margin keuntungan?**
        Margin berkisar 40-75% dari harga retail.

        **Q: Bagaimana cara cek stok?**
        Gunakan filter "Tersedia (Cek Stok)" untuk lihat produk ready.
        """)

    with tab3:
        st.markdown("""
        ### ℹ️ Tentang Katalog Reseller

        **Versi:** 1.0.0
        **Platform:** Streamlit PWA

        Aplikasi katalog produk dengan SKU untuk memudahkan reseller
        dalam mencari, memilih, dan memesan produk.

        **Fitur:**
        - 🔍 Pencarian berdasarkan nama, SKU, brand
        - 📂 Filter kategori, brand, subkategori
        - 🛒 Keranjang belanja & checkout
        - 📱 Mobile-friendly & PWA (bisa diinstall)
        - 💰 Kalkulasi margin otomatis
        - 📦 Cek stok real-time

        ---
        © 2024 Katalog Reseller. All rights reserved.
        """)


# ── Exchange Rate Fetcher ──────────────────────────────────
@st.cache_data(ttl=3600)
def get_usd_idr_data() -> dict:
    """Fetch USD/IDR rate + 7-day history from free API."""
    try:
        import requests
        resp = requests.get(
            "https://api.exchangerate-api.com/v4/latest/USD",
            timeout=5
        )
        data = resp.json()
        rate = data["rates"]["IDR"]

        # Try to get 7-day history from frankfurter API
        try:
            hist = requests.get(
                "https://api.frankfurter.app/2026-06-07..2026-06-14?from=USD&to=IDR",
                timeout=5
            )
            hist_data = hist.json()
            rates = hist_data.get("rates", {})
            history = []
            for date, vals in sorted(rates.items()):
                history.append(vals.get("IDR", rate))
            if not history:
                history = [rate - 500, rate - 300, rate - 200, rate - 100, rate - 50, rate - 20, rate]
        except Exception:
            # Simulate history if API fails
            import random
            history = [rate - random.randint(50, 500) for _ in range(6)] + [rate]

        prev = history[-2] if len(history) > 1 else rate
        change = rate - prev
        change_pct = (change / prev) * 100

        return {
            "rate": rate,
            "change": change,
            "change_pct": change_pct,
            "history": history,
        }
    except Exception:
        return {
            "rate": 16300.0,
            "change": 0,
            "change_pct": 0,
            "history": [16250, 16280, 16300, 16290, 16310, 16300, 16300],
        }


# ── Main App ─────────────────────────────────────────────────
def main():
    """Main application entry point."""
    # Inject PWA & CSS
    inject_pwa()
    inject_css()
    inject_whatsapp_float()

    # Check login status (does NOT block - guests can browse)
    logged_in = check_login()

    # Always initialize cart & products for browsing
    init_cart()
    ensure_products_in_state()
    init_chat()
    if "nav" not in st.session_state:
        st.session_state.nav = "Katalog"
    if "selected_category" not in st.session_state:
        st.session_state.selected_category = "Semua Kategori"
    if "filter_category" not in st.session_state:
        st.session_state.filter_category = "Semua Kategori"
    if "filter_brand" not in st.session_state:
        st.session_state.filter_brand = "Semua Brand"
    if "filter_subcat" not in st.session_state:
        st.session_state.filter_subcat = "Semua Subkategori"
    if "filter_available" not in st.session_state:
        st.session_state.filter_available = False
    if "filter_return" not in st.session_state:
        st.session_state.filter_return = False
    if "sort_by" not in st.session_state:
        st.session_state.sort_by = "Default"
    if "search_input" not in st.session_state:
        st.session_state.search_input = ""

    # ── Top Navigation Bar (functional) ──
    cart_count = get_cart_count()
    chat_unread = get_unread_count(st.session_state.get("username", ""), st.session_state.get("role", "reseller")) if logged_in else 0
    is_admin = logged_in and st.session_state.role == "admin"
    is_marketing = logged_in and st.session_state.role == "marketing"
    chat_badge = f' ({chat_unread})' if chat_unread > 0 else ""

    # Init active tab
    if "active_tab" not in st.session_state:
        st.session_state.active_tab = 0
    if "selected_product_sku" not in st.session_state:
        st.session_state.selected_product_sku = None

    # ═══ Exchange Rate Bar (above red navbar) ═══
    fx = get_usd_idr_data()
    rate = fx["rate"]
    change = fx["change"]
    change_pct = fx["change_pct"]
    history = fx["history"]

    is_up = change >= 0
    arrow = "▲" if is_up else "▼"
    color = "#2E7D32" if is_up else "#C62828"
    sign = "+" if is_up else ""

    # Sparkline as base64 img (SVG polyline stripped by Streamlit)
    if history and len(history) > 1:
        import base64
        min_h, max_h = min(history), max(history)
        rng = max_h - min_h or 1
        points = []
        for i, h in enumerate(history):
            x = (i / (len(history) - 1)) * 100
            y = 40 - ((h - min_h) / rng) * 30
            points.append(f"{x:.1f},{y:.1f}")
        polyline = " ".join(points)
        sparkline_color = "#2E7D32" if is_up else "#C62828"

        svg_raw = f'<svg xmlns="http://www.w3.org/2000/svg" width="120" height="40">' \
                  f'<polyline points="{polyline}" fill="none" stroke="{sparkline_color}" ' \
                  f'stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>' \
                  f'</svg>'
        b64 = base64.b64encode(svg_raw.encode()).decode()
        sparkline_img = f'<img src="data:image/svg+xml;base64,{b64}" ' \
                        f'style="width:120px;height:40px;vertical-align:middle;" alt="sparkline">'
    else:
        sparkline_img = ""

    st.markdown(f"""
    <div style="
        background: #FFFFFF;
        margin: -48px -4rem 0 -4rem;
        padding: 8px 4rem 6px 4rem;
        border-bottom: 1px solid #E0E0E0;
        display: flex;
        align-items: center;
        gap: 12px;
        font-size: 0.8rem;
        position: relative;
        z-index: 10;
    ">
        <span style="font-weight:700;color:#212121;font-size:0.85rem;">
            💱 USD/IDR
        </span>
        <span style="font-weight:700;color:#212121;font-size:1rem;">
            Rp {rate:,.0f}
        </span>
        <span style="color:{color};font-weight:600;">
            {arrow} {sign}{change_pct:+.2f}%
        </span>
        <span style="color:#757575;font-size:0.75rem;">
            ({sign}Rp {change:,.0f}) Hari ini
        </span>
        <span style="flex:1;"></span>
        {sparkline_img}
        <span style="color:#9E9E9E;font-size:0.7rem;">
            📅 14 Jun 2026
        </span>
    </div>
    """, unsafe_allow_html=True)

    # ── Navbar Red Background Wrapper ──
    st.markdown("""
    <div class="navbar-wrapper" style="
        background: linear-gradient(135deg, #E53935, #C62828);
        margin: 0 -4rem 1rem -4rem;
        padding: 10px 4rem 8px 4rem;
        box-shadow: 0 2px 12px rgba(0,0,0,0.15);
        position: relative;
    ">
    """, unsafe_allow_html=True)

    # Navbar brand + user
    brand_col, _, user_col = st.columns([2, 1, 2])

    with brand_col:
        st.markdown("""
        <div style="font-size:1.3rem;font-weight:700;color:#212121;">
        📦 KATALOG RESELLER
        </div>
        """, unsafe_allow_html=True)

    with user_col:
        if logged_in:
            st.markdown(f"""
            <div style="text-align:right;color:#212121;font-size:0.85rem;font-weight:500;padding-top:4px;">
            👋 {st.session_state.user}
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div style="text-align:right;color:#424242;font-size:0.85rem;padding-top:4px;">
            👤 Tamu
            </div>
            """, unsafe_allow_html=True)

    # Navbar buttons
    if logged_in:
        if is_marketing:
            nav_items = [
                ("🏠 Beranda", 0),
                ("📊 Marketing", 1),
                ("💬 Chat", 2),
                ("📖 Panduan", 3),
            ]
        else:
            nav_items = [
                ("🏠 Beranda", 0),
                (f"🛒 Keranjang ({cart_count})", 1),
                ("📝 Checkout", 2),
                (f"💬 Chat{chat_badge}", 3),
                ("📖 Panduan", 4),
            ]
        if is_admin:
            nav_items.append(("⚙️ Admin", len(nav_items)))
    else:
        nav_items = [
            ("🏠 Beranda", 0),
            ("🔑 Masuk / Daftar", 1),
            ("📖 Panduan", 2),
        ]

    nav_cols = st.columns(len(nav_items))
    for i, (label, tab_idx) in enumerate(nav_items):
        with nav_cols[i]:
            is_active = st.session_state.active_tab == tab_idx
            btn_type = "primary" if is_active else "secondary"
            if st.button(label, key=f"nav_{tab_idx}", use_container_width=True,
                         type=btn_type):
                st.session_state.active_tab = tab_idx
                st.rerun()

    # Close red wrapper
    st.markdown("</div>", unsafe_allow_html=True)

    # Logout button
    if logged_in:
        st.markdown('<div style="height:4px;"></div>', unsafe_allow_html=True)
        _, _, col3 = st.columns([6, 1, 1])
        with col3:
            if st.button("🚪 Logout", key="logout_btn_nav", use_container_width=True):
                logout()

    # ── Page Routing based on active_tab ──
    active = st.session_state.active_tab

    if logged_in:
        if is_marketing:
            # Marketing: 0=Katalog, 1=Marketing, 2=Chat, 3=Panduan
            if active == 0:
                page_catalog()
            elif active == 1:
                page_marketing()
            elif active == 2:
                page_chat()
            elif active == 3:
                page_about()
            elif is_admin and active == 4:
                page_admin()
        else:
            # Reseller/Admin: 0=Katalog, 1=Cart, 2=Checkout, 3=Chat, 4=Panduan
            if active == 0:
                page_catalog()
            elif active == 1:
                page_cart()
            elif active == 2:
                page_checkout()
            elif active == 3:
                page_chat()
            elif active == 4:
                page_about()
            elif is_admin and active == 5:
                page_admin()
    else:
        # Guest: 0=Katalog, 1=Login, 2=Panduan
        if active == 0:
            page_catalog()
        elif active == 1:
            show_auth_page()
        elif active == 2:
            page_about()

    # Footer
    st.markdown("---")
    st.markdown(
        "<div style='text-align:center;color:#BDBDBD;font-size:0.8rem;'>"
        "Katalog Reseller v1.0 · PWA · © 2024<br>"
        "Streamlit Cloud Ready · Mobile & Desktop"
        "</div>",
        unsafe_allow_html=True
    )


if __name__ == "__main__":
    main()

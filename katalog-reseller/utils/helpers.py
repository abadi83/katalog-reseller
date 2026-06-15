"""Helper functions for Katalog Reseller."""

import streamlit as st
from utils.admin import get_products, get_categories, get_subcategories, get_brands_from_products
from utils.formatting import format_rupiah


def search_products(query: str) -> list:
    """Search products by name, SKU, brand, or category."""
    products = get_products()
    q = query.lower().strip()
    if not q:
        return products
    results = []
    for p in products:
        if (q in p["name"].lower()
                or q in p["sku"].lower()
                or q in p["brand"].lower()
                or q in p["category"].lower()
                or q in p["subcategory"].lower()):
            results.append(p)
    return results


def filter_products(category: str = None, brand: str = None,
                    subcategory: str = None, available_only: bool = False,
                    can_return_only: bool = False) -> list:
    """Filter products by various criteria."""
    results = get_products()
    if category and category != "Semua Kategori":
        results = [p for p in results if p["category"] == category]
    if brand and brand != "Semua Brand":
        results = [p for p in results if p["brand"] == brand]
    if subcategory and subcategory != "Semua Subkategori":
        results = [p for p in results if p["subcategory"] == subcategory]
    if available_only:
        results = [p for p in results if p["available"] and p["stock"] > 0]
    if can_return_only:
        results = [p for p in results if p["can_return"]]
    return results


def show_product_card(product: dict):
    """Render a product card with SKU and 1:1 image."""
    margin = product["price_retail"] - product["price_reseller"]
    margin_pct = round((margin / product["price_retail"]) * 100)

    # Get first image
    images = product.get("images", [])
    if not images and product.get("image"):
        images = [product["image"]]
    first_img = images[0] if images else "https://placehold.co/400x400/E53935/FFF?text=NO+FOTO"

    # Image count badge
    img_count_badge = ""
    if len(images) > 1:
        img_count_badge = f'<div style="position:absolute;bottom:8px;right:8px;background:rgba(0,0,0,0.6);color:white;padding:2px 6px;border-radius:4px;font-size:0.65rem;">📷{len(images)}</div>'

    st.markdown(f"""
    <div style="
        background: white;
        border-radius: 12px;
        overflow: hidden;
        box-shadow: 0 2px 8px rgba(0,0,0,0.08);
        transition: transform 0.2s, box-shadow 0.2s;
        height: 100%;
        cursor: pointer;
    " onmouseover="this.style.transform='translateY(-4px)';this.style.boxShadow='0 4px 16px rgba(0,0,0,0.15)';"
       onmouseout="this.style.transform='translateY(0)';this.style.boxShadow='0 2px 8px rgba(0,0,0,0.08)';">
        <div style="position: relative; aspect-ratio: 1; overflow: hidden;">
            <img src="{first_img}" style="width: 100%; height: 100%; object-fit: cover;" alt="{product['name']}">
            {img_count_badge}
            {f'<div style="position:absolute;top:8px;right:8px;background:#E53935;color:white;padding:4px 8px;border-radius:6px;font-size:0.7rem;font-weight:600;">SALE</div>' if product['category'] == 'SALE' else ''}
            {f'<div style="position:absolute;top:8px;left:8px;background:#4CAF50;color:white;padding:4px 8px;border-radius:6px;font-size:0.7rem;">Bisa Retur</div>' if product['can_return'] else ''}
        </div>
        <div style="padding: 12px;">
            <div style="font-size:0.7rem;color:#E53935;font-weight:600;margin-bottom:4px;">{product['sku']}</div>
            <div style="font-size:0.85rem;font-weight:600;color:#212121;line-height:1.3;margin-bottom:8px;min-height:2.6em;">{product['name'][:60]}</div>
            <div style="font-size:0.7rem;color:#9E9E9E;margin-bottom:6px;">{product['brand']} · Stok: {product['stock']}</div>
            <div style="display:flex;align-items:center;gap:6px;margin-bottom:6px;">
                <span style="font-size:1rem;font-weight:700;color:#E53935;">{format_rupiah(product['price_reseller'])}</span>
                <span style="font-size:0.75rem;color:#9E9E9E;text-decoration:line-through;">{format_rupiah(product['price_retail'])}</span>
            </div>
            <div style="display:flex;align-items:center;gap:4px;margin-bottom:4px;">
                <span style="font-size:0.7rem;background:#E8F5E9;color:#2E7D32;padding:2px 6px;border-radius:4px;">💰 Margin {margin_pct}%</span>
                <span style="font-size:0.7rem;color:#757575;">({format_rupiah(margin)})</span>
            </div>
                <div style="font-size:0.7rem;color:#757575;">Min. Order: {product['min_order']} pcs</div>
        </div>
    </div>
    """, unsafe_allow_html=True)


def show_product_detail(product: dict):
    """Show detailed product view with image gallery."""
    margin = product["price_retail"] - product["price_reseller"]
    margin_pct = round((margin / product["price_retail"]) * 100)

    # Get images list
    images = product.get("images", [])
    if not images and product.get("image"):
        images = [product["image"]]
    if not images:
        images = ["https://placehold.co/400x400/E53935/FFF?text=NO+FOTO"]

    col1, col2 = st.columns([1, 1])

    with col1:
        # Image gallery with navigation dots
        if len(images) > 1:
            img_idx = st.radio(
                "Foto", range(len(images)),
                format_func=lambda i: f"Foto {i+1}",
                horizontal=True,
                key=f"img_idx_{product['sku']}",
                label_visibility="collapsed"
            )
        else:
            img_idx = 0

        # Display current image with 1:1 aspect ratio
        st.markdown(f"""
        <div style="aspect-ratio:1; overflow:hidden; border-radius:12px; background:#F5F5F5;">
            <img src="{images[img_idx]}"
                 style="width:100%; height:100%; object-fit:cover;"
                 alt="{product['name']}">
        </div>
        """, unsafe_allow_html=True)

        # Thumbnail strip
        if len(images) > 1:
            thumb_cols = st.columns(len(images))
            for i, img in enumerate(images):
                with thumb_cols[i]:
                    border = "3px solid #E53935" if i == img_idx else "3px solid transparent"
                    st.markdown(f"""
                    <div style="aspect-ratio:1; border-radius:8px; overflow:hidden;
                                border:{border}; cursor:pointer; opacity:{1 if i == img_idx else 0.6};">
                        <img src="{img}" style="width:100%; height:100%; object-fit:cover;">
                    </div>
                    """, unsafe_allow_html=True)

    with col2:
        st.markdown(f"### {product['name']}")
        st.markdown(f"**SKU:** `{product['sku']}`")
        st.markdown(f"**Brand:** {product['brand']}")
        st.markdown(f"**Kategori:** {product['category']} > {product['subcategory']}")

        st.markdown("---")
        st.markdown(f"#### 💰 Harga Reseller: **{format_rupiah(product['price_reseller'])}**")
        st.markdown(f"Harga Retail: ~~{format_rupiah(product['price_retail'])}~~")
        st.markdown(f"💰 Margin: **{format_rupiah(margin)}** ({margin_pct}%)")

        st.markdown(f"📦 Stok: **{product['stock']}** pcs | Min. Order: **{product['min_order']}** pcs")
        st.markdown(f"⚖️ Berat: {product.get('weight', '-')}")

        if product.get("colors"):
            colors = ", ".join(product["colors"])
            st.markdown(f"🎨 Warna: {colors}")

        if product.get("sizes"):
            sizes = ", ".join(product["sizes"])
            st.markdown(f"📏 Ukuran: {sizes}")

        st.markdown(f"✅ Bisa Retur: {'Ya' if product.get('can_return') else 'Tidak'}")
        st.caption(f"📷 {len(images)} foto")

    st.markdown("---")
    st.markdown(f"**Deskripsi:** {product.get('description', '-')}")


def show_cart_sidebar():
    """Show cart summary in sidebar."""
    from utils.cart import get_cart_count, get_cart_total

    count = get_cart_count()
    total = get_cart_total()

    st.markdown(f"""
    <div style="
        background: linear-gradient(135deg, #E53935, #C62828);
        color: white;
        padding: 12px 16px;
        border-radius: 12px;
        margin-bottom: 16px;
    ">
        <div style="font-size:0.85rem;">🛒 Keranjang Belanja</div>
        <div style="font-size:1.5rem;font-weight:700;">{count} item(s)</div>
        <div style="font-size:1.1rem;">{format_rupiah(total)}</div>
    </div>
    """, unsafe_allow_html=True)

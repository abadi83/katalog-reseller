"""Admin panel utilities for Katalog Reseller.
Provides product CRUD and category management for admin users.
"""

import streamlit as st
from data.products import PRODUCTS as DEFAULT_PRODUCTS, pil_to_base64
from PIL import Image
from io import BytesIO
import copy
import base64


def save_uploaded_images(uploaded_files) -> list:
    """Convert uploaded files to base64 data URLs (max 4), cropped to 1:1 ratio."""
    if not uploaded_files:
        return []
    images = []
    for i, file in enumerate(uploaded_files):
        if i >= 4:
            break
        try:
            img = Image.open(file).convert("RGB")
            w, h = img.size
            side = min(w, h)
            left = (w - side) // 2
            top = (h - side) // 2
            img = img.crop((left, top, left + side, top + side))
            img = img.resize((600, 600), Image.LANCZOS)
            data_url = pil_to_base64(img, "JPEG")
            images.append(data_url)
        except Exception as e:
            st.warning(f"Gagal memproses gambar {file.name}: {e}")
    return images


def save_3d_model(uploaded_file) -> str | None:
    """Convert uploaded 3D model (.glb/.gltf) to base64 data URL.
    Returns None if no file or error."""
    if uploaded_file is None:
        return None
    try:
        file_bytes = uploaded_file.read()
        if len(file_bytes) > 20 * 1024 * 1024:  # Max 20MB
            st.error("❌ File 3D terlalu besar! Maksimal 20MB.")
            return None
        b64 = base64.b64encode(file_bytes).decode()
        # Determine mime type
        name = uploaded_file.name.lower()
        if name.endswith('.glb'):
            mime = "model/gltf-binary"
        elif name.endswith('.gltf'):
            mime = "model/gltf+json"
        else:
            st.error("❌ Format tidak didukung. Gunakan .glb atau .gltf")
            return None
        return f"data:{mime};base64,{b64}"
    except Exception as e:
        st.error(f"❌ Gagal memproses file 3D: {e}")
        return None


def _init_image_slots(prefix: str, existing_images: list = None):
    """Initialize the images list in session state."""
    key = f"{prefix}_images"
    if key not in st.session_state:
        st.session_state[key] = existing_images.copy() if existing_images else []


def _collect_slot_images(prefix: str) -> list:
    """Get the list of uploaded images."""
    key = f"{prefix}_images"
    return st.session_state.get(key, [])


def _render_image_slot_grid(prefix: str, existing_images: list = None):
    """Render 4 small square image upload boxes in a 4-column grid."""
    _init_image_slots(prefix, existing_images)
    images_key = f"{prefix}_images"
    images = st.session_state[images_key]

    st.markdown("### 🖼️ Foto Produk (Maks. 4, Rasio 1:1)")
    st.caption("Upload via tombol di bawah, klik ✕ pada kotak untuk menghapus")

    # ── 4-box grid ──
    cols = st.columns(4)
    for i in range(4):
        with cols[i]:
            if i < len(images):
                # Filled slot — show image + delete button
                st.markdown(f"""
                <div style="aspect-ratio:1; border-radius:10px; overflow:hidden;
                            border:2px solid #E0E0E0; background:#F5F5F5;">
                    <img src="{images[i]}"
                         style="width:100%; height:100%; object-fit:cover;">
                </div>
                """, unsafe_allow_html=True)
                if st.button("✕ Hapus", key=f"{prefix}_del_{i}",
                             use_container_width=True):
                    st.session_state[images_key].pop(i)
                    st.rerun()
            else:
                # Empty slot — dashed placeholder
                st.markdown(f"""
                <div style="aspect-ratio:1; border-radius:10px;
                            border:2px dashed #BDBDBD; background:#FAFAFA;
                            display:flex; align-items:center; justify-content:center;">
                    <span style="font-size:2rem; color:#BDBDBD;">＋</span>
                </div>
                """, unsafe_allow_html=True)

    # ── Upload button (below the grid) ──
    remaining = 4 - len(images)
    if remaining > 0:
        new_files = st.file_uploader(
            f"📤 Upload foto ({remaining} slot tersisa) — JPG/PNG/WebP",
            type=["jpg", "jpeg", "png", "webp"],
            accept_multiple_files=True,
            key=f"{prefix}_uploader",
        )
        if new_files:
            for file in new_files:
                if len(st.session_state[images_key]) >= 4:
                    break
                try:
                    img = Image.open(file).convert("RGB")
                    w, h = img.size
                    side = min(w, h)
                    left = (w - side) // 2
                    top = (h - side) // 2
                    img = img.crop((left, top, left + side, top + side))
                    img = img.resize((400, 400), Image.LANCZOS)
                    data_url = pil_to_base64(img, "JPEG")
                    st.session_state[images_key].append(data_url)
                except Exception:
                    st.error(f"Gagal upload {file.name}")
            st.rerun()
    else:
        st.info("✅ 4 foto sudah terisi. Hapus salah satu untuk mengganti.")


def get_image_preview(product: dict) -> str:
    """Get first image URL or placeholder for a product."""
    images = product.get("images", [])
    if images:
        return images[0]
    if product.get("image"):
        return product["image"]
    return "https://placehold.co/400x400/E53935/FFF?text=NO+FOTO"


def ensure_products_in_state():
    """Initialize products in session_state from defaults if not present."""
    if "products" not in st.session_state:
        st.session_state.products = copy.deepcopy(DEFAULT_PRODUCTS)
    if "categories" not in st.session_state:
        cats = sorted(set(p["category"] for p in DEFAULT_PRODUCTS))
        st.session_state.categories = cats
    if "subcategories" not in st.session_state:
        subs = sorted(set(p["subcategory"] for p in DEFAULT_PRODUCTS))
        st.session_state.subcategories = subs


def get_products():
    """Get products from session state (mutable)."""
    ensure_products_in_state()
    return st.session_state.products


def get_categories():
    """Get categories from session state."""
    ensure_products_in_state()
    return st.session_state.categories


def get_subcategories():
    """Get subcategories from session state."""
    ensure_products_in_state()
    return st.session_state.subcategories


def get_brands_from_products():
    """Extract unique brands from current products."""
    return sorted(set(p["brand"] for p in get_products()))


def generate_sku(category: str, brand: str, subcategory: str) -> str:
    """Generate a SKU from category code + brand code + sequential number."""
    cat_code = "".join(w[0] for w in category.split()).upper()[:3]
    brand_code = brand[:3].upper()
    sub_code = subcategory[:3].upper()

    existing = [
        p["sku"] for p in get_products()
        if p["sku"].startswith(f"{cat_code}-{brand_code}")
    ]
    num = len(existing) + 1
    return f"{cat_code}-{brand_code}-{num:03d}"


# ── Page: Admin Panel ────────────────────────────────────────
def page_admin():
    """Admin panel page with product & category management."""
    st.markdown("## ⚙️ Admin Panel")

    if st.session_state.role != "admin":
        st.error("⛔ Akses ditolak! Hanya admin yang dapat mengakses halaman ini.")
        return

    ensure_products_in_state()

    tab1, tab2, tab3, tab4 = st.tabs(
        ["➕ Tambah Produk", "✏️ Edit Produk", "📂 Kelola Kategori", "📦 Update Stok Massal"]
    )

    with tab1:
        _tab_add_product()

    with tab2:
        _tab_edit_product()

    with tab3:
        _tab_manage_categories()

    with tab4:
        _tab_bulk_stock()


# ── Tab: Add Product ─────────────────────────────────────────
def _tab_add_product():
    st.markdown("### ➕ Tambah Produk Baru")

    col1, col2 = st.columns(2)

    with col1:
        name = st.text_input("📛 Nama Produk *", key="add_name",
                             placeholder="Contoh: Tas Selempang Wanita XYZ 001")
        sku_manual = st.text_input("🔖 SKU (Opsional — kosongkan untuk auto)", 
                                    key="add_sku_manual",
                                    placeholder="Auto: FAS-BLA-001")
        category = st.selectbox("📂 Kategori *",
                                get_categories(), key="add_cat")
        subcategory = st.selectbox("📌 Subkategori *",
                                   get_subcategories(), key="add_sub")
        brand = st.text_input("🏷️ Brand *", key="add_brand",
                              placeholder="Contoh: Blackkelly")

    with col2:
        price_reseller = st.number_input("💰 Harga Reseller *",
                                         min_value=1000, value=50000,
                                         step=1000, key="add_price_reseller")
        price_retail = st.number_input("🏪 Harga Retail *",
                                       min_value=1000, value=100000,
                                       step=1000, key="add_price_retail")
        stock = st.number_input("📦 Stok *", min_value=0, value=10,
                                step=1, key="add_stock")
        min_order = st.number_input("📋 Min. Order", min_value=1, value=1,
                                    step=1, key="add_min_order")

    # Additional details
    st.markdown("---")
    col3, col4 = st.columns(2)
    with col3:
        weight = st.text_input("⚖️ Berat", value="200g", key="add_weight")
        colors = st.text_input("🎨 Warna (pisahkan dengan koma)",
                               value="Hitam, Putih", key="add_colors",
                               placeholder="Merah, Biru, Hijau")
    with col4:
        description = st.text_area("📝 Deskripsi", key="add_desc",
                                   placeholder="Deskripsi produk...",
                                   height=100)
        available = st.checkbox("✅ Produk Tersedia", value=True,
                                key="add_available")
        can_return = st.checkbox("↩️ Bisa Retur", value=True,
                                 key="add_return")

    # Image upload — 4 box grid
    st.markdown("---")
    _render_image_slot_grid("add")

    # ── 3D Model Upload ──
    st.markdown("---")
    st.markdown("### 🧊 Model 3D (Opsional)")
    st.caption("Upload file .glb atau .gltf — Pembeli bisa melihat produk dalam 3D!")
    model_3d_file = st.file_uploader(
        "📤 Upload Model 3D (.glb / .gltf)",
        type=["glb", "gltf"],
        key="add_model_3d",
        accept_multiple_files=False,
    )
    model_3d_data = save_3d_model(model_3d_file) if model_3d_file else None
    if model_3d_data:
        st.success("✅ Model 3D berhasil diupload! 🧊")

    # Auto-generated SKU preview (only if no manual SKU)
    if sku_manual.strip():
        preview_sku = sku_manual.strip().upper()
        st.info(f"🔖 SKU Manual: **`{preview_sku}`**")
    elif brand and category and subcategory:
        preview_sku = generate_sku(category, brand, subcategory)
        st.info(f"🔖 SKU Otomatis: **`{preview_sku}`**")
    else:
        preview_sku = None

    st.markdown("---")

    if st.button("✅ Simpan Produk", use_container_width=True, type="primary"):
        errors = []
        if not name:
            errors.append("Nama produk wajib diisi")
        if not brand:
            errors.append("Brand wajib diisi")
        if not preview_sku:
            errors.append("Kategori, Brand, dan Subkategori wajib dipilih (atau isi SKU manual)")
        if price_reseller >= price_retail:
            errors.append("Harga reseller harus lebih rendah dari harga retail")

        if errors:
            for e in errors:
                st.error(f"❌ {e}")
        else:
            # Use manual or auto SKU
            final_sku = preview_sku

            # Check SKU uniqueness
            existing_skus = [p["sku"] for p in get_products()]
            if final_sku in existing_skus:
                if sku_manual.strip():
                    st.error(f"❌ SKU `{final_sku}` sudah digunakan! Gunakan SKU lain.")
                    st.stop()
                else:
                    counter = 1
                    base = "-".join(final_sku.split("-")[:2])
                    while final_sku in existing_skus:
                        counter += 1
                        final_sku = f"{base}-{counter:03d}"
                final_sku = f"{sku.split('-')[0]}-{sku.split('-')[1]}-{counter:03d}"

            new_product = {
                "sku": final_sku,
                "name": name,
                "category": category,
                "subcategory": subcategory,
                "brand": brand,
                "price_reseller": price_reseller,
                "price_retail": price_retail,
                "stock": stock,
                "available": available,
                "can_return": can_return,
                "images": _collect_slot_images("add")
                          or ["https://placehold.co/400x400/E53935/FFF?text=NEW"],
                "model_3d": model_3d_data,
                "description": description,
                "weight": weight,
                "colors": [c.strip() for c in colors.split(",") if c.strip()],
                "min_order": min_order,
            }

            st.session_state.products.append(new_product)

            # Update categories/subcategories if new
            if category not in st.session_state.categories:
                st.session_state.categories.append(category)
                st.session_state.categories.sort()
            if subcategory not in st.session_state.subcategories:
                st.session_state.subcategories.append(subcategory)
                st.session_state.subcategories.sort()

            st.success(f"✅ Produk **{name}** berhasil ditambahkan!")
            st.balloons()
            st.rerun()


# ── Tab: Update Stok Massal ──────────────────────────────────
def _tab_bulk_stock():
    st.markdown("### 📦 Update Stok Massal per SKU")

    products = get_products()
    if not products:
        st.info("Belum ada produk.")
        return

    # Build dataframe for editing
    import pandas as pd
    df_data = []
    for p in products:
        df_data.append({
            "SKU": p["sku"],
            "Nama Produk": p["name"][:60],
            "Kategori": p["category"],
            "Stok Saat Ini": p["stock"],
            "Stok Baru": p["stock"],  # editable
        })

    df = pd.DataFrame(df_data)

    st.markdown("#### ✏️ Edit stok langsung di tabel (kolom **Stok Baru**)")

    edited_df = st.data_editor(
        df,
        column_config={
            "SKU": st.column_config.TextColumn("SKU", disabled=True),
            "Nama Produk": st.column_config.TextColumn("Nama Produk", disabled=True),
            "Kategori": st.column_config.TextColumn("Kategori", disabled=True),
            "Stok Saat Ini": st.column_config.NumberColumn("Stok Saat Ini", disabled=True),
            "Stok Baru": st.column_config.NumberColumn(
                "Stok Baru ✏️",
                min_value=0,
                step=1,
                help="Edit nilai stok di kolom ini, lalu klik Simpan Semua",
            ),
        },
        use_container_width=True,
        hide_index=True,
        num_rows="fixed",
        key="bulk_stock_editor",
    )

    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        if st.button("💾 Simpan Semua Stok", use_container_width=True, type="primary"):
            updated = 0
            for _, row in edited_df.iterrows():
                sku = row["SKU"]
                new_stock = int(row["Stok Baru"])
                # Find product and update
                for p in st.session_state.products:
                    if p["sku"] == sku:
                        if p["stock"] != new_stock:
                            p["stock"] = new_stock
                            updated += 1
                        break
            if updated > 0:
                st.success(f"✅ {updated} stok berhasil diperbarui!")
                st.rerun()
            else:
                st.info("Tidak ada perubahan stok.")

    # ── File Upload (CSV / Excel) ──
    st.markdown("---")
    st.markdown("#### 📤 Atau Upload File untuk Update Stok Massal")
    st.caption("Format: kolom **SKU** dan **Stok**. Bisa CSV (.csv) atau Excel (.xlsx)")

    uploaded_file = st.file_uploader(
        "Upload file CSV atau Excel",
        type=["csv", "xlsx"],
        key="bulk_file_upload",
        help="File harus memiliki kolom 'SKU' dan 'Stok'"
    )

    if uploaded_file:
        try:
            # Read based on file type
            if uploaded_file.name.endswith(".xlsx"):
                file_df = pd.read_excel(uploaded_file, engine="openpyxl")
            else:
                file_df = pd.read_csv(uploaded_file)

            # Auto-detect columns (case-insensitive)
            cols = {c.strip().upper(): c for c in file_df.columns}
            sku_col = cols.get("SKU", cols.get("KODE", cols.get("KODE SKU", None)))
            stok_col = cols.get("STOK", cols.get("STOCK", cols.get("QTY", cols.get("JUMLAH", None))))

            if not sku_col or not stok_col:
                st.error("❌ File harus memiliki kolom **SKU** dan **Stok**!")
                st.caption(f"Kolom ditemukan: {', '.join(file_df.columns)}")
            else:
                st.markdown(f"**Preview data ({uploaded_file.name}):**")
                preview_df = file_df[[sku_col, stok_col]].copy()
                preview_df.columns = ["SKU", "Stok"]
                st.dataframe(preview_df.head(20), use_container_width=True, hide_index=True)
                st.caption(f"Total: {len(preview_df)} baris")

                if st.button("📥 Terapkan dari File", use_container_width=True, type="primary"):
                    updated = 0
                    skipped = 0
                    not_found = []
                    for _, row in file_df.iterrows():
                        sku = str(row[sku_col]).strip()
                        try:
                            stok = int(float(row[stok_col]))
                        except (ValueError, TypeError):
                            skipped += 1
                            continue
                        found = False
                        for p in st.session_state.products:
                            if p["sku"].upper() == sku.upper():
                                p["stock"] = stok
                                updated += 1
                                found = True
                                break
                        if not found:
                            not_found.append(sku)
                    msg = f"✅ **{updated}** stok berhasil diperbarui!"
                    if skipped:
                        msg += f"\n⏭️ {skipped} baris dilewati (stok tidak valid)"
                    if not_found:
                        msg += f"\n⚠️ SKU tidak ditemukan di aplikasi: {', '.join(not_found[:10])}"
                    if updated > 0:
                        st.success(msg)
                        st.rerun()
                    else:
                        st.warning("Tidak ada stok yang diperbarui. Periksa SKU.")
        except Exception as e:
            st.error(f"❌ Gagal membaca file: {e}")


# ── Tab: Edit Product ────────────────────────────────────────
def _tab_edit_product():
    st.markdown("### ✏️ Edit / Hapus Produk")

    products = get_products()

    if not products:
        st.info("Belum ada produk.")
        return

    # Search & select product
    search_term = st.text_input("🔍 Cari produk untuk diedit",
                                placeholder="Nama atau SKU...",
                                key="edit_search")
    if search_term:
        filtered = [
            p for p in products
            if search_term.lower() in p["name"].lower()
            or search_term.lower() in p["sku"].lower()
        ]
    else:
        filtered = products

    # Select product
    product_options = {f"[{p['sku']}] {p['name'][:60]}": p for p in filtered}
    if not product_options:
        st.warning("Produk tidak ditemukan.")
        return

    selected_label = st.selectbox(
        "Pilih produk", list(product_options.keys()), key="edit_select"
    )
    product = product_options[selected_label]
    sku = product["sku"]

    st.markdown("---")

    col1, col2 = st.columns(2)

    with col1:
        new_name = st.text_input("📛 Nama Produk", value=product["name"],
                                 key="edit_name")
        new_category = st.selectbox(
            "📂 Kategori",
            get_categories(),
            index=get_categories().index(product["category"])
            if product["category"] in get_categories() else 0,
            key="edit_cat"
        )
        new_subcategory = st.selectbox(
            "📌 Subkategori",
            get_subcategories(),
            index=get_subcategories().index(product["subcategory"])
            if product["subcategory"] in get_subcategories() else 0,
            key="edit_sub"
        )
        new_brand = st.text_input("🏷️ Brand", value=product["brand"],
                                  key="edit_brand")

    with col2:
        new_price_reseller = st.number_input(
            "💰 Harga Reseller",
            min_value=1000, value=product["price_reseller"],
            step=1000, key="edit_price_reseller"
        )
        new_price_retail = st.number_input(
            "🏪 Harga Retail",
            min_value=1000, value=product["price_retail"],
            step=1000, key="edit_price_retail"
        )
        new_stock = st.number_input(
            "📦 Stok", min_value=0, value=product["stock"],
            step=1, key="edit_stock"
        )
        new_min_order = st.number_input(
            "📋 Min. Order", min_value=1, value=product.get("min_order", 1),
            step=1, key="edit_min_order"
        )

    st.markdown("---")
    col3, col4 = st.columns(2)
    with col3:
        new_weight = st.text_input(
            "⚖️ Berat", value=product.get("weight", "200g"), key="edit_weight"
        )
        colors_str = ", ".join(product.get("colors", []))
        new_colors = st.text_input(
            "🎨 Warna (koma)", value=colors_str, key="edit_colors"
        )
    with col4:
        new_desc = st.text_area(
            "📝 Deskripsi", value=product.get("description", ""),
            key="edit_desc", height=100
        )
        new_available = st.checkbox("✅ Tersedia",
                                    value=product.get("available", True),
                                    key="edit_available")
        new_can_return = st.checkbox("↩️ Bisa Retur",
                                     value=product.get("can_return", True),
                                     key="edit_return")

    # Image upload — 4 box grid with existing images
    st.markdown("---")
    existing_images = product.get("images", [])
    if not existing_images and product.get("image"):
        existing_images = [product["image"]]
    _render_image_slot_grid("edit", existing_images)

    # ── 3D Model ──
    st.markdown("---")
    st.markdown("### 🧊 Model 3D (Opsional)")
    existing_3d = product.get("model_3d")
    if existing_3d:
        st.success("✅ Produk ini sudah memiliki model 3D. Upload baru untuk mengganti.")
        if st.button("🗑️ Hapus Model 3D", key="edit_del_3d"):
            for i, p in enumerate(st.session_state.products):
                if p["sku"] == sku:
                    st.session_state.products[i]["model_3d"] = None
                    st.success("✅ Model 3D dihapus!")
                    st.rerun()
            st.stop()
    model_3d_file = st.file_uploader(
        "📤 Upload Model 3D (.glb / .gltf) — Maks 20MB",
        type=["glb", "gltf"],
        key="edit_model_3d",
        accept_multiple_files=False,
    )
    new_model_3d = save_3d_model(model_3d_file) if model_3d_file else existing_3d
    if model_3d_file and new_model_3d:
        st.success("✅ Model 3D baru siap disimpan! 🧊")

    col_save, col_del = st.columns([3, 1])

    with col_save:
        if st.button("💾 Simpan Perubahan", use_container_width=True,
                     type="primary"):
            if new_price_reseller >= new_price_retail:
                st.error("❌ Harga reseller harus lebih rendah dari harga retail")
            else:
                final_images = _collect_slot_images("edit")
                if not final_images:
                    final_images = ["https://placehold.co/400x400/E53935/FFF?text=EMPTY"]

                # Update product in session_state
                for i, p in enumerate(st.session_state.products):
                    if p["sku"] == sku:
                        st.session_state.products[i] = {
                            "sku": p["sku"],  # SKU stays the same
                            "name": new_name,
                            "category": new_category,
                            "subcategory": new_subcategory,
                            "brand": new_brand,
                            "price_reseller": new_price_reseller,
                            "price_retail": new_price_retail,
                            "stock": new_stock,
                            "available": new_available,
                            "can_return": new_can_return,
                            "images": final_images,
                            "model_3d": new_model_3d,
                            "description": new_desc,
                            "weight": new_weight,
                            "colors": [c.strip() for c in new_colors.split(",")
                                       if c.strip()],
                            "min_order": new_min_order,
                        }
                        break

                # Sync categories/subcategories
                if new_category not in st.session_state.categories:
                    st.session_state.categories.append(new_category)
                    st.session_state.categories.sort()
                if new_subcategory not in st.session_state.subcategories:
                    st.session_state.subcategories.append(new_subcategory)
                    st.session_state.subcategories.sort()

                st.success(f"✅ Produk `{sku}` berhasil diperbarui!")
                st.rerun()

    with col_del:
        if st.button("🗑️ Hapus Produk", use_container_width=True,
                     type="secondary"):
            confirm_key = f"confirm_delete_{sku}"
            if confirm_key not in st.session_state:
                st.session_state[confirm_key] = False

            if not st.session_state[confirm_key]:
                st.warning(f"⚠️ Yakin hapus **{product['name'][:50]}**?")
                if st.button("✔️ Ya, hapus!", key=f"yes_del_{sku}"):
                    st.session_state.products = [
                        p for p in st.session_state.products
                        if p["sku"] != sku
                    ]
                    st.success(f"🗑️ Produk `{sku}` dihapus!")
                    st.rerun()
                if st.button("✖️ Batal", key=f"no_del_{sku}"):
                    st.rerun()


# ── Tab: Kelola Kategori ────────────────────────────────────
def _tab_manage_categories():
    st.markdown("### 📂 Kelola Kategori & Subkategori")

    ccol1, ccol2 = st.columns(2)

    # ── Categories ──
    with ccol1:
        st.markdown("#### 📂 Kategori")
        cats = get_categories()

        # Show all categories with delete button
        cats_to_delete = []
        for cat in cats:
            c1, c2 = st.columns([5, 1])
            with c1:
                st.markdown(f"• {cat}")
            with c2:
                if st.button("❌", key=f"delcat_{cat}"):
                    cats_to_delete.append(cat)

        # Process deletes
        for cat in cats_to_delete:
            if cat in st.session_state.categories:
                st.session_state.categories.remove(cat)
            for p in st.session_state.products:
                if p["category"] == cat:
                    p["category"] = "Uncategorized"
            if "Uncategorized" not in st.session_state.categories:
                st.session_state.categories.append("Uncategorized")
                st.session_state.categories.sort()
            st.rerun()

        # Add new category - use form to isolate input
        st.markdown("---")
        with st.form("add_category_form", clear_on_submit=True):
            new_cat = st.text_input(
                "➕ Tambah Kategori Baru",
                placeholder="Nama kategori...",
                key="form_new_category"
            )
            submitted = st.form_submit_button("✅ Tambah Kategori")
            if submitted and new_cat.strip():
                if new_cat.strip() not in st.session_state.categories:
                    st.session_state.categories.append(new_cat.strip())
                    st.session_state.categories.sort()
                    st.success(f"✅ **{new_cat.strip()}** ditambahkan!")
                    st.rerun()
                else:
                    st.warning(f"⚠️ **{new_cat.strip()}** sudah ada!")

        # Rename category
        st.markdown("---")
        with st.form("rename_category_form", clear_on_submit=True):
            rename_from = st.selectbox("✏️ Ganti Nama Kategori", cats, key="rename_from_cat")
            rename_to = st.text_input("Nama Baru", placeholder="Nama baru...", key="rename_to_cat")
            if st.form_submit_button("💾 Simpan Nama Baru"):
                if rename_to.strip() and rename_to.strip() not in st.session_state.categories:
                    idx = st.session_state.categories.index(rename_from)
                    st.session_state.categories[idx] = rename_to.strip()
                    for p in st.session_state.products:
                        if p["category"] == rename_from:
                            p["category"] = rename_to.strip()
                    st.session_state.categories.sort()
                    st.success(f"✅ **{rename_from}** → **{rename_to.strip()}**")
                    st.rerun()
                elif rename_to.strip() in st.session_state.categories:
                    st.warning(f"⚠️ **{rename_to.strip()}** sudah ada!")

    # ── Subcategories ──
    with ccol2:
        st.markdown("#### 📌 Subkategori")
        subs = get_subcategories()

        # Show all subcategories with delete
        subs_to_delete = []
        for sub in subs:
            c1, c2 = st.columns([5, 1])
            with c1:
                st.markdown(f"• {sub}")
            with c2:
                if st.button("❌", key=f"delsub_{sub}"):
                    subs_to_delete.append(sub)

        # Process deletes
        for sub in subs_to_delete:
            if sub in st.session_state.subcategories:
                st.session_state.subcategories.remove(sub)
            for p in st.session_state.products:
                if p["subcategory"] == sub:
                    p["subcategory"] = "Lainnya"
            if "Lainnya" not in st.session_state.subcategories:
                st.session_state.subcategories.append("Lainnya")
                st.session_state.subcategories.sort()
            st.rerun()

        # Add new - use form
        st.markdown("---")
        with st.form("add_subcategory_form", clear_on_submit=True):
            new_sub = st.text_input(
                "➕ Tambah Subkategori Baru",
                placeholder="Nama subkategori...",
                key="form_new_subcategory"
            )
            if st.form_submit_button("✅ Tambah Subkategori"):
                if new_sub.strip() and new_sub.strip() not in st.session_state.subcategories:
                    st.session_state.subcategories.append(new_sub.strip())
                    st.session_state.subcategories.sort()
                    st.success(f"✅ **{new_sub.strip()}** ditambahkan!")
                    st.rerun()
                elif new_sub.strip() in st.session_state.subcategories:
                    st.warning(f"⚠️ **{new_sub.strip()}** sudah ada!")

        # Rename subcategory
        st.markdown("---")
        with st.form("rename_subcategory_form", clear_on_submit=True):
            rename_sub_from = st.selectbox("✏️ Ganti Nama Subkategori", subs, key="rename_from_sub")
            rename_sub_to = st.text_input("Nama Baru", placeholder="Nama baru...", key="rename_to_sub")
            if st.form_submit_button("💾 Simpan Nama Baru"):
                if rename_sub_to.strip() and rename_sub_to.strip() not in st.session_state.subcategories:
                    idx = st.session_state.subcategories.index(rename_sub_from)
                    st.session_state.subcategories[idx] = rename_sub_to.strip()
                    for p in st.session_state.products:
                        if p["subcategory"] == rename_sub_from:
                            p["subcategory"] = rename_sub_to.strip()
                    st.session_state.subcategories.sort()
                    st.success(f"✅ **{rename_sub_from}** → **{rename_sub_to.strip()}**")
                    st.rerun()
                elif rename_sub_to.strip() in st.session_state.subcategories:
                    st.warning(f"⚠️ **{rename_sub_to.strip()}** sudah ada!")

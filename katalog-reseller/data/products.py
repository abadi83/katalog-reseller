"""Sample product data for Katalog Reseller.
Each product has an 'images' list (max 4) with 1:1 ratio image URLs or base64 data.
"""

import base64
from io import BytesIO
from PIL import Image


def pil_to_base64(img: Image.Image, format: str = "JPEG") -> str:
    """Convert PIL Image to base64 data URL."""
    buf = BytesIO()
    img.save(buf, format=format, quality=85)
    b64 = base64.b64encode(buf.getvalue()).decode()
    mime = "image/jpeg" if format.upper() == "JPEG" else f"image/{format.lower()}"
    return f"data:{mime};base64,{b64}"


def make_1x1_placeholder(text: str, color: str = "E53935") -> str:
    """Generate a 1:1 placeholder image URL."""
    return f"https://placehold.co/400x400/{color}/FFF?text={text}"


PRODUCTS = [
    {
        "sku": "SRB-INF-177",
        "name": "Tas Punggung / Backpack Wanita SRB INF 177",
        "category": "FASHION WANITA",
        "subcategory": "Tas",
        "brand": "SRB",
        "price_reseller": 85000,
        "price_retail": 150000,
        "stock": 45,
        "available": True,
        "can_return": True,
        "images": ["https://placehold.co/400x400/E53935/FFF?text=TAS+177"],
        "description": "Tas punggung wanita stylish, cocok untuk kerja, kuliah, atau jalan-jalan. Bahan berkualitas, ringan, dan tahan lama.",
        "weight": "500g",
        "colors": ["Hitam", "Navy", "Coklat"],
        "min_order": 1
    },
    {
        "sku": "KMI-KZR-663",
        "name": "Dompet Casual Wanita KMI KZR 663",
        "category": "FASHION WANITA",
        "subcategory": "Dompet",
        "brand": "KMI",
        "price_reseller": 45000,
        "price_retail": 85000,
        "stock": 120,
        "available": True,
        "can_return": True,
        "images": ["https://placehold.co/400x400/FF7043/FFF?text=DMP+663"],
        "description": "Dompet casual wanita dengan banyak slot kartu. Desain minimalis elegan, bahan sintetis premium.",
        "weight": "150g",
        "colors": ["Pink", "Hitam", "Merah"],
        "min_order": 2
    },
    {
        "sku": "KRO-KZR-849",
        "name": "T-Shirt Casual Wanita KRO KZR 849",
        "category": "FASHION WANITA",
        "subcategory": "Atasan",
        "brand": "KRO",
        "price_reseller": 55000,
        "price_retail": 100000,
        "stock": 200,
        "available": True,
        "can_return": False,
        "images": ["https://placehold.co/400x400/AB47BC/FFF?text=TSH+849"],
        "description": "T-Shirt casual wanita bahan cotton combed 30s, nyaman dipakai sehari-hari. Tersedia berbagai ukuran.",
        "weight": "200g",
        "colors": ["Putih", "Hitam", "Abu-abu", "Navy"],
        "min_order": 3
    },
    {
        "sku": "KRO-KZR-848",
        "name": "T-Shirt Casual Wanita KRO KZR 848",
        "category": "FASHION WANITA",
        "subcategory": "Atasan",
        "brand": "KRO",
        "price_reseller": 55000,
        "price_retail": 100000,
        "stock": 180,
        "available": True,
        "can_return": False,
        "images": ["https://placehold.co/400x400/7E57C2/FFF?text=TSH+848"],
        "description": "T-Shirt casual wanita motif stripe, bahan cotton combed premium. Cocok untuk tampilan santai.",
        "weight": "200g",
        "colors": ["Putih-Hitam", "Navy-Putih"],
        "min_order": 3
    },
    {
        "sku": "BLK-KLL-001",
        "name": "Kemeja Casual Pria Blackkelly KLL 001",
        "category": "FASHION PRIA",
        "subcategory": "Kemeja",
        "brand": "Blackkelly",
        "price_reseller": 95000,
        "price_retail": 175000,
        "stock": 65,
        "available": True,
        "can_return": True,
        "images": ["https://placehold.co/400x400/3949AB/FFF?text=KMJ+001"],
        "description": "Kemeja casual pria bahan oxford premium. Cocok untuk kerja kantor atau acara formal.",
        "weight": "300g",
        "colors": ["Putih", "Biru Muda", "Hitam"],
        "min_order": 1
    },
    {
        "sku": "BLK-KLL-002",
        "name": "Celana Chino Pria Blackkelly KLL 002",
        "category": "FASHION PRIA",
        "subcategory": "Celana",
        "brand": "Blackkelly",
        "price_reseller": 110000,
        "price_retail": 200000,
        "stock": 40,
        "available": True,
        "can_return": True,
        "images": ["https://placehold.co/400x400/1E88E5/FFF?text=CHN+002"],
        "description": "Celana chino pria slim fit, bahan stretch nyaman. Tersedia berbagai ukuran 28-36.",
        "weight": "450g",
        "colors": ["Khaki", "Navy", "Hitam", "Abu-abu"],
        "min_order": 1
    },
    {
        "sku": "BLK-KLL-003",
        "name": "Jaket Bomber Pria Blackkelly KLL 003",
        "category": "FASHION PRIA",
        "subcategory": "Jaket",
        "brand": "Blackkelly",
        "price_reseller": 175000,
        "price_retail": 325000,
        "stock": 25,
        "available": True,
        "can_return": True,
        "images": ["https://placehold.co/400x400/283593/FFF?text=JKT+003"],
        "description": "Jaket bomber pria style klasik. Bahan taslan premium, cocok untuk cuaca Indonesia.",
        "weight": "600g",
        "colors": ["Hitam", "Army", "Navy"],
        "min_order": 1
    },
    {
        "sku": "ELZ-KID-101",
        "name": "Dress Anak Perempuan Elzatta KID 101",
        "category": "FASHION ANAK",
        "subcategory": "Dress",
        "brand": "Elzatta",
        "price_reseller": 75000,
        "price_retail": 135000,
        "stock": 55,
        "available": True,
        "can_return": True,
        "images": ["https://placehold.co/400x400/F06292/FFF?text=DRS+101"],
        "description": "Dress anak perempuan lucu dengan motif bunga. Bahan katun halus, nyaman untuk si kecil.",
        "weight": "200g",
        "colors": ["Pink", "Ungu", "Kuning"],
        "min_order": 1
    },
    {
        "sku": "ELZ-KID-102",
        "name": "Setelan Anak Laki-laki Elzatta KID 102",
        "category": "FASHION ANAK",
        "subcategory": "Setelan",
        "brand": "Elzatta",
        "price_reseller": 85000,
        "price_retail": 155000,
        "stock": 40,
        "available": True,
        "can_return": False,
        "images": ["https://placehold.co/400x400/42A5F5/FFF?text=SET+102"],
        "description": "Setelan anak laki-laki kemeja + celana. Cocok untuk lebaran atau acara spesial.",
        "weight": "300g",
        "colors": ["Putih", "Biru", "Krem"],
        "min_order": 1
    },
    {
        "sku": "KRO-SPT-201",
        "name": "Sepatu Sneakers Wanita KRO SPT 201",
        "category": "SEPATU",
        "subcategory": "Sneakers",
        "brand": "KRO",
        "price_reseller": 135000,
        "price_retail": 250000,
        "stock": 30,
        "available": True,
        "can_return": True,
        "images": ["https://placehold.co/400x400/EC407A/FFF?text=SNK+201"],
        "description": "Sepatu sneakers wanita trendi, sol karet anti slip. Nyaman dipakai seharian.",
        "weight": "700g",
        "colors": ["Putih", "Pink", "Hitam"],
        "sizes": ["36", "37", "38", "39", "40"],
        "min_order": 1
    },
    {
        "sku": "BLK-SPT-301",
        "name": "Sepatu Formal Pria Blackkelly SPT 301",
        "category": "SEPATU",
        "subcategory": "Formal",
        "brand": "Blackkelly",
        "price_reseller": 195000,
        "price_retail": 350000,
        "stock": 20,
        "available": True,
        "can_return": True,
        "images": ["https://placehold.co/400x400/5C6BC0/FFF?text=FRM+301"],
        "description": "Sepatu formal pria kulit sintetis premium. Cocok untuk meeting, interview, atau wedding.",
        "weight": "800g",
        "colors": ["Hitam", "Coklat Tua"],
        "sizes": ["38", "39", "40", "41", "42", "43"],
        "min_order": 1
    },
    {
        "sku": "SRB-INF-178",
        "name": "Sling Bag Wanita SRB INF 178",
        "category": "FASHION WANITA",
        "subcategory": "Tas",
        "brand": "SRB",
        "price_reseller": 65000,
        "price_retail": 120000,
        "stock": 80,
        "available": True,
        "can_return": True,
        "images": ["https://placehold.co/400x400/EF5350/FFF?text=SLG+178"],
        "description": "Sling bag kecil wanita, cocok untuk hangout. Bahan parasut waterproof.",
        "weight": "300g",
        "colors": ["Hitam", "Merah", "Krem", "Navy"],
        "min_order": 2
    },
    {
        "sku": "KMI-KZR-664",
        "name": "Tas Selempang Pria KMI KZR 664",
        "category": "FASHION PRIA",
        "subcategory": "Tas",
        "brand": "KMI",
        "price_reseller": 75000,
        "price_retail": 140000,
        "stock": 50,
        "available": True,
        "can_return": True,
        "images": ["https://placehold.co/400x400/26A69A/FFF?text=SLP+664"],
        "description": "Tas selempang pria casual, banyak kantong. Bahan canvass tebal dan awet.",
        "weight": "400g",
        "colors": ["Hitam", "Coklat", "Hijau Army"],
        "min_order": 1
    },
    {
        "sku": "SRB-ACC-501",
        "name": "Topi Baseball Unisex SRB ACC 501",
        "category": "AKSESORIS",
        "subcategory": "Topi",
        "brand": "SRB",
        "price_reseller": 25000,
        "price_retail": 50000,
        "stock": 150,
        "available": True,
        "can_return": False,
        "images": ["https://placehold.co/400x400/78909C/FFF?text=TOP+501"],
        "description": "Topi baseball unisex adjustable strap. Cocok untuk pria & wanita.",
        "weight": "100g",
        "colors": ["Hitam", "Putih", "Navy", "Merah"],
        "min_order": 5
    },
    {
        "sku": "ELZ-HIJ-701",
        "name": "Hijab Segi Empat Premium Elzatta HIJ 701",
        "category": "FASHION WANITA",
        "subcategory": "Hijab",
        "brand": "Elzatta",
        "price_reseller": 35000,
        "price_retail": 65000,
        "stock": 300,
        "available": True,
        "can_return": True,
        "images": ["https://placehold.co/400x400/BA68C8/FFF?text=HIJ+701"],
        "description": "Hijab segi empat bahan voal premium, flowy dan tidak licin. Mudah dibentuk.",
        "weight": "100g",
        "colors": ["Hitam", "Putih", "Dusty Pink", "Mocca", "Sage Green", "Lavender"],
        "min_order": 3
    },
    {
        "sku": "SALE-KRO-999",
        "name": "T-Shirt Basic Pria KRO SALE 999",
        "category": "SALE",
        "subcategory": "Atasan",
        "brand": "KRO",
        "price_reseller": 35000,
        "price_retail": 70000,
        "stock": 500,
        "available": True,
        "can_return": False,
        "images": ["https://placehold.co/400x400/F44336/FFF?text=SALE+999"],
        "description": "⚡ SALE UP TO 75%! T-Shirt basic pria bahan cotton combed. Harga grosir murah meriah.",
        "weight": "180g",
        "colors": ["Putih", "Hitam", "Abu-abu"],
        "min_order": 6
    },
    {
        "sku": "SALE-SRB-998",
        "name": "Kaos Kaki Premium SRB SALE 998",
        "category": "SALE",
        "subcategory": "Kaos Kaki",
        "brand": "SRB",
        "price_reseller": 15000,
        "price_retail": 30000,
        "stock": 1000,
        "available": True,
        "can_return": False,
        "images": ["https://placehold.co/400x400/FF5722/FFF?text=KAKI+998"],
        "description": "⚡ DISKON BESAR! Kaos kaki premium 1 pack isi 5 pasang. Nyaman dan awet.",
        "weight": "250g",
        "colors": ["Mix Warna"],
        "min_order": 2
    },
]

# Unique categories and brands for filtering
CATEGORIES = sorted(set(p["category"] for p in PRODUCTS))
BRANDS = sorted(set(p["brand"] for p in PRODUCTS))
SUBCATEGORIES = sorted(set(p["subcategory"] for p in PRODUCTS))

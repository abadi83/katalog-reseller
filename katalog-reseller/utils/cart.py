"""Shopping cart utilities for Katalog Reseller."""

import streamlit as st
from typing import List, Dict


def init_cart():
    """Initialize cart in session state."""
    if "cart" not in st.session_state:
        st.session_state.cart = []


def add_to_cart(sku: str, name: str, price: int, qty: int = 1):
    """Add item to cart."""
    init_cart()
    for item in st.session_state.cart:
        if item["sku"] == sku:
            item["qty"] += qty
            return
    st.session_state.cart.append({
        "sku": sku,
        "name": name,
        "price": price,
        "qty": qty,
    })


def remove_from_cart(sku: str):
    """Remove item from cart."""
    st.session_state.cart = [
        item for item in st.session_state.cart if item["sku"] != sku
    ]


def update_cart_qty(sku: str, qty: int):
    """Update quantity of item in cart."""
    if qty <= 0:
        remove_from_cart(sku)
    else:
        for item in st.session_state.cart:
            if item["sku"] == sku:
                item["qty"] = qty
                break


def get_cart_total() -> int:
    """Get total price of cart."""
    return sum(item["price"] * item["qty"] for item in st.session_state.cart)


def get_cart_count() -> int:
    """Get total items count in cart."""
    return sum(item["qty"] for item in st.session_state.cart)


def clear_cart():
    """Clear all items from cart."""
    st.session_state.cart = []

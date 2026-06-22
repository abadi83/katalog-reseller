"""Live Chat system for Admin ↔ Reseller communication.
Messages stored in st.session_state for real-time feel.
"""

import streamlit as st
from datetime import datetime
import time


def init_chat():
    """Initialize chat messages in session state."""
    if "chat_messages" not in st.session_state:
        st.session_state.chat_messages = []
    if "chat_read" not in st.session_state:
        st.session_state.chat_read = {}  # {username: last_read_timestamp}


def send_message(sender: str, sender_name: str, receiver: str, text: str):
    """Send a message to the chat."""
    if not text.strip():
        return
    msg = {
        "id": f"msg_{int(time.time()*1000)}",
        "sender": sender,
        "sender_name": sender_name,
        "receiver": receiver,
        "text": text.strip(),
        "timestamp": datetime.now().strftime("%H:%M"),
        "datetime": datetime.now().isoformat(),
    }
    st.session_state.chat_messages.append(msg)


def get_conversation(user: str, role: str) -> list:
    """Get messages for a specific user.
    - Admin sees ALL messages
    - Reseller sees messages from/to admin
    """
    if role == "admin":
        return st.session_state.chat_messages
    return [
        m for m in st.session_state.chat_messages
        if m["sender"] == user or m["receiver"] == user
        or m["sender"] == "admin" or (m["receiver"] == "admin" and m["sender"] == user)
    ]


def get_unread_count(user: str, role: str) -> int:
    """Count unread messages for a user."""
    if not st.session_state.chat_messages:
        return 0
    last_read = st.session_state.chat_read.get(user, "")
    if role == "admin":
        # Admin's unread = messages from resellers not read yet
        count = 0
        for m in st.session_state.chat_messages:
            if m["sender"] != "admin" and m["datetime"] > last_read:
                count += 1
        return count
    else:
        # Reseller's unread = messages from admin to them
        count = 0
        for m in st.session_state.chat_messages:
            if (m["sender"] == "admin" or m["receiver"] == user) and m["datetime"] > last_read:
                count += 1
        return count


def mark_read(user: str):
    """Mark all messages as read for a user."""
    if st.session_state.chat_messages:
        st.session_state.chat_read[user] = st.session_state.chat_messages[-1]["datetime"]


def get_reseller_list() -> list:
    """Get list of resellers who have sent messages (for admin view)."""
    senders = set()
    for m in st.session_state.chat_messages:
        if m["sender"] != "admin":
            senders.add((m["sender"], m["sender_name"]))
    return sorted(senders, key=lambda x: x[0])


# ── Page: Live Chat ──────────────────────────────────────────
def page_chat():
    """Live Chat page."""
    init_chat()

    user = st.session_state.get("username", "guest")
    role = st.session_state.get("role", "reseller")
    name = st.session_state.get("user", "User")

    st.markdown("## 💬 Live Chat")

    # Admin view: select which reseller to chat with
    if role == "admin":
        _admin_chat_view(user, name)
    else:
        _reseller_chat_view(user, name, role)

    # Mark messages as read
    mark_read(user)


# ── Admin Chat View ──────────────────────────────────────────
def _admin_chat_view(user: str, name: str):
    """Admin sees all resellers and can chat with any of them."""
    resellers = get_reseller_list()

    col1, col2 = st.columns([1, 3])

    with col1:
        st.markdown("### 📋 Reseller")
        selected_reseller = st.radio(
            "Pilih reseller",
            [("all", "📢 Semua (Broadcast)")] + [(r[0], f"👤 {r[1]}") for r in resellers],
            format_func=lambda x: x[1],
            key="admin_chat_select",
            label_visibility="collapsed"
        )
        selected_user = selected_reseller[0] if selected_reseller else "all"

        # Quick reply templates
        st.markdown("---")
        st.caption("⚡ Quick Reply:")
        templates = [
            ("✅", "Pesanan Anda sudah kami proses!"),
            ("📦", "Stok tersedia, silakan order."),
            ("💰", "Harga sudah include PPN ya Kak."),
            ("🚚", "Estimasi pengiriman 2-3 hari kerja."),
            ("🏷️", "Ada produk baru nih, cek katalog ya!"),
        ]
        for icon, tmpl in templates:
            if st.button(f"{icon} {tmpl[:40]}...", key=f"qr_{icon}",
                         use_container_width=True):
                receiver = "all" if selected_user == "all" else selected_user
                send_message(user, name, receiver, tmpl)
                st.rerun()

    with col2:
        if selected_user == "all":
            # Show all conversations
            messages = get_conversation(user, "admin")
            # Group by reseller
            by_sender = {}
            for m in messages:
                if m["sender"] != "admin":
                    key = m["sender"]
                else:
                    key = m.get("receiver", "all")
                if key not in by_sender:
                    by_sender[key] = []
                by_sender[key].append(m)

            if not by_sender:
                st.info("💬 Belum ada pesan dari reseller.")
                return

            for sender_key, msgs in by_sender.items():
                sender_name = msgs[0]["sender_name"] if msgs[0]["sender"] != "admin" else "Admin"
                display_name = f"👤 {sender_name}" if sender_key != "admin" else "📢 Admin"
                with st.expander(f"{display_name} — {len(msgs)} pesan", expanded=len(by_sender) <= 3):
                    _render_messages(msgs, user)
                    # Reply input
                    with st.container():
                        reply_text = st.chat_input(
                            f"Balas ke {sender_name}...",
                            key=f"reply_{sender_key}"
                        )
                        if reply_text:
                            send_message(user, name, sender_key, reply_text)
                            st.rerun()
        else:
            # Chat with specific reseller
            reseller_name = dict(resellers).get(selected_user, selected_user)
            st.markdown(f"### 💬 Chat dengan **{reseller_name}**")
            messages = [
                m for m in get_conversation(user, "admin")
                if m["sender"] == selected_user or m["receiver"] == selected_user
            ]

            _render_messages(messages, user)

            reply_text = st.chat_input(f"Ketik pesan ke {reseller_name}...")
            if reply_text:
                send_message(user, name, selected_user, reply_text)
                st.rerun()


# ── Reseller Chat View ───────────────────────────────────────
def _reseller_chat_view(user: str, name: str, role: str):
    """Reseller sees only their conversation with admin."""
    messages = get_conversation(user, role)

    # Auto-send welcome if no messages
    if not messages:
        st.info("💬 Kirim pesan ke Admin untuk bantuan!")
        # Admin auto-reply simulation
        send_message("admin", "Admin Toko", user,
                     "👋 Halo! Ada yang bisa kami bantu? Silakan kirim pesan di sini.")
        messages = get_conversation(user, role)

    _render_messages(messages, user)

    # Chat input
    reply_text = st.chat_input("Ketik pesan Anda ke Admin...")
    if reply_text:
        send_message(user, name, "admin", reply_text)
        st.rerun()

    # ── WhatsApp quick link ──
    st.markdown("---")
    st.markdown("### 📱 Butuh respon cepat?")
    wa_number = "6285211112525"  # Ganti dengan nomor WhatsApp Admin
    wa_link = f"https://wa.me/{wa_number}?text=Halo%20Admin%2C%20saya%20{name.replace(' ', '%20')}%20dari%20Katalog%20Reseller..."
    st.html(f"""
    <div style="
        background: #E8F5E9;
        border: 1px solid #A5D6A7;
        border-radius: 12px;
        padding: 16px;
        text-align: center;
    ">
        <p style="margin:0 0 8px 0; color:#2E7D32; font-weight:600;">
            💚 Chat langsung via WhatsApp untuk respon lebih cepat!
        </p>
        <a href="{wa_link}" target="_blank" style="
            display: inline-block;
            background: #25D366;
            color: white;
            padding: 10px 24px;
            border-radius: 25px;
            text-decoration: none;
            font-weight: 600;
            font-size: 0.9rem;
            transition: all 0.2s;
        ">
            💬 Chat via WhatsApp
        </a>
    </div>
    """)


# ── Message Renderer ─────────────────────────────────────────
def _render_messages(messages: list, current_user: str):
    """Render chat messages using Streamlit's native chat_message component."""
    if not messages:
        st.caption("Belum ada pesan.")
        return

    for msg in messages:
        is_mine = msg["sender"] == current_user
        role = "user" if is_mine else "assistant"
        sender = msg.get("sender_name", "")

        with st.chat_message(role, avatar="🧑" if is_mine else "🛍️"):
            # Sender label for non-user messages
            if not is_mine and sender:
                st.caption(f"**{sender}**")
            st.markdown(msg.get("text", ""))
            st.caption(msg.get("timestamp", ""))

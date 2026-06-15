"""Shared formatting utilities to avoid circular imports."""


def format_rupiah(amount: int) -> str:
    """Format integer as Rupiah currency string."""
    return f"Rp {amount:,.0f}".replace(",", ".")

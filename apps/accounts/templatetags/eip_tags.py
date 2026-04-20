from django import template

register = template.Library()


@register.filter
def montant(value):
    """Formate un montant XPF : entier avec séparateur de milliers (espace)."""
    try:
        n = round(float(value))
        return f"{n:,}".replace(",", "\u00a0")  # espace insécable
    except (TypeError, ValueError):
        return "—"


@register.filter
def xpf(value):
    """Formate un montant XPF avec suffixe."""
    m = montant(value)
    if m == "—":
        return "—"
    return f"{m} XPF"
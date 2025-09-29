# --- DISPLAY FALLBACKS FOR ExpenseDraft ---
try:
    # Stelle sicher, dass die Klasse verfügbar ist
    ExpenseDraft  # type: ignore[name-defined]
except NameError:
    pass
else:
    # Falls die Liste gross_amount erwartet: auf amount zurückfallen
    if not hasattr(ExpenseDraft, "gross_amount"):
        ExpenseDraft.gross_amount = property(lambda self: getattr(self, "amount", None))
    # Optionale, harmlose Platzhalter – Liste zeigt dann leer statt 0,00,
    # aber bricht nicht, wenn net/vat referenziert werden.
    if not hasattr(ExpenseDraft, "net_amount"):
        ExpenseDraft.net_amount = property(lambda self: None)
    if not hasattr(ExpenseDraft, "vat_amount"):
        ExpenseDraft.vat_amount = property(lambda self: None)
# --- END DISPLAY FALLBACKS ---

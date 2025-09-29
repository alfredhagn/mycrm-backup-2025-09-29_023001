#!/bin/sed -f

# Entferne existierende OCR-Route (nur wenn vorhanden)
s|.*path('expenses/ocr/from-email/'.*||g

# Hänge gezielte Route an
/^.*expenses\/draft\/from-email.*$/a\
    path('expenses/ocr/from-email/', V.draft_from_email_bridge, name='exp_ocr_from_email'),

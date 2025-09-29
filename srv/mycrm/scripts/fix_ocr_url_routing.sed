#!/bin/sed -f
# Import ggf. auf views_expenses als V korrigieren
s|^from \. import views as V$|from . import views_expenses as V|

# vorhandene OCR-Route entfernen (falls abweichend verdrahtet)
^\s*path\('expenses/ocr/from-email/'.*$\d

# unsere OCR-Route direkt nach draft/from-email einfügen
/^.*expenses\/draft\/from-email.*$/a\
    path('expenses/ocr/from-email/', V.ocr_from_email, name='exp_ocr_from_email'),

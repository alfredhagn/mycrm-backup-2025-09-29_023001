#!/bin/sed -f

# Füge OCR-Route ein nach dem Draft-Eintrag
/^.*expenses\/draft\/from-email.*$/a\
    path('expenses/ocr/from-email/', V.draft_from_email_bridge, name='exp_ocr_from_email'),

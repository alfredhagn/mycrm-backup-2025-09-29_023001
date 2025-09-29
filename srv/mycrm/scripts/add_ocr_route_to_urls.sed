#!/bin/sed -f

# Hänge gezielte OCR-Route an
/^.*expenses\/draft\/from-email.*$/a\
    path('expenses/ocr/from-email/', V.ocr_from_email, name='exp_ocr_from_email'),

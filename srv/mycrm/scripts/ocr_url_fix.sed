#!/bin/sed -f
s|^from \. import views as V$|from . import views_expenses as V|
/expenses\/ocr\/from-email/d
/expenses\/draft\/from-email/ a\
    path('expenses/ocr/from-email/', V.ocr_from_email, name='exp_ocr_from_email'),

#!/bin/sed -f

# Korrigiere Importzeile auf views_expenses
s|^from \. import views as V$|from . import views_expenses as V|

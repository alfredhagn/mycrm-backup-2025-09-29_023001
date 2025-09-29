#!/bin/sed -E

# Entferne doppelte Buttons „Als Ausgabe vormerken“ im oberen Bereich
/<a class="btn btn-outline-success" href="\/crm\/expenses\/draft\/from-email.*Als Ausgabe vormerken<\/a>/d
/<a class="btn btn-outline-success" href="\/crm\/invoices\/draft\/from-email.*Als Ausgabe vormerken<\/a>/d

# Entferne Button "Excel-Import öffnen"
/<a class="btn btn-outline-primary" href="\/crm\/expenses\/draft\/from-email.*Excel-Import öffnen<\/a>/d

# Entferne alle Anhangs-Buttons „Als Ausgabe vormerken“
s|<a class="btn btn-sm btn-outline-success"[^>]*>Als Ausgabe vormerken<\/a>||g

# Füge neuen Button unter der Aktionenspalte ein (nach div.actions)
# Dafür zunächst die Zeile markieren und dann mit einem Platzhalter tricksen
s|(<div class="actions" style="[^"]*">)|\1\n  <a class="btn btn-outline-warning" href="/crm/expenses/ocr/from-email/?message_id={{ message.id }}">Rechnung per OCR erkennen</a>|


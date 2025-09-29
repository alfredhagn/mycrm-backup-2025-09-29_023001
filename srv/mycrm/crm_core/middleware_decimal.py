
from django.utils.deprecation import MiddlewareMixin

class DecimalCommaMiddleware(MiddlewareMixin):
    """
    Normalisiert dezimale POST-Werte (Komma/Punkt) für Buchhaltungs-Formulare.
    """
    KEYS = {"amount","total","brutto","gross","gross_amount","betrag","summe","total_amount","total_gross","vat","vat_rate","mwst","ust"}

    @staticmethod
    def _norm(v):
        if v is None: return v
        s = str(v).strip().replace(" ", "")
        # Tausenderpunkte entfernen, Komma -> Punkt
        s = s.replace(".", "").replace(",", ".")
        return s

    def process_request(self, request):
        if request.method == "POST" and request.path.startswith(("/crm/expenses","/crm/expense")):
            try:
                data = request.POST.copy()
                for k in list(data.keys()):
                    lk = k.lower()
                    if lk in self.KEYS or any(x in lk for x in ("amount","total","gross","betrag","summe","vat","ust","mwst")):
                        data[k] = self._norm(data.get(k))
                request.POST = data
            except Exception:
                pass
        return None

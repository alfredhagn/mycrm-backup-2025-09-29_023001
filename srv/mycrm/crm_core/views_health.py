from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.db import connections
from django.contrib.staticfiles import finders

@login_required
def healthz(request):
    res = {}
    # DB
    try:
        with connections['default'].cursor() as c:
            c.execute("SELECT 1")
        res['db'] = 'ok'
    except Exception as e:
        res['db'] = f'error: {e.__class__.__name__}: {e}'
    # Statics
    try:
        res['static'] = 'ok' if finders.find('admin/css/base.css') else 'missing'
    except Exception as e:
        res['static'] = f'error: {e.__class__.__name__}: {e}'
    # MS-Token (robust erkennen)
    ok = False
    try:
        from .ms_tokens import get_ms_session  # type: ignore
        sess = get_ms_session(request)
        # 1) String-Token
        if isinstance(sess, str) and sess.strip():
            ok = True
        # 2) OAuth-/Requests-Session mit token-Attribut
        token = getattr(sess, 'token', None)
        if isinstance(token, dict) and token.get('access_token'):
            ok = True
    except Exception:
        pass
    # 3) Fallback: gängige Session-Keys prüfen
    if not ok:
        for k in ('access_token', 'token', 'msal', 'oauth'):
            v = request.session.get(k)
            if (isinstance(v, dict) and v.get('access_token')) or (isinstance(v, str) and v.strip()):
                ok = True
                break
    res['ms_token'] = 'ok' if ok else 'missing'
    return JsonResponse(res)

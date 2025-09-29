import os
from datetime import timedelta, datetime, timezone
from django.utils import timezone as djtz
from allauth.socialaccount.models import SocialToken, SocialAccount, SocialApp
from requests_oauthlib import OAuth2Session

TENANT = os.getenv("MS_TENANT") or os.getenv("MS_TENANT_ID") or "common"
CLIENT_ID = os.getenv("MS_CLIENT_ID", "")
CLIENT_SECRET = os.getenv("MS_CLIENT_SECRET", "")
TOKEN_URL = f"https://login.microsoftonline.com/{TENANT}/oauth2/v2.0/token"

DEFAULT_SCOPE = (
    "openid","offline_access","email","profile",
    "User.Read","Mail.Read","Mail.ReadWrite","Mail.Send",
    "Calendars.Read","Calendars.ReadWrite",
)

def _token_updater_for(user):
    def _updater(tok_dict):
        acc = SocialAccount.objects.get(user=user, provider="microsoft")
        app = SocialApp.objects.filter(provider="microsoft").first()
        st, _ = SocialToken.objects.get_or_create(app=app, account=acc)
        if tok_dict.get("access_token"):
            st.token = tok_dict["access_token"]
        if tok_dict.get("refresh_token"):
            st.refresh_token = tok_dict["refresh_token"]
        # expires_at ggf. aus expires_in berechnen
        expires_at = tok_dict.get("expires_at")
        if not expires_at and tok_dict.get("expires_in"):
            expires_at = djtz.now() + timedelta(seconds=int(tok_dict["expires_in"]))
        if expires_at:
            # requests-oauthlib liefert float/epoch oder datetime je nach Pfad
            if isinstance(expires_at, (int, float)):
                expires_at = datetime.fromtimestamp(expires_at, tz=timezone.utc)
            st.expires_at = expires_at
        st.save()
    return _updater

def get_ms_session(user, scope=DEFAULT_SCOPE):
    acc = SocialAccount.objects.get(user=user, provider="microsoft")
    app = SocialApp.objects.filter(provider="microsoft").first()
    st = SocialToken.objects.filter(account=acc, app=app).first()

    token = None
    if st:
        token = {
            "access_token": st.token,
            "refresh_token": st.refresh_token,
            "token_type": "Bearer",
            "expires_at": st.expires_at.timestamp() if st.expires_at else None,
        }

    extra = {"client_id": CLIENT_ID, "client_secret": CLIENT_SECRET}
    sess = OAuth2Session(
        CLIENT_ID,
        token=token,
        scope=list(scope),
        auto_refresh_url=TOKEN_URL,
        auto_refresh_kwargs=extra,
        token_updater=_token_updater_for(user),
    )

    # Optional: proaktiv refreshen, wenn <60s Restlaufzeit
    if st and st.expires_at:
        if (st.expires_at - datetime.now(timezone.utc)) < timedelta(seconds=60):
            sess.refresh_token(TOKEN_URL, **extra)

    return sess

from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from allauth.socialaccount.models import SocialToken
from django.utils import timezone

class PersistTokensAdapter(DefaultSocialAccountAdapter):
    """
    Erzwingt das Speichern/Updaten von Access- & Refresh-Token
    bei jedem Login/Refresh.
    """

    def save_token(self, request, sociallogin, token):
        # passende SocialApp ermitteln
        app = getattr(token, "app", None)
        if app is None:
            app = self.get_app(request, provider=sociallogin.account.provider)

        # vorhandenen DB-Token suchen/erstellen
        st, _ = SocialToken.objects.get_or_create(
            app=app,
            account=sociallogin.account,
        )

        # Felder immer aktualisieren
        st.token = getattr(token, "token", "") or st.token
        st.token_secret = getattr(token, "token_secret", "") or ""
        expires_at = getattr(token, "expires_at", None)
        if expires_at:
            st.expires_at = expires_at
        refresh_token = getattr(token, "refresh_token", None)
        if refresh_token:  # nur überschreiben, wenn auch geliefert
            st.refresh_token = refresh_token

        st.save()
        return st

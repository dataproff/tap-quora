"""quora Authentication."""

from __future__ import annotations

from singer_sdk.authenticators import OAuthAuthenticator, SingletonMeta

# The SingletonMeta metaclass makes your streams reuse the same authenticator instance.
# If this behaviour interferes with your use-case, you can remove the metaclass.
class QuoraAuthenticator(OAuthAuthenticator, metaclass=SingletonMeta):
    """Authenticator class for quora."""

    @property
    def oauth_request_body(self) -> dict:
        client_id = self.config.get("client_id", None)
        client_secret = self.config.get("client_secret", None)
        refresh_token = self.config.get("refresh_token", None)
        return {
            'client_id': client_id,
            'client_secret': client_secret,
            'refresh_token': refresh_token,
            'grant_type': 'refresh_token'
        }

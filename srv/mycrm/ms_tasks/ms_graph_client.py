# /srv/mycrm/ms_tasks/ms_graph_client.py
import requests
import os
from datetime import datetime, timedelta

class MSGraphClient:
    def __init__(self):
        self.tenant_id = os.getenv("AZURE_TENANT_ID")
        self.client_id = os.getenv("AZURE_CLIENT_ID")
        self.client_secret = os.getenv("AZURE_CLIENT_SECRET")
        self.scope = "https://graph.microsoft.com/.default"
        self.token_url = f"https://login.microsoftonline.com/{self.tenant_id}/oauth2/v2.0/token"
        self.access_token = None
        self.token_expires = datetime.utcnow()

    def get_token(self):
        if self.access_token and datetime.utcnow() < self.token_expires:
            return self.access_token

        resp = requests.post(self.token_url, data={
            "client_id": self.client_id,
            "scope": self.scope,
            "client_secret": self.client_secret,
            "grant_type": "client_credentials",
        }, timeout=30)

        if resp.status_code != 200:
            raise Exception(f"Token request failed ({resp.status_code}): {resp.text}")

        data = resp.json()
        self.access_token = data["access_token"]
        self.token_expires = datetime.utcnow() + timedelta(seconds=int(data.get("expires_in", "3600")) - 60)
        return self.access_token

    def _request(self, method, url, **kwargs):
        token = self.get_token()
        headers = kwargs.pop("headers", {})
        headers["Authorization"] = f"Bearer {token}"
        headers.setdefault("Content-Type", "application/json")

        full_url = f"https://graph.microsoft.com/v1.0{url}"
        r = requests.request(method, full_url, headers=headers, timeout=30, **kwargs)
        if not r.ok:
            raise Exception(f"Graph {method} {url} failed: {r.status_code} {r.text}")
        if r.text:
            return r.json()
        return {}

    def get(self, url):
        return self._request("GET", url)

    def patch(self, url, data):
        return self._request("PATCH", url, json=data)

    def delete(self, url):
        return self._request("DELETE", url)

    def post(self, url, data):
        return self._request("POST", url, json=data)

    def delete(self, url):
        return self._request("DELETE", url)

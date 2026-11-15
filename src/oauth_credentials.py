"""Local OAuth credential loading shared by Gmail and Sheets clients."""

import os
import tempfile


def _save_credentials(token_file, creds):
    directory = os.path.dirname(os.path.abspath(token_file))
    temporary_path = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w", encoding="utf-8", dir=directory,
            prefix=".oauth-token-", suffix=".tmp", delete=False,
        ) as token:
            temporary_path = token.name
            token.write(creds.to_json())
            token.flush()
            os.fsync(token.fileno())
        os.replace(temporary_path, token_file)
    except Exception:
        if temporary_path and os.path.exists(temporary_path):
            os.unlink(temporary_path)
        raise

def get_user_credentials(scopes, token_file):
    from google.auth.exceptions import RefreshError
    from google.auth.transport.requests import Request
    from google.oauth2.credentials import Credentials
    from google_auth_oauthlib.flow import InstalledAppFlow

    creds = None
    refreshed = False
    try:
        creds = Credentials.from_authorized_user_file(token_file, scopes)
    except FileNotFoundError:
        pass

    if creds and not creds.has_scopes(scopes):
        creds = None

    if creds and not creds.valid and creds.expired and creds.refresh_token:
        try:
            creds.refresh(Request())
            refreshed = True
        except RefreshError as error:
            if "invalid_grant" not in str(error).lower():
                raise
            creds = None

    if creds and creds.valid:
        if refreshed:
            _save_credentials(token_file, creds)
        return creds

    creds = InstalledAppFlow.from_client_secrets_file(
        "credentials/credentials.json", scopes
    ).run_local_server(port=0)
    _save_credentials(token_file, creds)
    return creds

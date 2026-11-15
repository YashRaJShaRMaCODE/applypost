import sys
import tempfile
import types
import unittest
from pathlib import Path
from unittest.mock import Mock, patch

from oauth_credentials import _save_credentials, get_user_credentials


class OAuthCredentialTests(unittest.TestCase):
    def google_modules(self, refresh_error, cached, authorized):
        google = types.ModuleType("google")
        google.__path__ = []
        auth = types.ModuleType("google.auth")
        auth.__path__ = []
        exceptions = types.ModuleType("google.auth.exceptions")
        exceptions.RefreshError = refresh_error
        transport = types.ModuleType("google.auth.transport")
        transport.__path__ = []
        requests = types.ModuleType("google.auth.transport.requests")
        requests.Request = Mock
        oauth2 = types.ModuleType("google.oauth2")
        oauth2.__path__ = []
        credentials = types.ModuleType("google.oauth2.credentials")
        credentials.Credentials = Mock(from_authorized_user_file=Mock(return_value=cached))
        oauthlib = types.ModuleType("google_auth_oauthlib")
        oauthlib.__path__ = []
        flow_module = types.ModuleType("google_auth_oauthlib.flow")
        flow_module.InstalledAppFlow = Mock(from_client_secrets_file=Mock(return_value=Mock(
            run_local_server=Mock(return_value=authorized)
        )))
        modules = {
            "google": google,
            "google.auth": auth,
            "google.auth.exceptions": exceptions,
            "google.auth.transport": transport,
            "google.auth.transport.requests": requests,
            "google.oauth2": oauth2,
            "google.oauth2.credentials": credentials,
            "google_auth_oauthlib": oauthlib,
            "google_auth_oauthlib.flow": flow_module,
        }
        return modules, credentials, flow_module

    def test_revoked_refresh_token_restarts_local_authorization(self):
        class FakeRefreshError(Exception):
            pass

        cached = Mock(valid=False, expired=True, refresh_token="refresh-token")
        cached.refresh.side_effect = FakeRefreshError("invalid_grant: revoked")
        authorized = Mock(valid=True, to_json=Mock(return_value='{"token":"fresh"}'))
        modules, _credentials, flow = self.google_modules(FakeRefreshError, cached, authorized)

        with patch.dict(sys.modules, modules), patch("oauth_credentials._save_credentials") as save:
            result = get_user_credentials(["scope"], "token.json")

        self.assertIs(result, authorized)
        flow.InstalledAppFlow.from_client_secrets_file.assert_called_once_with(
            "credentials/credentials.json", ["scope"]
        )
        save.assert_called_once_with("token.json", authorized)

    def test_transient_refresh_error_is_not_hidden_by_a_new_login(self):
        class FakeRefreshError(Exception):
            pass

        cached = Mock(valid=False, expired=True, refresh_token="refresh-token")
        cached.refresh.side_effect = FakeRefreshError("temporary network error")
        modules, _, flow = self.google_modules(FakeRefreshError, cached, Mock())

        with patch.dict(sys.modules, modules), self.assertRaisesRegex(FakeRefreshError, "temporary"):
            get_user_credentials(["scope"], "token.json")

        flow.InstalledAppFlow.from_client_secrets_file.assert_not_called()

    def test_valid_cached_token_is_reused_without_rewriting(self):
        cached = Mock(valid=True)
        cached.has_scopes.return_value = True
        modules, _, flow = self.google_modules(Exception, cached, Mock())

        with patch.dict(sys.modules, modules), patch("oauth_credentials._save_credentials") as save:
            result = get_user_credentials(["scope"], "token.json")

        self.assertIs(result, cached)
        flow.InstalledAppFlow.from_client_secrets_file.assert_not_called()
        save.assert_not_called()

    def test_cached_token_with_missing_scopes_restarts_authorization(self):
        cached = Mock(valid=True)
        cached.has_scopes.return_value = False
        authorized = Mock(valid=True, to_json=Mock(return_value='{"token":"scoped"}'))
        modules, _, flow = self.google_modules(Exception, cached, authorized)

        with patch.dict(sys.modules, modules), patch("oauth_credentials._save_credentials"):
            result = get_user_credentials(["new-scope"], "token.json")

        self.assertIs(result, authorized)
        flow.InstalledAppFlow.from_client_secrets_file.assert_called_once_with(
            "credentials/credentials.json", ["new-scope"]
        )

    def test_token_is_replaced_atomically_and_failed_replace_preserves_previous_file(self):
        with tempfile.TemporaryDirectory() as directory:
            token_path = Path(directory) / "token.json"
            token_path.write_text('{"token":"old"}', encoding="utf-8")
            credentials = Mock(to_json=Mock(return_value='{"token":"fresh"}'))
            _save_credentials(token_path, credentials)
            self.assertEqual(token_path.read_text(encoding="utf-8"), '{"token":"fresh"}')
            self.assertEqual(list(Path(directory).glob(".oauth-token-*.tmp")), [])

            with patch("oauth_credentials.os.replace", side_effect=OSError("replace failed")), \
                    self.assertRaisesRegex(OSError, "replace failed"):
                _save_credentials(token_path, credentials)
            self.assertEqual(token_path.read_text(encoding="utf-8"), '{"token":"fresh"}')
            self.assertEqual(list(Path(directory).glob(".oauth-token-*.tmp")), [])


if __name__ == "__main__":
    unittest.main()

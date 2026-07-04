import unittest

from fastapi.testclient import TestClient

from main import app

client: TestClient = TestClient(app)


class TestPasswordCheckerAPI(unittest.TestCase):
    """HTTP-level testing environment for the /check_password/ endpoint."""

    def _post(self, username: str = "jkowalski", email: str = "jan.kowalski@securebank.pl",
              password: str = "P@r@mp@sk1l@m2026", prev_password: str | None = None,
              # type: ignore[name-defined]
              raw_payload: dict | None = None) -> "httpx.Response":
        """Helper to build a request payload and POST it to the endpoint."""
        payload: dict = raw_payload if raw_payload is not None else {
            "username": username,
            "email": email,
            "password": password,
        }
        if prev_password is not None and raw_payload is None:
            payload["prev_password"] = prev_password

        return client.post("/check_password/", json=payload)

    def test_root_returns_welcome_message(self) -> None:
        """Root endpoint should respond with a friendly welcome message."""
        response = client.get("/")

        self.assertEqual(response.status_code, 200)
        self.assertIn("message", response.json())

    def test_easy(self) -> None:
        """Simple weak password test through the API."""
        response = self._post(password="MamaTata1")

        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.json()["is_compliant"])

    def test_hard_eset_password(self) -> None:
        """Hard and long password generated via eset, through the API."""
        response = self._post(password="+$D@=0~<LPG@d@o")

        self.assertEqual(response.status_code, 200)
        body: dict = response.json()
        self.assertTrue(body["is_compliant"])
        self.assertEqual(body["score"], 4)

    def test_with_prev(self) -> None:
        """Password too similar to previous one, checked through the API."""
        response = self._post(
            password="P@r@mp@sk1l@m2077",
            prev_password="P@r@mp@sk1l@m2026",
        )

        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.json()["is_compliant"])

    def test_response_shape_contains_expected_fields(self) -> None:
        """Response body should always match the documented response model."""
        response = self._post()

        body: dict = response.json()
        expected_fields: set[str] = {
            "score", "label", "color", "description", "is_compliant"}

        self.assertEqual(response.status_code, 200)
        self.assertTrue(expected_fields.issubset(body.keys()))
        self.assertIsInstance(body["score"], int)
        self.assertTrue(0 <= body["score"] <= 4)

    def test_common_password_rejected_via_api(self) -> None:
        """Password present in the known common-passwords list should score 0."""
        response = self._post(password="123456789")

        body: dict = response.json()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(body["score"], 0)
        self.assertFalse(body["is_compliant"])

    def test_edge_case_missing_password_field(self) -> None:
        """Request without a password field must be rejected with 422."""
        response = self._post(
            raw_payload={"username": "jkowalski", "email": "jan.kowalski@securebank.pl"})

        self.assertEqual(response.status_code, 422)

    def test_edge_case_invalid_email(self) -> None:
        """Request with a malformed email address must be rejected with 422."""
        response = self._post(email="not-an-email")

        self.assertEqual(response.status_code, 422)

    def test_edge_case_malformed_json(self) -> None:
        """Request body that isn't valid JSON must be rejected with 422."""
        response = client.post(
            "/check_password/",
            content="{not valid json",
            headers={"Content-Type": "application/json"},
        )

        self.assertEqual(response.status_code, 422)

    def test_edge_case_password_too_long(self) -> None:
        """Password exceeding the maximum accepted length must be rejected with 422."""
        response = self._post(password="a" * 200)

        self.assertEqual(response.status_code, 422)

    def test_edge_case_password_redacted_in_validation_logs(self) -> None:
        """Plaintext password must never appear in logs, even on validation failure."""
        secret_password: str = "SuperSecretPlaintext123!"

        with self.assertLogs("main", level="ERROR") as captured:
            self._post(email="not-an-email", password=secret_password)

        combined_log_output: str = " ".join(captured.output)
        self.assertNotIn(secret_password, combined_log_output)

    def test_edge_case_password_redacted_when_password_itself_invalid(self) -> None:
        """Password field's own invalid input must be redacted, not logged in plaintext."""
        secret_password: str = "a" * 200

        with self.assertLogs("main", level="ERROR") as captured:
            self._post(password=secret_password)

        combined_log_output: str = " ".join(captured.output)
        self.assertNotIn(secret_password, combined_log_output)
        self.assertIn("REDACTED", combined_log_output)


if __name__ == "__main__":
    unittest.main()

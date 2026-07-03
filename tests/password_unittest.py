import unittest
import os
from src import password_check, prepare_user_inputs

LANGUAGE_PATH: str = 'lang-english.txt'
with open(os.path.abspath(LANGUAGE_PATH), "r") as f:
    GLOBAL_WORDS: list[str] = f.read().splitlines()


class TestPasswordChecker(unittest.TestCase):
    """Password testing environment."""

    def _check(self, password: str, username: str = "jkowalski",
               email: str = "jan.kowalski@securebank.pl", prev_password: str = None) -> dict[str, str | int | bool | list[str]]:
        """Helper to prepare inputs and run the checker."""
        user_inputs: list[str] = prepare_user_inputs(
            username=username, email=email)
        user_inputs.extend(GLOBAL_WORDS)
        return password_check(password=password, user_inputs=user_inputs, prev_password=prev_password)

    def test_easy(self) -> None:
        """Simple password test."""
        password: str = "MamaTata1"

        result: dict[str, str | int | bool | list[str]
                     ] = self._check(password=password)

        self.assertFalse(result["is_compliant"])

    def test_easy_password(self) -> None:
        """Easy long password test."""
        password: str = "qwerty123456789"

        result: dict[str, str | int | bool | list[str]
                     ] = self._check(password=password)

        self.assertFalse(result["is_compliant"])

    def test_hard_password_connected(self) -> None:
        """Long and hard password but with hints in username and email adress."""
        password: str = "janek2026securebank!?"
        username: str = "jkowalski"
        email: str = "jan.kowalski@securebank.pl"

        result: dict[str, str | int | bool | list[str]] = self._check(
            password=password, username=username, email=email)

        self.assertFalse(result["is_compliant"])

    def test_hard_common_words(self) -> None:
        """Long and hard password but with common words."""
        password: str = "ilovemywifekasia!"

        result: dict[str, str | int | bool | list[str]
                     ] = self._check(password=password)

        self.assertFalse(result["is_compliant"])

    def test_hard_eset_password(self) -> None:
        """Hard and long password generated via eset."""
        password: str = "+$D@=0~<LPG@d@o"

        result: dict[str, str | int | bool | list[str]
                     ] = self._check(password=password)

        self.assertTrue(result["is_compliant"])
        self.assertEqual(result["score"], 4)

    def test_medium_eset_password(self) -> None:
        """Hard but shorter password generated via eset."""
        password: str = "G,azBR0p.}.z"

        result: dict[str, str | int | bool | list[str]
                     ] = self._check(password=password)

        self.assertTrue(result["is_compliant"])
        self.assertEqual(result["score"], 3)

    def test_before_prev(self) -> None:
        """Test for checking password without any relation."""
        password: str = "P@r@mp@sk1l@m2026"

        result: dict[str, str | int | bool | list[str]
                     ] = self._check(password=password)

        self.assertTrue(result["is_compliant"])
        self.assertEqual(result["score"], 4)

    def test_with_prev(self) -> None:
        """Test for checking password with relation to previous one."""
        prev_password: str = "P@r@mp@sk1l@m2026"
        password: str = "P@r@mp@sk1l@m2077"

        result: dict[str, str | int | bool | list[str]] = self._check(
            password=password, prev_password=prev_password)

        self.assertFalse(result["is_compliant"])

    def test_edge_case_empty_or_very_short(self) -> None:
        """Verify that short passwords are rejected."""

        result_empty: dict[str, str | int | bool |
                           list[str]] = self._check(password="")
        result_short: dict[str, str | int | bool |
                           list[str]] = self._check(password="A1!")

        self.assertFalse(result_empty["is_compliant"])
        self.assertFalse(result_short["is_compliant"])

    def test_edge_case_whitespace_padding(self) -> None:
        """Password is short but filled with white spaces."""
        password: str = "MamaTata1                      "

        result: dict[str, str | int | bool | list[str]
                     ] = self._check(password=password)

        self.assertFalse(result["is_compliant"])

    def test_edge_case_case_insensitivity(self) -> None:
        """Check username inclusion."""
        password: str = "jkowalskisecret2026"
        username: str = "JKOWALSKI"
        email: str = "jan.kowalski@securebank.pl"

        result: dict[str, str | int | bool | list[str]] = self._check(
            password=password, username=username, email=email)

        self.assertFalse(result["is_compliant"])
        self.assertIn(username.lower(), result["description"])


if __name__ == "__main__":
    unittest.main()

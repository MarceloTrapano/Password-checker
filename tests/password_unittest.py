import unittest
import os
from src import password_check, prepare_user_inputs

LANGUAGE_PATH = 'lang-english.txt'
with open(os.path.abspath(LANGUAGE_PATH), "r") as f:
    GLOBAL_WORDS = f.read().splitlines()


class TestPasswordChecker(unittest.TestCase):

    def test_easy(self):
        password = "MamaTata1"
        username = "jkowalski"
        email = "jan.kowalski@securebank.pl"

        user_inputs = prepare_user_inputs(username=username, email=email)
        user_inputs.extend(GLOBAL_WORDS)
        result = password_check(password=password, user_inputs=user_inputs)

        self.assertFalse(result["is_compliant"])

    def test_easy_password(self):
        password = "qwerty123456789"
        username = "jkowalski"
        email = "jan.kowalski@wp.pl"

        user_inputs = prepare_user_inputs(username=username, email=email)
        user_inputs.extend(GLOBAL_WORDS)
        result = password_check(password=password, user_inputs=user_inputs)

        self.assertFalse(result["is_compliant"])

    def test_hard_password_connected(self):
        password = "janek2026securebank!?"
        username = "jkowalski"
        email = "jan.kowalski@securebank.pl"

        user_inputs = prepare_user_inputs(username=username, email=email)
        user_inputs.extend(GLOBAL_WORDS)
        result = password_check(password=password, user_inputs=user_inputs)

        self.assertFalse(result["is_compliant"])

    def test_hard_common_words(self):
        password = "ilovemywifekasia!"
        username = "jkowalski"
        email = "jan.kowalski@securebank.pl"

        user_inputs = prepare_user_inputs(username=username, email=email)
        user_inputs.extend(GLOBAL_WORDS)
        result = password_check(password=password, user_inputs=user_inputs)

        self.assertFalse(result["is_compliant"])

    def test_hard_eset_password(self):
        password = "+$D@=0~<LPG@d@o"
        username = "jkowalski"
        email = "jan.kowalski@securebank.pl"

        user_inputs = prepare_user_inputs(username=username, email=email)
        user_inputs.extend(GLOBAL_WORDS)
        result = password_check(password=password, user_inputs=user_inputs)

        self.assertTrue(result["is_compliant"])
        self.assertEqual(result["score"], 4)

    def test_medium_eset_password(self):
        password = "G,azBR0p.}.z"
        username = "jkowalski"
        email = "jan.kowalski@securebank.pl"

        user_inputs = prepare_user_inputs(username=username, email=email)
        user_inputs.extend(GLOBAL_WORDS)
        result = password_check(password=password, user_inputs=user_inputs)

        self.assertTrue(result["is_compliant"])
        self.assertEqual(result["score"], 3)

    def test_before_prev(self):
        password = "P@r@mp@sk1l@m2026"
        username = "jkowalski"
        email = "jan.kowalski@securebank.pl"

        user_inputs = prepare_user_inputs(username=username, email=email)
        user_inputs.extend(GLOBAL_WORDS)
        result = password_check(password=password, user_inputs=user_inputs)

        self.assertTrue(result["is_compliant"])
        self.assertEqual(result["score"], 4)

    def test_with_prev(self):
        prev_password = "P@r@mp@sk1l@m2026"
        password = "P@r@mp@sk1l@m2077"
        username = "jkowalski"
        email = "jan.kowalski@securebank.pl"

        user_inputs = prepare_user_inputs(username=username, email=email)
        user_inputs.extend(GLOBAL_WORDS)
        result = password_check(
            password=password, user_inputs=user_inputs, prev_password=prev_password)

        self.assertFalse(result["is_compliant"])

    def test_edge_case_empty_or_very_short(self):
        user_inputs = prepare_user_inputs(
            username="jkowalski", email="jan@wp.pl")
        user_inputs.extend(GLOBAL_WORDS)

        result_empty = password_check(password="", user_inputs=user_inputs)
        result_short = password_check(password="A1!", user_inputs=user_inputs)

        self.assertFalse(result_empty["is_compliant"])
        self.assertFalse(result_short["is_compliant"])

    def test_edge_case_whitespace_padding(self):
        password_with_spaces = "MamaTata1                      "
        user_inputs = prepare_user_inputs(
            username="jkowalski", email="jan@wp.pl")
        user_inputs.extend(GLOBAL_WORDS)

        result = password_check(
            password=password_with_spaces, user_inputs=user_inputs)

        self.assertFalse(result["is_compliant"])

    def test_edge_case_case_insensitivity(self):

        username = "JKOWALSKI"
        password = "jkowalskisecret2026"

        user_inputs = prepare_user_inputs(
            username=username, email="jan@securebank.pl")
        user_inputs.extend(GLOBAL_WORDS)
        result = password_check(password=password, user_inputs=user_inputs)

        self.assertFalse(result["is_compliant"])


if __name__ == "__main__":
    unittest.main()

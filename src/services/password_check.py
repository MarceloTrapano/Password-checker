import re
import logging

from zxcvbn import zxcvbn

from src.common.logger import password_logger
from src.common.password_strength import PasswordStrength


LEVENSHTEIN_DISTANCE_THRESHOLD: int = 4
WORD_LENGTH_THRESHOLD: int = 4
MINIMAL_PASSWORD_LENGTH: int = 12
RECOMENDED_PASSWORD_LENGTH: int = 15

logger = password_logger(__name__)


def password_check(password: str, user_inputs: list[str] | None = None, prev_password: str | None = None, common_passwords: set[str] | None = None) -> dict[str, str | int | bool | list[str]]:
    """Check strength of password.

    Args:
        password (str): input password.
        user_inputs (list[str], optional): list with hints for password. Defaults to [].
        prev_password (str | None, optional): previous password. Defaults to None.

    Returns:
        dict[str, str | int | bool]: dictionary with password strength information.
    """
    logger.info("Checking password")
    password = password.strip()  # parse white spaces
    password_lower: str = password.lower()
    password_status: PasswordStrength

    if common_passwords and password_lower in common_passwords:
        logger.info("Password has been detected in database.")
        return {
            "score": 0,
            "label": "Very weak",
            "color":  "#FF4D4D",
            "description": "Password has been detected in database.",
            "is_compliant": False
        }

    if prev_password:
        prev_password_lower = prev_password.lower()
        if password_lower == prev_password_lower:  # Previous password is same
            password_status = PasswordStrength.VERY_WEAK
            logger.info("Password classified as VERY_WEAK")
            return {
                "score": password_status.score, "label": password_status.label, "color": password_status.color,
                "description": "New password cannot be identical to your previous password.", "is_compliant": password_status.is_compliant
            }

        # Previous password is too similar
        if _levenshtein_distance(password_lower, prev_password_lower) < LEVENSHTEIN_DISTANCE_THRESHOLD:
            password_status = PasswordStrength.VERY_WEAK
            logger.info("Password classified as WEAK")
            return {
                "score": password_status.score, "label": password_status.label, "color": password_status.color,
                "description": "Password is too similar to your previous password. Please make more substantial changes.", "is_compliant": password_status.is_compliant
            }

        user_inputs.append(prev_password_lower)

    # Sorting is necessary to exclude word inclusion
    sorted_inputs: list[str] = sorted(
        list(set(user_inputs)), key=len, reverse=True)
    virtual_password: str = password_lower

    words_detected: list[str] = []
    # Mask words with single token
    for item in sorted_inputs:
        if item in virtual_password:
            words_detected.append(item)
            virtual_password = virtual_password.replace(item, "*")

    # Handle true password length
    if len(virtual_password) < MINIMAL_PASSWORD_LENGTH:
        password_status = PasswordStrength.VERY_WEAK
        desc: str = "Password is too short."
        if words_detected:
            desc = f"Password relies too heavily on contextual data ({', '.join(words_detected)}). Its effective cryptographic length is too short."
        logger.info("Password classified as VERY_WEAK")
        return {
            "score": password_status.score, "label": password_status.label, "color": password_status.color,
            "description": desc, "is_compliant": password_status.is_compliant
        }

    analysis = zxcvbn(password, user_inputs=user_inputs)

    password_status = PasswordStrength.from_score(analysis['score'])

    final_score = password_status.score
    # Penalty for password length between 12 and 15
    if len(virtual_password) < RECOMENDED_PASSWORD_LENGTH:
        final_score = max(0, final_score - 1)

    password_status = PasswordStrength.from_score(final_score)
    logger.info(f"Password classified as {password_status.label}")

    return {
        "score": password_status.score,
        "label": password_status.label,
        "color": password_status.color,
        "description": password_status.description if password_status.is_compliant else "Contains weak patterns or personal info.",
        "is_compliant": password_status.is_compliant,
        "suggestions": analysis['feedback']['suggestions']
    }


def prepare_user_inputs(username: str, email: str) -> list[str]:
    """Prepare user inputs list for better password protection.

    Args:
        username (str): username.
        email (str): email adress.

    Returns:
        list[str]: list of extracted words from username and email adress.
    """
    inputs: list[str] = []

    if username:
        inputs.append(username.lower())

    if email:
        inputs.append(email.lower())

        parts: list[str] = email.lower().split('@')
        inputs.extend(parts)

        domain: str = parts[1]
        domain_name: str = domain.split('.')[0]
        inputs.append(domain_name)

        sub_parts: list[str] = re.split(r'[._-]', parts[0])
        inputs.extend(sub_parts)

    filtered_inputs = filter(lambda word: len(
        word) >= WORD_LENGTH_THRESHOLD, inputs)
    distinct_inputs = set(filtered_inputs)
    final_inputs = list(distinct_inputs)

    return final_inputs


def _levenshtein_distance(s1: str, s2: str) -> int:
    """Calculates the edit distance to prevent minor changes from previous passwords.

    Args:
        s1 (str): first word.
        s2 (str): second word.

    Returns:
        int: calculated distance.
    """
    current_row: list[int]
    insertions: int
    deletions: int
    substitutions: int

    if len(s1) < len(s2):
        return _levenshtein_distance(s2, s1)
    if len(s2) == 0:
        return len(s1)

    previous_row: list[int] = list(range(len(s2) + 1))
    for i, c1 in enumerate(s1):
        current_row = [i + 1]
        for j, c2 in enumerate(s2):
            insertions = previous_row[j + 1] + 1
            deletions = current_row[j] + 1
            substitutions = previous_row[j] + (c1 != c2)
            current_row.append(min(insertions, deletions, substitutions))
        previous_row = current_row

    return previous_row[-1]

import re
from zxcvbn import zxcvbn

from src import PasswordStrength


def password_check(password: str, user_inputs: list[str] = [], prev_password: str | None = None) -> dict[str, str | int | bool]:
    password_lower: str = password.lower()

    if prev_password:
        prev_password_lower = prev_password.lower()
        if password_lower == prev_password_lower:
            return {
                "score": 0, "label": "Very weak", "color": "#FF4D4D",
                "description": "New password cannot be identical to your previous password.", "is_compliant": False
            }

        if _levenshtein_distance(password_lower, prev_password_lower) < 4:
            return {
                "score": 1, "label": "Weak", "color": "#FF944D",
                "description": "Password is too similar to your previous password. Please make more substantial changes.", "is_compliant": False
            }

        user_inputs.append(prev_password_lower)

    sorted_inputs = sorted(list(set(user_inputs)), key=len, reverse=True)
    virtual_password = password_lower

    words_detected = []
    for item in sorted_inputs:
        if len(item) >= 3 and item in virtual_password:
            words_detected.append(item)
            virtual_password = virtual_password.replace(item, "*")

    if len(virtual_password) < 12:
        strength = PasswordStrength.VERY_WEAK
        desc = "Password is too short."
        if words_detected:
            desc = f"Password relies too heavily on contextual data ({', '.join(words_detected)}). Its effective cryptographic length is too short."

        return {
            "score": strength.score, "label": strength.label, "color": strength.color,
            "description": desc, "is_compliant": False
        }

    analysis = zxcvbn(password, user_inputs=user_inputs)
    strength = PasswordStrength.from_score(analysis['score'])

    final_score = strength.score
    if words_detected:
        final_score = max(0, final_score - 1)

    final_strength = PasswordStrength.from_score(final_score)
    is_compliant = final_strength.score >= 3

    return {
        "score": final_strength.score,
        "label": final_strength.label,
        "color": final_strength.color,
        "description": final_strength.description if is_compliant else "Contains weak patterns or personal info.",
        "is_compliant": is_compliant,
        "suggestions": analysis['feedback']['suggestions']
    }


def prepare_user_inputs(username, email):
    inputs = []
    if username:
        inputs.append(username.lower())
    if email:
        inputs.append(email.lower())
        parts = email.lower().split('@')
        inputs.extend(parts)
        domain = parts[1]
        domain_name = domain.split('.')[0]
        inputs.append(domain_name)
        sub_parts = re.split(r'[._-]', parts[0])
        inputs.extend(sub_parts)
    return list(set(filter(None, inputs)))


def _levenshtein_distance(s1: str, s2: str) -> int:
    """Calculates the edit distance to prevent minor changes from previous passwords."""
    if len(s1) < len(s2):
        return _levenshtein_distance(s2, s1)
    if len(s2) == 0:
        return len(s1)

    previous_row = range(len(s2) + 1)
    for i, c1 in enumerate(s1):
        current_row = [i + 1]
        for j, c2 in enumerate(s2):
            insertions = previous_row[j + 1] + 1
            deletions = current_row[j] + 1
            substitutions = previous_row[j] + (c1 != c2)
            current_row.append(min(insertions, deletions, substitutions))
        previous_row = current_row

    return previous_row[-1]

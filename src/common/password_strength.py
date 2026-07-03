from enum import Enum


class PasswordStrength(Enum):
    VERY_WEAK = (0, "Very weak", "#FF4D4D",
                 "Immediate rejection. Disallowed by HIPAA/FedRAMP.")
    WEAK = (1, "Weak", "#FF944D", "Too easy to guess. Disallowed.")
    MEDIUM = (2, "Medium", "#FFC107", "Too short or predictable for FedRAMP.")
    STRONG = (3, "Strong", "#4CAF50",
              "Meets the minimum security requirements.")
    VERY_STRONG = (4, "Very strong", "#2E7D32",
                   "Recommended password strength by HIPAA/FedRAMP.")

    def __init__(self, score, label, color, description):
        self.score = score
        self.label = label
        self.color = color
        self.description = description

    @classmethod
    def from_score(cls, score):
        for strength in cls:
            if strength.score == score:
                return strength
        return cls.VERY_WEAK

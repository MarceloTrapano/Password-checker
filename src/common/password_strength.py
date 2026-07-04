from enum import Enum
from typing import Self

from src.common.logger import password_logger

logger = password_logger(__name__)


SATISFACTION_SCORE: int = 3


class PasswordStrength(Enum):
    """Password strength enumeration representing HIPAA/FedRAMP compliance levels."""
    VERY_WEAK = (0, "Very weak", "#FF4D4D",
                 "Immediate rejection. Disallowed by HIPAA/FedRAMP.")
    WEAK = (
        1, "Weak", "#FF944D", "Too easy to guess. Disallowed.")
    MEDIUM = (
        2, "Medium", "#FFC107", "Too short or predictable for FedRAMP.")
    STRONG = (3, "Strong", "#4CAF50",
              "Meets the minimum security requirements.")
    VERY_STRONG = (4, "Very strong", "#2E7D32",
                   "Recommended password strength by HIPAA/FedRAMP.")

    def __init__(self, score: int, label: str, color: str, description: str) -> None:
        """Initialize the password strength enumeration value.

        Args:
            score (int): password score [0-4].
            label (str): label connected with score.
            color (str): color for frontend.
            description (str): description of state.
        """
        self.score = score
        self.label = label
        self.color = color
        self.description = description
        self.is_compliant: bool = self.score >= SATISFACTION_SCORE

    @classmethod
    def from_score(cls, score: int) -> Self:
        """Extract the enumeration value matching a specific integer score.

        Args:
            score (int): input score value from correct range [0-4].

        Raises:
            ValueError: incorrect score was passed.

        Returns:
            PasswordStrength: the matching enumeration instance.
        """
        for strength in cls:
            if strength.score == score:
                return strength
        logger.error("Incorrect score")
        raise ValueError("Incorrect score.")

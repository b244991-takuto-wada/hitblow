"""HIGH / LOW アイテム"""

LOW = {"0", "1", "2", "3", "4"}
HIGH = {"5", "6", "7", "8", "9"}


def high_low(secret):
    """
    secret="295"
    ↓
    "LOW HIGH HIGH"
    """
    result = []

    for digit in secret:
        if digit in LOW:
            result.append("LOW")
        else:
            result.append("HIGH")

    return " ".join(result)
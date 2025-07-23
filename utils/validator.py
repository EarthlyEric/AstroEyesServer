import re

def validate_password_strength(password: str) -> str:
    """
    Validates the strength of a password.
    Parameters:
        password: The password to validate.
    Returns:
        The validated password if it meets the strength requirements.
    Raises:
        ValueError: If the password does not meet the strength requirements.
    """
    if len(password) < 8 or len(password) > 128:
        raise ValueError("Password must be 8-128 characters")
    if not re.search(r"[A-Z]", password):
        raise ValueError("Must contain an uppercase letter")
    if not re.search(r"[a-z]", password):
        raise ValueError("Must contain a lowercase letter")
    if not re.search(r"[0-9]", password):
        raise ValueError("Must contain a digit")
    if not re.search(r"[!@#\$%\^&\*\(\)_\-\+=\{\}\[\]:;\"'<>,\.\?/\\|]", password):
        raise ValueError("Must contain a special character")
    
    return password
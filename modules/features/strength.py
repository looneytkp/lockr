import re

def password_strength_feedback(pwd):
    reasons = []

    # Check minimum length
    if len(pwd) < 8:
        reasons.append("Too short")

    # Check for lowercase letter
    if not re.search(r'[a-z]', pwd):
        reasons.append("No lowercase letter")

    # Check for uppercase letter
    if not re.search(r'[A-Z]', pwd):
        reasons.append("No uppercase letter")

    # Check for digit
    if not re.search(r'\d', pwd):
        reasons.append("No digit")

    # Check for special symbol
    if not re.search(r'[!@#$%^&*_+\-=]', pwd):
        reasons.append("No symbol")

    # Check for low character variety (<=3 unique chars)
    if len(set(pwd)) <= 3:
        reasons.append("Too repetitive/similar characters")

    # Check against common weak passwords
    common = {"password", "123456", "qwerty", "letmein", "admin"}
    if pwd.lower() in common:
        reasons.append("Common password")

    return reasons
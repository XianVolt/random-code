import re

def check_password(password):
    score = 0

    if len(password) >= 8:
        score += 1

    if re.search(r"[A-Z]", password):
        score += 1

    if re.search(r"[a-z]", password):
        score += 1

    if re.search(r"[0-9]", password):
        score += 1

    if re.search(r"[^A-Za-z0-9]", password):
        score += 1

    print("\n===== SECURITY REPORT =====")

    if score <= 2:
        print("Strength: WEAK")
    elif score <= 4:
        print("Strength: MEDIUM")
    else:
        print("Strength: STRONG")

    print(f"Score: {score}/5")

    if len(password) < 8:
        print("- Use at least 8 characters.")
    if not re.search(r"[A-Z]", password):
        print("- Add an uppercase letter.")
    if not re.search(r"[a-z]", password):
        print("- Add a lowercase letter.")
    if not re.search(r"[0-9]", password):
        print("- Add a number.")
    if not re.search(r"[^A-Za-z0-9]", password):
        print("- Add a special character.")

    print("===========================")


print("==============================")
print("    XIANVOLT SECURITY CHECKER")
print("==============================")

password = input("Enter a test password: ")
check_password(password)

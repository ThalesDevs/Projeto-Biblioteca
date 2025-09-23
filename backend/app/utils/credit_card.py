
import re
from datetime import datetime

def luhn_check(card_number: str) -> bool:
    digits = [int(d) for d in re.sub(r"\D", "", card_number)]
    if not digits:
        return False
    checksum = 0
    parity = (len(digits) - 2) % 2
    for i, d in enumerate(digits[::-1]):
        if i % 2 == 1:
            d *= 2
            if d > 9:
                d -= 9
        checksum += d
    return checksum % 10 == 0

def sanitize_card(card_number: str) -> str:
    return re.sub(r"\D", "", card_number)

def mask_card(card_number: str) -> str:
    s = sanitize_card(card_number)
    if len(s) < 4:
        return "****"
    return "**** **** **** " + s[-4:]

def validate_expiry(mm_yy: str) -> bool:
    m = re.match(r"^(0[1-9]|1[0-2])\/(\d{2})$", mm_yy)
    if not m:
        return False
    month = int(m.group(1))
    year = 2000 + int(m.group(2))
    now = datetime.utcnow()
    # Consider valid through end of month
    return (year > now.year) or (year == now.year and month >= now.month)

def validate_cvv(cvv: str) -> bool:
    return bool(re.fullmatch(r"\d{3,4}", cvv))

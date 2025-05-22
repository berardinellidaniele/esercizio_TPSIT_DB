import re

def valida_stringa(val, maxlen=50):
    if val is None:
        raise ValueError("valore None non ammesso")

    val = str(val).strip()
    if not val:
        raise ValueError("stringa vuota non ammessa")

    if len(val) > maxlen:
        raise ValueError(f"stringa troppo lunga: {len(val)} > {maxlen}")

    if not re.match(r"^[a-zA-Z0-9\s'-]+$", val):
        raise ValueError(f"stringa contiene caratteri non validi: {val}")

    return val
def valida_integer(val, minval=1, maxval=1000):
    n = int(val)
    if n < minval or n > maxval:
        raise ValueError(f"valore intero fuori range: {n}")
    return n

def valida_float(val, minval=0.01, maxval=99999):
    f = float(val)
    if f < minval or f > maxval:
        raise ValueError(f"valore float fuori range: {f}")
    return round(f, 2)

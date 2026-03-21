"""
PayTM Checksum utilities.
Requires: pip install pycryptodome
"""
import base64
import hashlib
import random
import string

from Crypto.Cipher import AES

_IV = "@@@@&&&&####$$$$"
_BLOCK_SIZE = 16


# ── Public API ─────────────────────────────────────────────────────────────────

def generate_checksum(param_dict: dict, merchant_key: str, salt: str = None) -> str:
    """Generate a PayTM checksum hash for the given parameters."""
    params_string = _get_param_string(param_dict)
    salt = salt or _id_generator(4)
    final_string = f'{params_string}|{salt}'
    hash_string = hashlib.sha256(final_string.encode()).hexdigest() + salt
    return _encode(hash_string, _IV, merchant_key)


def generate_checksum_by_str(param_str: str, merchant_key: str, salt: str = None) -> str:
    salt = salt or _id_generator(4)
    final_string = f'{param_str}|{salt}'
    hash_string = hashlib.sha256(final_string.encode()).hexdigest() + salt
    return _encode(hash_string, _IV, merchant_key)


def verify_checksum(param_dict: dict, merchant_key: str, checksum: str) -> bool:
    """Verify a PayTM checksum. Returns True if valid."""
    if not checksum:
        return False
    params = {k: v for k, v in param_dict.items() if k != 'CHECKSUMHASH'}
    try:
        paytm_hash = _decode(checksum, _IV, merchant_key)
        salt = paytm_hash[-4:]
    except Exception:
        return False
    return generate_checksum(params, merchant_key, salt=salt) == checksum


def verify_checksum_by_str(param_str: str, merchant_key: str, checksum: str) -> bool:
    if not checksum:
        return False
    try:
        paytm_hash = _decode(checksum, _IV, merchant_key)
        salt = paytm_hash[-4:]
    except Exception:
        return False
    return generate_checksum_by_str(param_str, merchant_key, salt=salt) == checksum


def generate_refund_checksum(param_dict: dict, merchant_key: str, salt: str = None) -> str:
    """Generate checksum for a refund request (rejects values containing '|')."""
    for v in param_dict.values():
        if '|' in v:
            raise ValueError("Refund param values must not contain '|'")
    return generate_checksum(param_dict, merchant_key, salt=salt)


# ── Internal helpers ───────────────────────────────────────────────────────────

def _id_generator(size: int = 6) -> str:
    chars = string.ascii_letters + string.digits
    return ''.join(random.choice(chars) for _ in range(size))


def _get_param_string(params: dict) -> str:
    parts = []
    for key in sorted(params.keys()):
        value = params[key]
        if '|' in str(value):
            raise ValueError(f"Parameter '{key}' must not contain '|'")
        parts.append('' if value == 'null' else str(value))
    return '|'.join(parts)


def _pad(s: str) -> str:
    pad_size = _BLOCK_SIZE - len(s) % _BLOCK_SIZE
    return s + chr(pad_size) * pad_size


def _unpad(s: str) -> str:
    return s[:-ord(s[-1])]


def _encode(to_encode: str, iv: str, key: str) -> str:
    padded = _pad(to_encode).encode('utf-8')
    cipher = AES.new(key.encode('utf-8'), AES.MODE_CBC, iv.encode('utf-8'))
    encrypted = cipher.encrypt(padded)
    return base64.b64encode(encrypted).decode('utf-8')


def _decode(to_decode: str, iv: str, key: str) -> str:
    raw = base64.b64decode(to_decode)
    cipher = AES.new(key.encode('utf-8'), AES.MODE_CBC, iv.encode('utf-8'))
    decrypted = cipher.decrypt(raw)
    if isinstance(decrypted, bytes):
        decrypted = decrypted.decode('utf-8')
    return _unpad(decrypted)

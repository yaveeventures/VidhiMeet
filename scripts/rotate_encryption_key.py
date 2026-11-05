"""
rotate_encryption_key.py
------------------------
Utility script to re-encrypt sensitive database fields (such as lawyer payout bank accounts)
from an old/compromised Fernet encryption key to a newly generated active key.

Usage:
    python -m scripts.rotate_encryption_key --old-key <OLD_KEY> --new-key <NEW_KEY> [--dry-run]
"""

import argparse
import base64
import hashlib
import os
import sys

from cryptography.fernet import Fernet
from sqlalchemy import select

# Ensure project root is in sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from backend.db import SessionLocal
from backend.models import LawyerBankAccount


def derive_fernet_key(raw_key: str) -> bytes:
    key_bytes = hashlib.sha256(raw_key.encode("utf-8")).digest()
    return base64.urlsafe_b64encode(key_bytes)


def rotate_keys(old_key: str, new_key: str, dry_run: bool = False):
    old_cipher = Fernet(derive_fernet_key(old_key))
    new_cipher = Fernet(derive_fernet_key(new_key))

    db = SessionLocal()
    try:
        accounts = db.scalars(select(LawyerBankAccount)).all()
        print(f"[*] Found {len(accounts)} bank account record(s) to verify/re-encrypt.")

        re_encrypted = 0
        for acct in accounts:
            raw_acc_enc = acct.account_number
            raw_ifsc_enc = acct.ifsc_code

            # Check and re-encrypt account number
            changed = False
            if raw_acc_enc:
                try:
                    decrypted_acc = old_cipher.decrypt(raw_acc_enc.encode("utf-8")).decode("utf-8")
                    if not dry_run:
                        acct.account_number = new_cipher.encrypt(decrypted_acc.encode("utf-8")).decode("utf-8")
                    changed = True
                except Exception:
                    pass

            if raw_ifsc_enc:
                try:
                    decrypted_ifsc = old_cipher.decrypt(raw_ifsc_enc.encode("utf-8")).decode("utf-8")
                    if not dry_run:
                        acct.ifsc_code = new_cipher.encrypt(decrypted_ifsc.encode("utf-8")).decode("utf-8")
                    changed = True
                except Exception:
                    pass

            if changed:
                re_encrypted += 1

        if not dry_run:
            db.commit()
            print(f"[+] Successfully re-encrypted {re_encrypted} bank account(s) with the new key.")
        else:
            print(f"[i] Dry run complete: {re_encrypted} bank account(s) eligible for re-encryption.")
    finally:
        db.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Rotate Fernet encryption keys for VidhiMeet database records.")
    parser.add_argument("--old-key", required=True, help="Previous (compromised) encryption key")
    parser.add_argument("--new-key", required=True, help="New secure encryption key")
    parser.add_argument("--dry-run", action="store_true", help="Preview records without committing changes")
    args = parser.parse_args()

    rotate_keys(args.old_key, args.new_key, dry_run=args.dry_run)

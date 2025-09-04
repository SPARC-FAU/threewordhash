# src/threewordhash/core.py
import hmac
import hashlib
import unicodedata
import os
import string
from typing import List

import argparse


# ---- Utilities ----
def _normalize(s: str) -> str:
    # Lowercase, strip, collapse internal whitespace, NFKC normalize
    s = unicodedata.normalize("NFKC", s.strip().lower())
    return " ".join(s.split())


def _hmac_sha256(key: bytes, msg: str) -> bytes:
    return hmac.new(key, _normalize(msg).encode("utf-8"), hashlib.sha256).digest()


def _bytes_to_indices(b: bytes, vocab_size: int, n: int) -> List[int]:
    """
    Deterministically turn bytes into n indices in [0, vocab_size).
    We consume 4 bytes at a time for a 32-bit int and mod by vocab_size.
    If we run out, we re-hash to extend the stream.
    """
    needed = n
    out = []
    pool = b
    ctr = 0
    while needed > 0:
        # consume in 4-byte chunks
        for i in range(0, len(pool), 4):
            chunk = pool[i : i + 4]
            if len(chunk) < 4:
                break
            val = int.from_bytes(chunk, "big", signed=False)
            out.append(val % vocab_size)
            needed -= 1
            if needed == 0:
                break
        if needed > 0:
            ctr += 1
            pool = hashlib.sha256(pool + ctr.to_bytes(2, "big")).digest()
    return out


def _checksum_base36(b: bytes, length: int = 2) -> str:
    """
    Short base36 checksum over the digest. Not crypto-strong (doesn't need to be);
    purely for typo detection.
    """
    num = int.from_bytes(hashlib.sha256(b).digest(), "big")
    chars = string.digits + string.ascii_uppercase
    out = ""
    for _ in range(length):
        out = chars[num % 36] + out
        num //= 36
    return out


# ---- Public API ----
def load_wordlist(path: str) -> List[str]:
    """
    Expects one word per line. Leading indices in Diceware files are OK:
    we'll read the last whitespace-separated token on each line.
    """
    vocab = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            # handle '12345\tword' or 'word'
            token = line.split()[-1]
            vocab.append(token)
    if len(vocab) < 512:
        raise ValueError(
            "Wordlist is too short. Use a larger list (e.g., EFF Diceware 7,776 words)."
        )
    # ensure uniqueness
    if len(vocab) != len(set(vocab)):
        raise ValueError("Wordlist contains duplicates.")
    return vocab


def friendly_id(
    user_input: str,
    secret_salt: str,
    wordlist: List[str],
    n_words: int = 3,
    checksum_len: int = 2,
    sep: str = "-",
) -> str:
    """
    Create a human-friendly, deterministic ID from input.
    Store ONLY the returned ID. Keep secret_salt secret.
    """
    if n_words < 2:
        raise ValueError("Use at least 2 words.")
    digest = _hmac_sha256(secret_salt.encode("utf-8"), user_input)
    idxs = _bytes_to_indices(digest, len(wordlist), n_words)
    words = [wordlist[i] for i in idxs]
    check = _checksum_base36(digest, checksum_len)
    return sep.join(words + [check] if checksum_len > 0 else words)


def create_salt_digest(byte_length: int = 32) -> str:
    return os.urandom(byte_length).hex()


def parse_args():
    argparser = argparse.ArgumentParser(
        description="Three-Word Hash: Generate and verify human-friendly IDs."
    )

    argparser.add_argument(
        "-w",
        "--wordlist",
        type=str,
        help="Path to wordlist file",
        default="wordlist/eff_large_wordlist.txt",
    )

    argparser.add_argument(
        "-s",
        "--salt",
        type=str,
        help="Secret salt",
        default=None,
    )

    argparser.add_argument(
        "--salt-size",
        type=int,
        help="Salt size in bytes (default: 32). Only relevant if salt is auto-generated.",
        default=32,
    )

    argparser.add_argument(
        "-i",
        "--input",
        type=str,
        action="append",
        help="Input strings (e.g., names or emails)",
    )

    argparser.add_argument(
        "-n",
        "--nwords",
        type=int,
        help="Number of words in ID (default: 3)",
        default=3,
    )

    argparser.add_argument(
        "-c",
        "--checksum",
        type=int,
        help="Checksum length (default: 2)",
        default=2,
    )

    args = argparser.parse_args()

    return args


def main():
    args = parse_args()

    if args.wordlist is None or not os.path.isfile(args.wordlist):
        print("Please provide a valid path to a wordlist file.")
        return

    if args.salt is None:
        # create a random salt
        args.salt = create_salt_digest(args.salt_size)
        print("Generated random salt:", args.salt)

    wordlist = load_wordlist(args.wordlist)
    for ipt in args.input or []:
        pid = friendly_id(
            ipt,
            args.salt,
            wordlist,
            args.nwords,
            args.checksum,
        )
        print(f"{ipt} -> {pid}")

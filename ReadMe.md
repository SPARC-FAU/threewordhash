# threewordhash

Small utility to generate a human‑readable, what3words‑style **three‑word hash** from arbitrary input.

> ⚠️ **Not for cryptography.** Three‑word hashes are for human‑friendly IDs and quick references, not security!

---

## Why?

Identifiers like `a6f9c2…` are great for machines and terrible for brains. A short phrase such as `"orbit.coffee.novel"` is easier to use when working with humans, like on a call, or type without confusion. This project turns any input string (or bytes) into such a phrase using a fixed word list and a deterministic mapping.

Inspired by *what3words* (three‑word addressing).

---

## Installation

This package isn’t published on PyPI (yet). Install from source:

```bash
# Clone
git clone https://github.com/SPARC-FAU/threewordhash
cd threewordhash

# Create a virtual environment (recommended)
python -m venv .venv
source .venv/bin/activate   # on Windows: .venv\Scripts\activate

# Install
pip install -e .

# Or with GUI
pip install -e .[gui]
```

> If you prefer not to use `-e`, replace with `pip install .`.

---

## Quick start

The simplest use-case is from cli, simply pass in a set of inputs and get three words:
```bash
twh -i ... -i ...
```
If you want to have spaces in your input, remember to quote it:
```bash
twh -i "John Doe" -i supercalifragilistic -i "Lorem ipsum dolor sit amet"
```

If you prefer a GUI, install the project with the GUI dependencies and run
```bash
twh_gui
```

--- 

## Argument options
The following set of arguments/options work on both the GUI and cli version, with the exception of the `-i/--input` paramter (only for cli).

- `-i/--input`: Input to encode. Can be given 0+ times, each token is encoded individually. Remeber to quote strings with spaces so that they are treated as a single token!
- `-w/--wordlist`: Path to the wordlist file. Defaults to `eff_large_wordlist`.
- `-s/--salt`: The secret salt added to the encoding. This prevents reverse engineering based on common names/inputs. If not specified (default), a custom salt will be generated and printed. If set, the GUI will disable modifications or reading the salt.
- `--salt-size`: The size of the salt in bytes. Defaults to 32. This is only relevant if the salt is to be generated.
- `-n/--nwords`: The number of words to be generated. Defaults to 3
- `-c/--checksum`: The length of the checksum. If set, a checksum is appended to the generated words of the given length. Defaults to 2.

---

## Code usage
Here is a minimal sample of how to use threewordhash:
```python

from threewordhash.core import load_wordlist, friendly_id, create_salt_digest

...

words = friendly_id(
	"my super awesome input",
	secret_salt = create_salt_digest(32),	# The '32' is optional
	wordlist = load_wordlist("path to the wordlist")
	n_words = 3,		# Optional
	checksum_len = 2,	# Optional
	sep = "-",			# Optional
)

...
```

Please note: I have created this library primarily for me and ease-of-use as a cli/gui tool.
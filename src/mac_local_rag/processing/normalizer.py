
import re
import unicodedata


def normalize_text(text: str) -> str:
    # Normalize Unicode representations
    text = unicodedata.normalize("NFC", text)

    # Standardize line endings
    text = text.replace("\r\n", "\n").replace("\r", "\n")

    # Replace non-breaking spaces
    text = text.replace("\u00a0", " ")

    # Remove trailing spaces from each line
    text = "\n".join(
        line.rstrip() for line in text.split("\n")
    )

    # Limit excessive blank lines
    text = re.sub(r"\n{3,}", "\n\n", text)

    return text.strip()

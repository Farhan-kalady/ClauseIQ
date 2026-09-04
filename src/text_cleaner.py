import re


def clean_text(text: str) -> str:
    """Clean and normalize contract clause text.
    
    Steps:
    1. Check for valid string input
    2. Lowercase text
    3. Remove URLs
    4. Remove email addresses
    5. Strip unusual symbols while keeping basic punctuation
    6. Normalize whitespace
    """
    if not isinstance(text, str):
        return ""

    text = text.lower()
    text = re.sub(r"https?://\S+|www\.\S+", " ", text)       # remove URLs
    text = re.sub(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b", " ", text)  # remove emails
    text = re.sub(r"[^a-z0-9.,;:()\- ]", " ", text)          # strip weird characters, keep basic punctuation
    text = re.sub(r"\s+", " ", text)                         # collapse multiple whitespaces
    return text.strip()


if __name__ == "__main__":
    sample = "This   Agreement   shall be governed by the laws of Delaware! Contact legal@example.com or visit https://example.com/terms."
    print("Raw sample:")
    print(sample)
    print("\nCleaned sample:")
    print(clean_text(sample))
import re
from unidecode import unidecode

def clean_slug(text):
    """Convert any string to a clean slug"""
    # Transliterate non-ASCII characters to ASCII equivalents
    text = unidecode(text)
    # Convert to lowercase
    text = text.lower()
    # Replace spaces and special characters with hyphens
    text = re.sub(r'[^\w\s-]', '', text)
    text = re.sub(r'[-\s]+', '-', text.strip())
    return text
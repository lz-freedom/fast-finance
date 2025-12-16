import re

def to_camel_case(text: str) -> str:
    """
    Convert string from 'Title Case', 'Snake_Case' or 'Space Separated' to 'camelCase'.
    Examples:
        "Total Assets" -> "totalAssets"
        "Free_Cash_Flow" -> "freeCashFlow"
    """
    # Remove special chars but keep spaces/underscores for splitting
    s = re.sub(r"[^a-zA-Z0-9\s_]", "", text)
    
    # Split by space or underscore
    words = re.split(r"[\s_]+", s)
    words = [w for w in words if w]
    
    if not words:
        return text.lower() # Fallback

    # First word lowercase, others capitalized
    return words[0].lower() + "".join(w.capitalize() for w in words[1:])

def recursive_camel_case(data: any) -> any:
    """
    Recursively transform all dictionary keys in the data to camelCase.
    """
    if isinstance(data, dict):
        return {to_camel_case(k): recursive_camel_case(v) for k, v in data.items()}
    if isinstance(data, list):
        return [recursive_camel_case(item) for item in data]
    return data

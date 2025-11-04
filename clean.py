import ast
import re

def extract_match_dicts(text_blob):
    """
    Extracts valid match dictionaries from a mixed log + data string.
    Returns a list of cleaned dictionaries.
    """
    # Match any top-level dictionary using regex
    dict_pattern = re.compile(r"\{.*?\}(?=\n|\Z)", re.DOTALL)
    matches = dict_pattern.findall(text_blob)

    cleaned = []
    for raw in matches:
        try:
            parsed = ast.literal_eval(raw)
            if isinstance(parsed, dict) and "league" in parsed and "hometeam" in parsed:
                cleaned.append(parsed)
        except (ValueError, SyntaxError):
            continue  # Skip malformed entries

    return cleaned

# 🧪 Example usage
with open("sample.txt", "r" ,encoding='utf-8') as f:
    if f is None:
        raise ValueError("File not found or could not be opened.")
    raw_text = f.read()

match_data = extract_match_dicts(raw_text)
with open("cleaned_matches.txt", "w", encoding='utf-8') as f:
    for match in match_data:
        f.write(f"{match}\n")
for match in match_data:
    print(match)

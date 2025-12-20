import random
import re
from copy import deepcopy
import os
import string

# ------------------------------------------------------------
# Utility functions
# ------------------------------------------------------------

def split_paragraphs(text):
    return [p for p in text.split("\n\n") if p.strip()]


def split_sentences(text):
    return re.split(r'(?<=[.;])\s+', text)


def split_words(text):
    return re.findall(r'\b\w+\b', text)


# ------------------------------------------------------------
# 1. Entity Drift (name inconsistency)
# ------------------------------------------------------------

def drift_entities(text, probability=0.3):
    entities = list(set(re.findall(r'\b[A-Z][a-zA-Z& ]{3,}\b', text)))
    if not entities:
        return text

    text_copy = text
    sample_size = max(1, int(len(entities) * probability))
    selected = random.sample(entities, min(sample_size, len(entities)))

    for ent in selected:
        mutated = ent + " Holdings" if random.random() < 0.5 else ent.replace(" ", "")
        text_copy = text_copy.replace(ent, mutated, 1)

    return text_copy


# ------------------------------------------------------------
# 2. Section Reference Corruption
# ------------------------------------------------------------

def corrupt_references(text, probability=0.25):
    refs = re.findall(r'Section\s+\d+(\.\d+)*', text)
    if not refs:
        return text

    for ref in refs:
        if random.random() < probability:
            fake_ref = f"Section {random.randint(20,99)}.{random.randint(1,9)}"
            text = text.replace(ref, fake_ref, 1)

    return text


# ------------------------------------------------------------
# 3. Clause Boundary Distortion
# ------------------------------------------------------------

def distort_clause_boundaries(text):
    paragraphs = split_paragraphs(text)
    if len(paragraphs) < 3:
        return text

    idx = random.randint(0, len(paragraphs) - 2)
    paragraphs[idx] += " " + paragraphs[idx + 1]
    del paragraphs[idx + 1]

    return "\n\n".join(paragraphs)


# ------------------------------------------------------------
# 4. Temporal Inconsistency
# ------------------------------------------------------------

def temporal_inconsistency(text):
    date_patterns = [
        r'\b\d{1,2}\s+[A-Z][a-z]+\s+\d{4}\b',
        r'\b\d{4}-\d{2}-\d{2}\b'
    ]

    dates = []
    for pattern in date_patterns:
        dates.extend(re.findall(pattern, text))

    if len(dates) < 2:
        return text

    d1, d2 = random.sample(dates, 2)
    return text.replace(d1, d2, 1)


# ------------------------------------------------------------
# 5. Style Drift
# ------------------------------------------------------------

def style_drift(text, probability=0.3):
    sentences = split_sentences(text)

    for i in range(len(sentences)):
        if random.random() < probability:
            sentences[i] = sentences[i].capitalize()
            if random.random() < 0.5:
                sentences[i] = sentences[i].replace(",", "")
            if random.random() < 0.3:
                sentences[i] = sentences[i].replace(";", ".")

    return " ".join(sentences)


# ------------------------------------------------------------
# 6. Semantic Dropout
# ------------------------------------------------------------

def semantic_dropout(text, probability=0.15):
    paragraphs = split_paragraphs(text)
    if len(paragraphs) < 4:
        return text

    retained = [p for p in paragraphs if random.random() > probability]
    if len(retained) < 2:
        return text

    return "\n\n".join(retained)


# ------------------------------------------------------------
# 7. Logical order disturbance (Refined: swap_sections)
# ------------------------------------------------------------

def swap_sections(text):
    """
    Identifies major sections (e.g. SECTION 1, Article II) and swaps two of them.
    """
    # Pattern for common section headers
    section_pattern = r'\n\n(?P<header>(?:SECTION|ARTICLE|Clause)\s+[0-9A-Z\.]+)\b'
    sections = list(re.finditer(section_pattern, text, re.IGNORECASE))
    
    if len(sections) < 3:
        return text

    # Pick two sections to swap
    idx1, idx2 = sorted(random.sample(range(len(sections) - 1), 2))
    
    start1 = sections[idx1].start()
    end1 = sections[idx1+1].start()
    
    start2 = sections[idx2].start()
    end2 = sections[idx2+1].start() if idx2 + 1 < len(sections) else len(text)
    
    sec1_content = text[start1:end1]
    sec2_content = text[start2:end2]
    
    # Reconstruct text
    new_text = (
        text[:start1]
        + sec2_content
        + text[end1:start2]
        + sec1_content
        + text[end2:]
    )
    return new_text


# ------------------------------------------------------------
# 8. Smart Referential Integrity
# ------------------------------------------------------------

def smart_corrupt_references(text, probability=0.4):
    """
    Finds existing section numbers and points references to the WRONG ones.
    """
    # Find all potential section numbers in headers
    headers = re.findall(r'(?:SECTION|ARTICLE|Section|Article)\s+(?P<num>[0-9A-Z\.]+)', text)
    if len(headers) < 2:
        return corrupt_references(text, probability) # Fallback

    # Find references like "Section 5" or "Article II"
    ref_pattern = r'(?P<prefix>Section|Article)\s+(?P<num>[0-9A-Z\.]+)'
    
    def mutate_ref(match):
        if random.random() < probability:
            wrong_num = random.choice([h for h in headers if h != match.group('num')] or headers)
            return f"{match.group('prefix')} {wrong_num}"
        return match.group(0)

    return re.sub(ref_pattern, mutate_ref, text)


# ------------------------------------------------------------
# 9. Jurisdictional Conflict
# ------------------------------------------------------------

def jurisdictional_conflict(text):
    """
    Introduces conflicting laws/venues.
    """
    jurisdictions = [
        "Delaware", "New York", "California", "Texas", "Florida",
        "England and Wales", "Singapore", "Japan", "Hong Kong", "Ontario"
    ]
    
    # Find existing jurisdictions
    found = [j for j in jurisdictions if j in text]
    
    if not found:
        # If none found, look for common patterns like "laws of [State]"
        pattern = r'laws of (?:the State of )?(?P<state>[A-Z][a-z]+)'
        match = re.search(pattern, text)
        if match:
            fake_juri = random.choice([j for j in jurisdictions if j != match.group('state')])
            return text.replace(match.group('state'), fake_juri, 1)
        return text

    # Swap one found jurisdiction with a conflicting one
    target = random.choice(found)
    fake_juri = random.choice([j for j in jurisdictions if j != target])
    
    # Only replace one instance to create the conflict
    return text.replace(target, fake_juri, 1)


# ------------------------------------------------------------
# 10. Definition Drift
# ------------------------------------------------------------

def definition_drift(text):
    """
    Finds a defined term in quotes and changes its meaning or name later.
    """
    # Find terms like ("Term") or "Term"
    defs = re.findall(r'["\'](?P<term>[A-Z][a-zA-Z ]+)["\']', text)
    # Filter for multi-word or capitalized terms likely to be definitions
    defs = [d for d in defs if len(d.split()) <= 4 and d[0].isupper()]
    
    if not defs:
        return text
    
    target_def = random.choice(defs)
    # Find occurrences after the first one (which is usually the definition)
    occurrences = list(re.finditer(rf'\b{re.escape(target_def)}\b', text))
    
    if len(occurrences) < 2:
        return text
    
    # Mutate a random later occurrence
    idx = random.randint(1, len(occurrences) - 1)
    match = occurrences[idx]
    
    mutations = [
        target_def + "s", # pluralize
        target_def.replace(" ", ""), # remove space
        "Gross " + target_def if "Net" in target_def else "Net " + target_def,
        target_def.split()[0] # shorten
    ]
    mutated = random.choice(mutations)
    
    return text[:match.start()] + mutated + text[match.end():]


# ------------------------------------------------------------
# 11. Financial Discrepancy
# ------------------------------------------------------------

def financial_discrepancy(text):
    """
    Mutates dollar amounts slightly.
    """
    # Regex for $1,000.00 or $1000
    money_pattern = r'\$(?P<amt>\d{1,3}(?:,\d{3})*(?:\.\d{2})?)'
    matches = list(re.finditer(money_pattern, text))
    
    if not matches:
        return text
    
    # Pick a random amount to mutate
    match = random.choice(matches)
    original_amt = match.group('amt')
    
    # Remove commas for math
    num_str = original_amt.replace(',', '')
    try:
        val = float(num_str)
        # Mutate: +/- 1, +/- 10%, or swap a digit
        mutation_type = random.choice(["offset", "percent", "digit"])
        if mutation_type == "offset":
            new_val = val + random.choice([-100, -10, 1, 10, 100])
        elif mutation_type == "percent":
            new_val = val * random.choice([0.9, 1.1, 1.01])
        else:
            # digit swap
            s = list(num_str)
            idx = random.randint(0, len(s)-1)
            if s[idx].isdigit():
                s[idx] = str((int(s[idx]) + 1) % 10)
            new_val = float("".join(s))
            
        new_amt = f"{new_val:,.2f}" if '.' in original_amt else f"{int(new_val):,}"
        return text[:match.start()] + "$" + new_amt + text[match.end():]
    except:
        return text


# ------------------------------------------------------------
# 12. Notice Inconsistency
# ------------------------------------------------------------

def notice_inconsistency(text):
    """
    Alters address or recipient in the "Notices" section.
    """
    # Find "Notices" or "Addresses" section
    notice_pattern = r'(?i)(?:Section|Article)?\s*(?:\d+\.)?\s*(?:NOTICES|ADDRESSES)(?P<content>.*?)(?:\n\n|\Z)'
    match = re.search(notice_pattern, text, re.DOTALL)
    
    if not match:
        return text
    
    content = match.group('content')
    # Look for zip codes, fax numbers, or "Attn:"
    mutations = [
        (r'\b\d{5}\b', lambda m: str(random.randint(10000, 99999))), # Zip
        (r'Attn:\s*[A-Z][a-z]+ [A-Z][a-z]+', "Attn: John Doe"), # Recipient
        (r'Fax:\s*[\d-]+', "Fax: 555-0199"), # Fax
        (r'\b[A-Z]{2}\s+\d{5}\b', "NY 10001") # State + Zip
    ]
    
    for pattern, replacement in mutations:
        if re.search(pattern, content):
            new_content = re.sub(pattern, replacement, content, count=1)
            return text.replace(content, new_content, 1)
            
    return text


# ------------------------------------------------------------
# 13. Typo Injection
# ------------------------------------------------------------

def inject_typos(text, probability=0.02):
    """
    Introduces subtle human-like typos.
    """
    words = text.split()
    for i in range(len(words)):
        if random.random() > probability:
            continue

        word = words[i]
        if len(word) < 4 or not word.isalpha():
            continue

        typo_type = random.choice(["delete", "duplicate", "swap"])
        idx = random.randint(1, len(word) - 2)

        if typo_type == "delete":
            word = word[:idx] + word[idx+1:]
        elif typo_type == "duplicate":
            word = word[:idx] + word[idx] + word[idx:]
        elif typo_type == "swap":
            word = word[:idx] + word[idx+1] + word[idx] + word[idx+2:]

        words[i] = word

    return " ".join(words)


# ------------------------------------------------------------
# Master Fake Generator
# ------------------------------------------------------------

def generate_fake_contract(real_text, difficulty="medium"):
    """
    Applies a RANDOM SUBSET (1–4) of transforms to generate a fake.
    """

    transform_pool = [
        drift_entities,
        smart_corrupt_references,   # Upgraded
        distort_clause_boundaries,
        temporal_inconsistency,
        style_drift,
        semantic_dropout,
        swap_sections,              # Upgraded
        jurisdictional_conflict,    # NEW
        definition_drift,           # NEW
        financial_discrepancy,      # NEW
        notice_inconsistency,       # NEW
        inject_typos
    ]

    num_transforms = random.randint(1, 4)
    selected_transforms = random.sample(transform_pool, num_transforms)

    difficulty_strength = {
        "easy": 0.4,
        "medium": 0.65,
        "hard": 0.85
    }
    strength = difficulty_strength.get(difficulty, 0.65)

    text = deepcopy(real_text)

    for transform in selected_transforms:
        if random.random() < strength:
            text = transform(text)

    return text


# ------------------------------------------------------------
# Folder Processing (1 fake per file)
# ------------------------------------------------------------

def process_folder(folder_path, difficulty="medium"):
    for filename in os.listdir(folder_path):
        if not filename.lower().endswith(".txt"):
            continue
        file_path = os.path.join(folder_path, filename)
        with open(file_path, "r", encoding="utf-8") as f:
            original_text = f.read()
        fake_text = generate_fake_contract(original_text, difficulty)
        # Overwrite the original file
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(fake_text)
        print(f"{filename} → overwritten with fake content")

# ------------------------------------------------------------
# Usage
# ------------------------------------------------------------

if __name__ == "__main__":
    folder = "fake_data"
    process_folder(folder_path=folder, difficulty="medium")

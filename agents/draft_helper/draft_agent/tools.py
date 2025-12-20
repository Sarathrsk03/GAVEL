#from thefuzz import fuzz
import os
import glob
from typing import Optional, Dict
from fuzzywuzzy import fuzz 
import pypandoc
import os
import base64



def contracts_agreements(domain: str) -> Optional[Dict]:
    """
    This tool is responsible for retrieving templates for contractual agreements only.
    It supports commercial and legal contracts such as Non-Disclosure Agreements (NDAs),
    Affiliate Agreements, Co-Branding Agreements, Joint Venture Agreements, and similar contracts.

    The tool identifies the most relevant contract template by applying fuzzy matching
    against the available template file names and their contents based on the provided domain.

    Args:
        domain (str): A user-provided description or name of the contract type
                    (e.g., "Affiliate Agreement", "Co-Branding Agreement").

    Returns:
        Optional[Dict]: A dictionary containing the matched contract template content
                        if a suitable template is found; otherwise, None.
    """

    # Directory where your contract template markdown files are stored
    CONTRACT_TEMPLATES_DIR = "contract_templates"
    # File extension for the templates
    TEMPLATE_EXTENSION = ".md"
    # 1. Normalize the domain string for consistent matching
    domain_normalized = domain.lower().replace("-", " ")

    # This structure is for mapping simplified names to file patterns (e.g. for Master Service Agreement.md)
    template_name_to_keywords = {
        "Affiliate Agreement": ["affiliate agreement", "confidentiality"],
        "Co-branding Agreement": ["co-branding agreement", "co-branding"],
        "Joint Venture Agreement": ["joint venture agreement", "joint venture"],
    }

    best_match_score = -1
    best_match_content = None
    
    # Use glob to find all markdown files in the specified directory
    template_files = glob.glob(os.path.join(CONTRACT_TEMPLATES_DIR, f"*{TEMPLATE_EXTENSION}"))

    # If no templates are found, return None
    if not template_files:
        print(f"Warning: No files found in '{CONTRACT_TEMPLATES_DIR}'.")
        return None

    for file_path in template_files:
        # Get the simple file name without extension
        file_name = os.path.basename(file_path).removesuffix(TEMPLATE_EXTENSION).lower().replace("_", " ").strip()

        try:
            # 2. Read the file content
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            content_normalized = content.lower()
        except Exception as e:
            print(f"Error reading file {file_path}: {e}")
            continue

        # --- Scoring Logic ---
        
        # A. File Name Match Score (Prioritize a good name match)
        # Check if the domain is a good partial match to the file name itself
        name_match_score = fuzz.partial_ratio(file_name, domain_normalized)

        # B. Content Match Score (How much the template's content relates to the domain)
        # We'll use Token Set Ratio, which is great for comparing strings where word order is shuffled.
        # This checks for the *presence* of domain keywords in the contract text.
        content_domain_score = fuzz.token_set_ratio(domain_normalized, content_normalized)

        # C. Keyword Reinforcement Score (Reinforce based on standard contract names present in content)
        keyword_score = 0
        for simple_name, keywords in template_name_to_keywords.items():
            # If the file name is close to a standard name, or if the content contains the keywords
            if simple_name in file_name or any(k in content_normalized for k in keywords):
                # A successful simple name match adds a bonus to the score
                keyword_score = 10 
                break # Only need one keyword match for the bonus

        # 3. Combine scores to get a Final Match Score
        # Weight the name and content scores, and add the keyword bonus.
        # Example weighting: 40% Name Match, 50% Content Match, 10% Keyword Bonus
        final_score = (0.40 * name_match_score) + (0.50 * content_domain_score) + keyword_score

        print(f"Template: {file_name} | Final Score: {final_score:.2f} (Name: {name_match_score}, Content: {content_domain_score})")

        # 4. Update the best match
        if final_score > best_match_score:
            best_match_score = final_score
            best_match_content = content

    # Set a minimum threshold for returning a result
    MATCH_THRESHOLD = 65 
    if best_match_score >= MATCH_THRESHOLD:
        return {
            "contract": best_match_content
        }
    else:
        return None



def criminal_litigation(domain: str) -> Optional[Dict]:
    """
    This tool is responsible for retrieving templates for criminal litigation documents only.
    It supports documents such as FIRs, bail applications, bail bonds, surety bonds,
    charge sheets, sentencing-related documents, and similar criminal procedure forms.

    The tool identifies the most relevant criminal litigation template by applying
    fuzzy matching against the available template file names and their contents
    based on the provided domain.

    Args:
        domain (str): A user-provided description or name of the criminal document
                      (e.g., "Bail Application", "FIR", "Surety Bond").

    Returns:
        Optional[Dict]: A dictionary containing the matched template content
                        if a suitable template is found; otherwise, None.
    """

    # Directory where criminal litigation templates are stored
    CRIMINAL_TEMPLATES_DIR = "criminal_litigation_templates"
    TEMPLATE_EXTENSION = ".md"

    # 1. Normalize domain input
    domain_normalized = domain.lower().replace("-", " ").strip()

    # Mapping of standard criminal document names to keywords
    template_name_to_keywords = {
        "FIR": ["first information report", "fir", "complaint"],
        "Bail Application": ["bail application", "anticipatory bail", "regular bail"],
        "Bail Bond": ["bail bond", "personal bond"],
        "Surety Bond": ["surety", "surety bond"],
        "Charge Sheet": ["charge sheet", "chargesheet", "final report"],
        "Sentencing Application": ["sentencing", "sentence", "punishment"],
    }

    best_match_score = -1
    best_match_content = None

    # Find all markdown templates
    template_files = glob.glob(
        os.path.join(CRIMINAL_TEMPLATES_DIR, f"*{TEMPLATE_EXTENSION}")
    )

    if not template_files:
        print(f"Warning: No files found in '{CRIMINAL_TEMPLATES_DIR}'.")
        return None

    for file_path in template_files:
        file_name = (
            os.path.basename(file_path)
            .removesuffix(TEMPLATE_EXTENSION)
            .lower()
            .replace("_", " ")
            .strip()
        )

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
            content_normalized = content.lower()
        except Exception as e:
            print(f"Error reading file {file_path}: {e}")
            continue

        # ----------------------------
        # Scoring Logic
        # ----------------------------

        # A. File name similarity
        name_match_score = fuzz.partial_ratio(file_name, domain_normalized)

        # B. Content relevance
        content_match_score = fuzz.token_set_ratio(
            domain_normalized, content_normalized
        )

        # C. Keyword reinforcement
        keyword_score = 0
        for standard_name, keywords in template_name_to_keywords.items():
            if (
                standard_name.lower() in file_name
                or any(k in content_normalized for k in keywords)
            ):
                keyword_score = 10
                break

        # Final weighted score
        final_score = (
            0.40 * name_match_score
            + 0.50 * content_match_score
            + keyword_score
        )

        print(
            f"Template: {file_name} | Final Score: {final_score:.2f} "
            f"(Name: {name_match_score}, Content: {content_match_score})"
        )

        if final_score > best_match_score:
            best_match_score = final_score
            best_match_content = content

    # Minimum confidence threshold
    MATCH_THRESHOLD = 65

    if best_match_score >= MATCH_THRESHOLD:
        return {
            "criminal_document": best_match_content
        }

    return None



def civil_litigation(domain: str) -> Optional[Dict]:
    """
    This tool is responsible for retrieving templates for civil litigation documents only.
    It supports procedural and filing-related civil court documents such as address forms,
    vakalatnamas, memo of appearance, inspection forms, checklists, and similar civil litigation forms.

    The tool identifies the most relevant civil litigation template by applying fuzzy matching
    against the available template file names and their contents based on the provided domain.

    Args:
        domain (str): A user-provided description or name of the civil litigation form
                      (e.g., "Address Form", "Vakalatnama", "Memo of Appearance").

    Returns:
        Optional[Dict]: A dictionary containing the matched template content
                        if a suitable template is found; otherwise, None.
    """

    # Directory where civil litigation templates are stored
    CIVIL_TEMPLATES_DIR = "civil_litigation_templates"
    TEMPLATE_EXTENSION = ".md"

    # 1. Normalize domain input
    domain_normalized = domain.lower().replace("-", " ").strip()

    # Mapping of common civil litigation forms to keywords
    template_name_to_keywords = {
        "Address Form": ["address form", "party address"],
        "Vakalatnama": ["vakalatnama", "power of attorney"],
        "Memo of Appearance": ["memo of appearance", "appearance"],
        "Memorandum of Appearance": ["memorandum of appearance"],
        "Inspection Form": ["inspection", "record inspection"],
        "Case Information Format": ["case information", "case details"],
        "Index Form": ["index", "index of documents"],
        "List of Documents": ["list of documents", "documents annexed"],
        "Notice to Produce": ["notice to produce", "produce documents"],
        "Process Fee": ["process fee", "court process fee"],
        "Commercial Court Forms": ["commercial court", "commercial litigation"],
    }

    best_match_score = -1
    best_match_content = None

    # Find all markdown templates
    template_files = glob.glob(
        os.path.join(CIVIL_TEMPLATES_DIR, f"*{TEMPLATE_EXTENSION}")
    )

    if not template_files:
        print(f"Warning: No files found in '{CIVIL_TEMPLATES_DIR}'.")
        return None

    for file_path in template_files:
        file_name = (
            os.path.basename(file_path)
            .removesuffix(TEMPLATE_EXTENSION)
            .lower()
            .replace("_", " ")
            .strip()
        )

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
            content_normalized = content.lower()
        except Exception as e:
            print(f"Error reading file {file_path}: {e}")
            continue

        # ----------------------------
        # Scoring Logic
        # ----------------------------

        # A. File name similarity
        name_match_score = fuzz.partial_ratio(file_name, domain_normalized)

        # B. Content relevance
        content_match_score = fuzz.token_set_ratio(
            domain_normalized, content_normalized
        )

        # C. Keyword reinforcement
        keyword_score = 0
        for standard_name, keywords in template_name_to_keywords.items():
            if (
                standard_name.lower() in file_name
                or any(k in content_normalized for k in keywords)
            ):
                keyword_score = 10
                break

        # Final weighted score
        final_score = (
            0.40 * name_match_score
            + 0.50 * content_match_score
            + keyword_score
        )

        print(
            f"Template: {file_name} | Final Score: {final_score:.2f} "
            f"(Name: {name_match_score}, Content: {content_match_score})"
        )

        if final_score > best_match_score:
            best_match_score = final_score
            best_match_content = content

    # Minimum confidence threshold
    MATCH_THRESHOLD = 65

    if best_match_score >= MATCH_THRESHOLD:
        return {
            "civil_document": best_match_content
        }

    return None


def commercial_templates(domain: str) -> Optional[Dict]:
    """
    This tool is responsible for retrieving templates for commercial court
    and commercial litigation procedural documents only.
    It supports CA forms, commercial court filing formats, and similar documents.

    The tool identifies the most relevant commercial template by applying
    fuzzy matching against the available template file names and their contents
    based on the provided domain.

    Args:
        domain (str): A user-provided description or name of the commercial form
                      (e.g., "CA Form 7", "Commercial Court Filing").

    Returns:
        Optional[Dict]: A dictionary containing the matched template content
                        if a suitable template is found; otherwise, None.
    """

    # Directory where commercial templates are stored
    COMMERCIAL_TEMPLATES_DIR = "commercial_templates"
    TEMPLATE_EXTENSION = ".md"

    # 1. Normalize domain input
    domain_normalized = domain.lower().replace("-", " ").strip()

    # Mapping of standard commercial forms to keywords
    template_name_to_keywords = {
        "CA Form": ["ca form", "commercial application"],
        "CA Form 7": ["ca form 7", "commercial application 7"],
        "Commercial Court Filing": ["commercial court", "commercial filing"],
        "Commercial Court Rules": ["commercial court rules", "commercial rules"],
        "Statement of Claim": ["statement of claim", "soc"],
        "Written Statement": ["written statement", "defence"],
        "Commercial Summary Suit": ["summary suit", "commercial summary"],
    }

    best_match_score = -1
    best_match_content = None

    # Locate all markdown templates
    template_files = glob.glob(
        os.path.join(COMMERCIAL_TEMPLATES_DIR, f"*{TEMPLATE_EXTENSION}")
    )

    if not template_files:
        print(f"Warning: No files found in '{COMMERCIAL_TEMPLATES_DIR}'.")
        return None

    for file_path in template_files:
        file_name = (
            os.path.basename(file_path)
            .removesuffix(TEMPLATE_EXTENSION)
            .lower()
            .replace("_", " ")
            .strip()
        )

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
            content_normalized = content.lower()
        except Exception as e:
            print(f"Error reading file {file_path}: {e}")
            continue

        # ----------------------------
        # Scoring Logic
        # ----------------------------

        # A. File name similarity
        name_match_score = fuzz.partial_ratio(file_name, domain_normalized)

        # B. Content relevance
        content_match_score = fuzz.token_set_ratio(
            domain_normalized, content_normalized
        )

        # C. Keyword reinforcement
        keyword_score = 0
        for standard_name, keywords in template_name_to_keywords.items():
            if (
                standard_name.lower() in file_name
                or any(k in content_normalized for k in keywords)
            ):
                keyword_score = 10
                break

        # Final weighted score
        final_score = (
            0.40 * name_match_score
            + 0.50 * content_match_score
            + keyword_score
        )

        print(
            f"Template: {file_name} | Final Score: {final_score:.2f} "
            f"(Name: {name_match_score}, Content: {content_match_score})"
        )

        if final_score > best_match_score:
            best_match_score = final_score
            best_match_content = content

    # Minimum confidence threshold
    MATCH_THRESHOLD = 65

    if best_match_score >= MATCH_THRESHOLD:
        return {
            "commercial_document": best_match_content
        }

    return None


def criminal_or_civil_litigation(domain: str) -> Optional[Dict]:
    """
    This tool is responsible for retrieving templates for procedural documents
    that are commonly used in both criminal and civil litigation.
    These include general-purpose court forms such as vakalatnamas,
    process fee forms, inspection forms, and similar filings.

    The tool identifies the most relevant template by applying fuzzy matching
    against the available template file names and their contents
    based on the provided domain.

    Args:
        domain (str): A user-provided description or name of the form
                      (e.g., "Process Fee Form", "Vakalatnama Form").

    Returns:
        Optional[Dict]: A dictionary containing the matched template content
                        if a suitable template is found; otherwise, None.
    """

    # Directory where common civil/criminal templates are stored
    COMMON_TEMPLATES_DIR = "common_litigation_templates"
    TEMPLATE_EXTENSION = ".md"

    # 1. Normalize domain input
    domain_normalized = domain.lower().replace("-", " ").strip()

    # Mapping of commonly shared forms to keywords
    template_name_to_keywords = {
        "Vakalatnama": ["vakalatnama", "power of attorney"],
        "Process Fee": ["process fee", "court fee"],
        "E-Court Fee": ["e court fee", "court fee"],
        "Inspection Form": ["inspection", "record inspection"],
        "Memo of Appearance": ["memo of appearance", "appearance"],
        "Address Form": ["address form", "party address"],
        "List of Documents": ["list of documents", "annexures"],
        "Filing Form": ["filing form", "court filing"],
    }

    best_match_score = -1
    best_match_content = None

    # Locate all markdown templates
    template_files = glob.glob(
        os.path.join(COMMON_TEMPLATES_DIR, f"*{TEMPLATE_EXTENSION}")
    )

    if not template_files:
        print(f"Warning: No files found in '{COMMON_TEMPLATES_DIR}'.")
        return None

    for file_path in template_files:
        file_name = (
            os.path.basename(file_path)
            .removesuffix(TEMPLATE_EXTENSION)
            .lower()
            .replace("_", " ")
            .strip()
        )

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
            content_normalized = content.lower()
        except Exception as e:
            print(f"Error reading file {file_path}: {e}")
            continue

        # ----------------------------
        # Scoring Logic
        # ----------------------------

        # A. File name similarity
        name_match_score = fuzz.partial_ratio(file_name, domain_normalized)

        # B. Content relevance
        content_match_score = fuzz.token_set_ratio(
            domain_normalized, content_normalized
        )

        # C. Keyword reinforcement
        keyword_score = 0
        for standard_name, keywords in template_name_to_keywords.items():
            if (
                standard_name.lower() in file_name
                or any(k in content_normalized for k in keywords)
            ):
                keyword_score = 10
                break

        # Final weighted score
        final_score = (
            0.40 * name_match_score
            + 0.50 * content_match_score
            + keyword_score
        )

        print(
            f"Template: {file_name} | Final Score: {final_score:.2f} "
            f"(Name: {name_match_score}, Content: {content_match_score})"
        )

        if final_score > best_match_score:
            best_match_score = final_score
            best_match_content = content

    # Minimum confidence threshold
    MATCH_THRESHOLD = 65

    if best_match_score >= MATCH_THRESHOLD:
        return {
            "common_litigation_document": best_match_content
        }

    return None


from typing import Optional, Dict
import os
import glob
from fuzzywuzzy import fuzz


def writ_template(domain: str) -> Optional[Dict]:
    """
    This tool is responsible for retrieving templates for writ petitions only.
    It supports writs such as Habeas Corpus, Mandamus, Certiorari, Prohibition,
    Quo Warranto, and other constitutional writ petitions.

    The tool identifies the most relevant writ petition template by applying
    fuzzy matching against the available template file names and their contents
    based on the provided domain.

    Args:
        domain (str): A user-provided description or name of the writ
                      (e.g., "Writ of Mandamus", "Habeas Corpus Petition").

    Returns:
        Optional[Dict]: A dictionary containing the matched template content
                        if a suitable template is found; otherwise, None.
    """

    # Directory where writ templates are stored
    WRIT_TEMPLATES_DIR = "writ_templates"
    TEMPLATE_EXTENSION = ".md"

    # 1. Normalize domain input
    domain_normalized = domain.lower().replace("-", " ").strip()

    # Mapping of standard writ types to keywords
    template_name_to_keywords = {
        "Habeas Corpus": ["habeas corpus", "illegal detention"],
        "Mandamus": ["mandamus", "public duty", "direction"],
        "Certiorari": ["certiorari", "quash order"],
        "Prohibition": ["prohibition", "restrain proceedings"],
        "Quo Warranto": ["quo warranto", "authority of office"],
        "Writ Petition": ["writ petition", "article 226", "article 32"],
    }

    best_match_score = -1
    best_match_content = None

    # Locate all markdown templates
    template_files = glob.glob(
        os.path.join(WRIT_TEMPLATES_DIR, f"*{TEMPLATE_EXTENSION}")
    )

    if not template_files:
        print(f"Warning: No files found in '{WRIT_TEMPLATES_DIR}'.")
        return None

    for file_path in template_files:
        file_name = (
            os.path.basename(file_path)
            .removesuffix(TEMPLATE_EXTENSION)
            .lower()
            .replace("_", " ")
            .strip()
        )

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
            content_normalized = content.lower()
        except Exception as e:
            print(f"Error reading file {file_path}: {e}")
            continue

        # ----------------------------
        # Scoring Logic
        # ----------------------------

        # A. File name similarity
        name_match_score = fuzz.partial_ratio(file_name, domain_normalized)

        # B. Content relevance
        content_match_score = fuzz.token_set_ratio(
            domain_normalized, content_normalized
        )

        # C. Keyword reinforcement
        keyword_score = 0
        for standard_name, keywords in template_name_to_keywords.items():
            if (
                standard_name.lower() in file_name
                or any(k in content_normalized for k in keywords)
            ):
                keyword_score = 10
                break

        # Final weighted score
        final_score = (
            0.40 * name_match_score
            + 0.50 * content_match_score
            + keyword_score
        )

        print(
            f"Writ Template: {file_name} | Final Score: {final_score:.2f} "
            f"(Name: {name_match_score}, Content: {content_match_score})"
        )

        if final_score > best_match_score:
            best_match_score = final_score
            best_match_content = content

    # Minimum confidence threshold
    MATCH_THRESHOLD = 65

    if best_match_score >= MATCH_THRESHOLD:
        return {
            "writ_document": best_match_content
        }

    return None




def family_law(domain: str) -> Optional[Dict]:
    """
    This tool is responsible for retrieving templates for family law matters only.
    It supports legal documents related to divorce, judicial separation, maintenance,
    adoption, guardianship, domestic violence, restitution of conjugal rights,
    and other family law proceedings.

    The tool identifies the most relevant family law template by applying fuzzy
    matching against the available template file names and their contents
    based on the provided domain.

    Args:
        domain (str): A user-provided description or name of the family law matter
                      (e.g., "Divorce Petition", "Adoption Deed", "Maintenance Application").

    Returns:
        Optional[Dict]: A dictionary containing the matched family law template content
                        if a suitable template is found; otherwise, None.
    """

    # Directory where family law templates are stored
    FAMILY_LAW_TEMPLATES_DIR = "family_law_templates"
    TEMPLATE_EXTENSION = ".md"

    # 1. Normalize domain input
    domain_normalized = domain.lower().replace("-", " ").strip()

    # Standard family law categories with reinforcement keywords
    template_name_to_keywords = {
        "Divorce": ["divorce", "dissolution of marriage"],
        "Judicial Separation": ["judicial separation"],
        "Maintenance": ["maintenance", "section 125", "alimony"],
        "Adoption": ["adoption", "adoptive parent"],
        "Guardianship": ["guardianship", "minor child"],
        "Domestic Violence": ["domestic violence", "protection order"],
        "Restitution of Conjugal Rights": ["restitution", "conjugal rights"],
        "Family Court Petition": ["family court", "marriage act"],
    }

    best_match_score = -1
    best_match_content = None

    # Locate all markdown templates
    template_files = glob.glob(
        os.path.join(FAMILY_LAW_TEMPLATES_DIR, f"*{TEMPLATE_EXTENSION}")
    )

    if not template_files:
        print(f"Warning: No files found in '{FAMILY_LAW_TEMPLATES_DIR}'.")
        return None

    for file_path in template_files:
        file_name = (
            os.path.basename(file_path)
            .removesuffix(TEMPLATE_EXTENSION)
            .lower()
            .replace("_", " ")
            .strip()
        )

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
            content_normalized = content.lower()
        except Exception as e:
            print(f"Error reading file {file_path}: {e}")
            continue

        # ----------------------------
        # Scoring Logic
        # ----------------------------

        # A. File name similarity
        name_match_score = fuzz.partial_ratio(file_name, domain_normalized)

        # B. Content relevance
        content_match_score = fuzz.token_set_ratio(
            domain_normalized, content_normalized
        )

        # C. Keyword reinforcement
        keyword_score = 0
        for standard_name, keywords in template_name_to_keywords.items():
            if (
                standard_name.lower() in file_name
                or any(k in content_normalized for k in keywords)
            ):
                keyword_score = 10
                break

        # Final weighted score
        final_score = (
            0.40 * name_match_score
            + 0.50 * content_match_score
            + keyword_score
        )

        print(
            f"Family Law Template: {file_name} | Final Score: {final_score:.2f} "
            f"(Name: {name_match_score}, Content: {content_match_score})"
        )

        if final_score > best_match_score:
            best_match_score = final_score
            best_match_content = content

    # Minimum confidence threshold
    MATCH_THRESHOLD = 65

    if best_match_score >= MATCH_THRESHOLD:
        return {
            "family_law": best_match_content
        }

    return None


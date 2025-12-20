# # contract_template_extractor.py

# import os
# import re
# import pdfplumber
# import spacy

# # -------------------------------
# # CONFIG
# # -------------------------------

# # Path to your dataset
# DATASET_PATH = r"C:\Users\Gayathri\Downloads\GAVEL\agents\draft_helper\CUAD_v1\full_contract_pdf"

# # Where to save templates
# OUTPUT_PATH = r"C:\Users\Gayathri\Downloads\GAVEL\agents\draft_helper\contract_templates"
# os.makedirs(OUTPUT_PATH, exist_ok=True)

# # Load spaCy NER model
# nlp = spacy.load("en_core_web_sm")
# nlp.max_length = 3000000  # increase limit to handle large texts

# # -------------------------------
# # FUNCTIONS
# # -------------------------------

# def extract_text_from_pdf(pdf_path):
#     """Extract text from a single PDF"""
#     text = ""
#     with pdfplumber.open(pdf_path) as pdf:
#         for page in pdf.pages:
#             page_text = page.extract_text()
#             if page_text:
#                 text += page_text + "\n"
#     return text

# def clean_text(text):
#     """Normalize text: remove multiple spaces and newlines"""
#     text = re.sub(r'\n+', '\n', text)
#     text = re.sub(r'\s+', ' ', text)
#     return text.strip()

# def generate_template(text, chunk_size=80000):
#     """
#     Replace common variable entities with placeholders using chunking:
#     - Parties / Organizations -> {{party_name}}
#     - Dates -> {{effective_date}}
#     - Money / Percent -> {{amount}}
#     """
#     template = ""
#     for i in range(0, len(text), chunk_size):
#         chunk = text[i:i+chunk_size]
#         doc = nlp(chunk)
#         chunk_template = chunk
#         for ent in doc.ents:
#             if ent.label_ in ["PERSON", "ORG"]:
#                 chunk_template = chunk_template.replace(ent.text, "{{party_name}}")
#             elif ent.label_ in ["DATE"]:
#                 chunk_template = chunk_template.replace(ent.text, "{{effective_date}}")
#             elif ent.label_ in ["MONEY", "PERCENT"]:
#                 chunk_template = chunk_template.replace(ent.text, "{{amount}}")
#         template += chunk_template
#     return template

# def segment_clauses(text):
#     """
#     Split text into clauses based on numbered headings like 1., 2.1., etc.
#     Returns a list of clauses
#     """
#     pattern = r'(\n\d+(\.\d+)*\.?\s+[A-Za-z].*?)\n'
#     splits = re.split(pattern, text)
#     clauses = [s.strip() for s in splits if s and s.strip()]
#     return clauses

# # -------------------------------
# # MAIN PROCESS
# # -------------------------------

# for root, dirs, files in os.walk(DATASET_PATH):
#     # Skip if no PDF files in this folder
#     pdf_files = [f for f in files if f.lower().endswith(".pdf")]
#     if not pdf_files:
#         continue
    
#     # Contract type = leaf folder name
#     contract_type = os.path.basename(root)
#     output_file = os.path.join(OUTPUT_PATH, f"{contract_type}.md")
    
#     # Skip if template already exists
#     if os.path.exists(output_file):
#         print(f"[SKIP] Template for {contract_type} already exists. Skipping.")
#         continue
    
#     print(f"[INFO] Processing contract type: {contract_type}")
    
#     combined_text = ""
    
#     # Extract and combine all PDFs in this folder
#     for pdf_file in pdf_files:
#         pdf_path = os.path.join(root, pdf_file)
#         try:
#             text = extract_text_from_pdf(pdf_path)
#             combined_text += clean_text(text) + "\n\n"
#         except Exception as e:
#             print(f"[WARNING] Failed to read {pdf_file}: {e}")
    
#     if not combined_text.strip():
#         print(f"[WARNING] No text found for {contract_type}, skipping.")
#         continue
    
#     # Replace entities with placeholders (chunked)
#     template_text = generate_template(combined_text)
    
#     # Optional: segment into clauses
#     clauses = segment_clauses(template_text)
    
#     # Recombine clauses into Markdown-style template
#     markdown_template = f"# Template for {contract_type}\n\n"
#     for idx, clause in enumerate(clauses, start=1):
#         markdown_template += f"## Clause {idx}\n{clause}\n\n"
    
#     # Save template
#     with open(output_file, "w", encoding="utf-8") as f:
#         f.write(markdown_template)
    
#     print(f"[INFO] Template saved: {output_file}")

# print("[DONE] All templates generated.")



# import os
# import pdfplumber

# # Path to folder containing PDFs
# folder_path = r"C:\Users\Gayathri\Downloads\GAVEL\agents\draft_helper\contract_templates"

# # Loop through all files in the folder
# for filename in os.listdir(folder_path):
#     if filename.lower().endswith(".pdf"):
#         pdf_path = os.path.join(folder_path, filename)
#         md_filename = filename.rsplit(".", 1)[0] + ".md"
#         md_path = os.path.join(folder_path, md_filename)

#         # Extract text from PDF
#         with pdfplumber.open(pdf_path) as pdf:
#             all_text = ""
#             for page in pdf.pages:
#                 all_text += page.extract_text() + "\n\n"

#         # Save as Markdown file
#         with open(md_path, "w", encoding="utf-8") as f:
#             f.write(all_text)

#         print(f"Converted: {filename} → {md_filename}")

# print("All PDFs converted to Markdown!")


# import os

# base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# index_path = os.path.join(base_dir, "agents\draft_helper\kanoon_faiss_index.bin")
# metadata_path = os.path.join(base_dir, "agents\draft_helper\kanoon_metadata.json")

# print("Index exists:", os.path.exists(index_path))
# print("Metadata exists:", os.path.exists(metadata_path))
# print("Index path:", index_path)
# print("Metadata path:", metadata_path)


import pypandoc

pypandoc.download_pandoc()
# combine_dataset.py
import os
import json
import re
import PyPDF2
import docx2txt
import mammoth

SUPPORTED_EXTENSIONS = {'.pdf', '.docx', '.doc', '.txt', '.json'}

def clean_text(text):
    """
    Cleans text by:
    - Removing non-alphanumeric special characters (except .,!?;:'"() and spaces)
    - Removing multiple spaces/newlines
    - Ensuring one empty line between sections
    """
    if not text:
        return ""

    # Remove unwanted special characters (keep punctuation and normal chars)
    text = re.sub(r"[^a-zA-Z0-9\s.,!?;:'\"()\-]", " ", text)

    # Replace multiple spaces with single space
    text = re.sub(r"\s+", " ", text)

    # Normalize newlines
    text = re.sub(r"\n+", "\n", text)

    return text.strip()


def combine_dataset_files(dataset_folder="dataset", output_file="comfolder/combinedfile2.txt"):
    """
    Combine all text content from dataset/ folder into a single combinedfile1.txt
    Supports PDF, DOCX, DOC, TXT, and JSON.
    Removes extra empty lines and special characters.
    """
    print(f"🧩 Combining all files from '{dataset_folder}' into {output_file} ...")

    if not os.path.exists(dataset_folder):
        raise ValueError(f"Dataset folder '{dataset_folder}' not found!")

    combined_text_parts = []

    for root, dirs, files in os.walk(dataset_folder):
        for filename in files:
            file_path = os.path.join(root, filename)
            file_ext = os.path.splitext(filename)[1].lower()

            if file_ext not in SUPPORTED_EXTENSIONS:
                continue

            try:
                text = ""

                if file_ext == ".pdf":
                    with open(file_path, "rb") as f:
                        reader = PyPDF2.PdfReader(f)
                        for page_num, page in enumerate(reader.pages, start=1):
                            page_text = page.extract_text()
                            if page_text:
                                text += f"\n=== {filename} (Page {page_num}) ===\n{page_text}\n"

                elif file_ext == ".docx":
                    text = docx2txt.process(file_path)
                    if text:
                        text = f"=== {filename} (DOCX) ===\n{text}\n"

                elif file_ext == ".doc":
                    with open(file_path, "rb") as f:
                        result = mammoth.extract_raw_text(f)
                        text = result.value
                        if text:
                            text = f"=== {filename} (DOC) ===\n{text}\n"

                elif file_ext == ".txt":
                    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                        t = f.read()
                        if t:
                            text = f"=== {filename} (TXT) ===\n{t}\n"

                elif file_ext == ".json":
                    with open(file_path, "r", encoding="utf-8") as f:
                        data = json.load(f)
                        json_text = json.dumps(data, indent=2, ensure_ascii=False)
                        text = f"=== {filename} (JSON) ===\n{json_text}\n"

                # Clean and append
                if text.strip():
                    cleaned_text = clean_text(text)
                    combined_text_parts.append(cleaned_text)

            except Exception as e:
                print(f"⚠️ Skipping {filename}: {e}")

    # Join all sections with exactly one blank line
    final_combined = "\n\n".join(combined_text_parts)

    # Write to file
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    with open(output_file, "w", encoding="utf-8") as out_file:
        out_file.write(final_combined.strip() + "\n")

    print(f"✅ Combined dataset saved to '{output_file}'")
    print(f"📏 File size: {len(final_combined)} characters")


if __name__ == "__main__":
    combine_dataset_files()

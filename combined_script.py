# combine_dataset.py
import os
import json
import PyPDF2
import docx2txt
import mammoth

SUPPORTED_EXTENSIONS = {'.pdf', '.docx', '.doc', '.txt', '.json'}

def combine_dataset_files(dataset_folder="dataset", output_file="comfolder/combinedfile1.txt"):
    """
    Combine all text content from dataset/ folder into a single combinedfile1.txt
    Supports PDF, DOCX, DOC, TXT, and JSON.
    """
    print(f"🧩 Combining all files from '{dataset_folder}' into {output_file} ...")

    if not os.path.exists(dataset_folder):
        raise ValueError(f"Dataset folder '{dataset_folder}' not found!")

    combined_text = ""

    for root, dirs, files in os.walk(dataset_folder):
        for filename in files:
            file_path = os.path.join(root, filename)
            file_ext = os.path.splitext(filename)[1].lower()

            if file_ext not in SUPPORTED_EXTENSIONS:
                continue

            try:
                # PDF files
                if file_ext == ".pdf":
                    with open(file_path, "rb") as f:
                        reader = PyPDF2.PdfReader(f)
                        for page_num, page in enumerate(reader.pages, start=1):
                            text = page.extract_text()
                            if text:
                                combined_text += f"\n========================================================================================"
                                combined_text += f"\n\n=== {filename} (Page {page_num}) ===\n{text}\n"

                # DOCX files
                elif file_ext == ".docx":
                    text = docx2txt.process(file_path)
                    if text:
                        
                        combined_text += f"\n========================================================================================"
                        combined_text += f"\n\n=== {filename} (DOCX) ===\n{text}\n"
                        

                # DOC files
                elif file_ext == ".doc":
                    with open(file_path, "rb") as f:
                        result = mammoth.extract_raw_text(f)
                        text = result.value
                        if text:
                            combined_text += f"\n========================================================================================"
                            combined_text += f"\n\n=== {filename} (DOC) ===\n{text}\n"

                # TXT files
                elif file_ext == ".txt":
                    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                        text = f.read()
                        if text:
                            combined_text += f"\n========================================================================================"
                            combined_text += f"\n\n=== {filename} (TXT) ===\n{text}\n"

                # JSON files
                elif file_ext == ".json":
                    with open(file_path, "r", encoding="utf-8") as f:
                        data = json.load(f)
                        json_text = json.dumps(data, indent=2, ensure_ascii=False)
                        combined_text += f"============================================" 
                        combined_text += f"\n\n=== {filename} (JSON) ===\n{json_text}\n"

            except Exception as e:
                print(f"⚠️ Skipping {filename}: {e}")

    # Write combined file
    with open(output_file, "w", encoding="utf-8") as out_file:
        out_file.write(combined_text.strip())

    print(f"✅ Combined dataset saved to '{output_file}'")
    print(f"📏 File size: {len(combined_text)} characters")


if __name__ == "__main__":
    combine_dataset_files()

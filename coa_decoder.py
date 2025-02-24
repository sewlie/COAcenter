import pdfplumber
import re
import logging
import os

# ✅ Configure logging
logging.basicConfig(
    filename="single_pdf_analyzer.log",
    level=logging.DEBUG,
    format="%(asctime)s - %(levelname)s - %(message)s",
)

# ✅ Paths
PDF_FOLDER_PATH = r"C:\Users\lilma\OneDrive\Documentos\NICO CODE\COAcenter"

# ✅ Function to clean extracted text
def clean_text(text):
    if text is None:
        return ""
    return re.sub(r'\s+', ' ', text).strip()

# ✅ Function to extract COA data
def extract_data_from_pdf(pdf_path):
    extracted_data = {
        "Sample Information": {},
        "Cannabinoids": [],
        "Pesticides": {},
        "Microbial & Mycotoxins": [],
        "Heavy Metals": [],
        "Filth & Moisture": []
    }

    with pdfplumber.open(pdf_path) as pdf:
        for page_num, page in enumerate(pdf.pages, start=1):
            text = page.extract_text()
            if not text:
                print(f"⚠️ Page {page_num} has no extracted text.")
                continue

            lines = text.split("\n")

            # ✅ Extract Sample Information (Page 1)
            if page_num == 1:
                for line in lines:
                    if "Batch#:" in line:
                        extracted_data["Sample Information"]["Batch#"] = clean_text(line.split("Batch#:")[1])
                    if "Sampled:" in line:
                        extracted_data["Sample Information"]["Sampled Date"] = clean_text(line.split("Sampled:")[1])
                    if "Total Amount:" in line:
                        extracted_data["Sample Information"]["Total Amount"] = clean_text(line.split("Total Amount:")[1])
                    if "Retail Product Size:" in line:
                        extracted_data["Sample Information"]["Retail Size"] = clean_text(line.split("Retail Product Size:")[1])
                    if "Retail Serving Size:" in line:
                        extracted_data["Sample Information"]["Serving Size"] = clean_text(line.split("Retail Serving Size:")[1])

            # ✅ Extract Pesticides (Handles Two Columns)
            if "Pesticides PASSED" in text or "Pesticide LOQ" in text:
                pesticides = {}
                capture = False
                for line in lines:
                    if "Pesticide LOQ" in line or "Pesticides PASSED" in line:
                        capture = True
                        continue
                    if "Heavy Metals PASSED" in line or "Microbial PASSED" in line:
                        capture = False
                        break
                    
                    if capture:
                        parts = re.split(r'\s{2,}', line.strip())  # Split on multiple spaces
                        if len(parts) >= 5:
                            name, loq, units, action_level, pass_fail = parts[:5]
                            result = parts[5] if len(parts) > 5 else "<0.1000"

                            pesticides[clean_text(name)] = {
                                "LOQ": clean_text(loq),
                                "Units": clean_text(units),
                                "Action Level": clean_text(action_level),
                                "Pass/Fail": clean_text(pass_fail),
                                "Result": clean_text(result),
                            }
                
                if pesticides:
                    extracted_data["Pesticides"] = pesticides

            # ✅ Extract Microbial & Mycotoxins
            if "Microbial PASSED" in text or "Mycotoxins PASSED" in text:
                capture = False
                for line in lines:
                    if "Microbial PASSED" in line or "Mycotoxins PASSED" in line:
                        capture = True
                        continue
                    if "Heavy Metals PASSED" in line:
                        capture = False
                        break
                    if capture:
                        extracted_data["Microbial & Mycotoxins"].append(clean_text(line))

            # ✅ Extract Heavy Metals
            if "Heavy Metals PASSED" in text:
                capture = False
                for line in lines:
                    if "Heavy Metals PASSED" in line:
                        capture = True
                        continue
                    if "Filth/Foreign PASSED" in line:
                        capture = False
                        break
                    if capture:
                        extracted_data["Heavy Metals"].append(clean_text(line))

            # ✅ Extract Filth & Moisture
            if "Filth/Foreign PASSED" in text:
                capture = False
                for line in lines:
                    if "Filth/Foreign PASSED" in line:
                        capture = True
                        continue
                    if "Water Activity" in line:
                        capture = False
                        break
                    if capture:
                        extracted_data["Filth & Moisture"].append(clean_text(line))

    return extracted_data

# ✅ Function to process all PDFs in the folder
def process_all_pdfs(folder_path):
    for file_name in os.listdir(folder_path):
        if file_name.lower().endswith(".pdf"):
            pdf_path = os.path.join(folder_path, file_name)
            print(f"\n🔹 **Processing {file_name}**\n")

            # ✅ Extract COA data
            extracted_data = extract_data_from_pdf(pdf_path)

            # ✅ Print the structured data
            print("\n🔹 **Sample Information:**")
            for key, value in extracted_data["Sample Information"].items():
                print(f"{key}: {value}")

            print("\n🔹 **Pesticides:**")
            if extracted_data["Pesticides"]:
                for name, data in extracted_data["Pesticides"].items():
                    print(f"{name}: {data}")
            else:
                print("No pesticides found.")

# ✅ Run processing for all PDFs in the folder
process_all_pdfs(PDF_FOLDER_PATH)

print("\n✅ **Processing complete!** ✅")

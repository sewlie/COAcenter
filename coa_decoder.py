import pdfplumber
import re
import os
import json

# ✅ Paths
PDF_FOLDER_PATH = r"C:\Users\lilma\OneDrive\Documentos\NICO CODE\COAcenter"
CSV_FILE_PATH = r"C:\Users\lilma\OneDrive\Documentos\NICO CODE\COAcenter\extracted_terpenes.csv"

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

            # ✅ Extract Cannabinoids
            if "Cannabinoid" in text:
                capture = False
                for line in lines:
                    if "Cannabinoid" in line:
                        capture = True
                        continue
                    if "Weight:" in line:
                        capture = False
                        break
                    if capture:
                        extracted_data["Cannabinoids"].append(clean_text(line))

            # ✅ Extract Pesticides
            if "Pesticide LOQ" in text or "Pesticides PASSED" in text:
                for line in lines:
                    if "Heavy Metals" in line:
                        break
                    match = re.match(r'([\w\s-]+?)\s+([\d.]+)\s+ppm\s+([\d.]+)\s+(PASS|FAIL)\s+<?([\d.]+)', line)
                    if match:
                        name, loq, action_level, pass_fail, result = match.groups()
                        extracted_data["Pesticides"][clean_text(name)] = {
                            "LOQ (ppm)": loq,
                            "Action Level": action_level,
                            "Pass/Fail": pass_fail,
                            "Result": f"<{result}"
                        }

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

# ✅ Function to extract Terpenes
def extract_terpenes(pdf_path):
    with pdfplumber.open(pdf_path) as pdf:
        text = "".join(page.extract_text() for page in pdf.pages if page.extract_text())
        if not text.strip():
            return {}, "0.0000%"

    data = {}
    lines = text.split("\n")

    for i, line in enumerate(lines):
        if "Terpenes TESTED" in line:
            data["start_index"] = i
        elif "Total (%)" in line:
            data["end_index"] = i
            total_match = re.search(r"Total \(\%\)\s+(\d+\.\d+)", line)
            if total_match:
                data["total_percentage"] = f"{float(total_match.group(1)):.4f}%"

    terpene_data = {}
    start_index = data.get("start_index", 0)
    end_index = data.get("end_index", len(lines))

    for line in lines[start_index:end_index]:
        parts = re.split(r'\s+', line.strip())
        if len(parts) > 3:
            terpene_name_parts = []
            for part in parts:
                if re.match(r'^\d+(\.\d+)?$', part):
                    break
                terpene_name_parts.append(part)

            terpene_name = " ".join(terpene_name_parts).strip()
            try:
                result_percentage = parts[len(terpene_name_parts) + 2].strip()
                result_percentage = "0.0000%" if result_percentage.startswith("<") else f"{float(result_percentage):.4f}%"
                terpene_data[terpene_name] = result_percentage
            except (ValueError, IndexError):
                terpene_data[terpene_name] = "0.0000%"

    total_percentage = data.get("total_percentage", "0.0000%")
    return terpene_data, total_percentage

# ✅ Function to process all PDFs in the folder
def process_all_pdfs(folder_path):
    for file_name in os.listdir(folder_path):
        if file_name.lower().endswith(".pdf"):
            pdf_path = os.path.join(folder_path, file_name)
            print(f"\n🔹 **Processing {file_name}**\n")

            # ✅ Extract COA data
            extracted_data = extract_data_from_pdf(pdf_path)

            # ✅ Extract Terpene data
            terpene_data, total_terpenes = extract_terpenes(pdf_path)
            extracted_data["Terpenes"] = terpene_data
            extracted_data["Sample Information"]["Total Terpenes"] = total_terpenes

            # ✅ Print the structured data
            print("\n🔹 **Sample Information:**")
            for key, value in extracted_data["Sample Information"].items():
                print(f"{key}: {value}")

            print("\n🔹 **Terpenes:**")
            print(f"Total Terpenes: {total_terpenes}")
            for terpene, value in terpene_data.items():
                print(f"{terpene}: {value}")

            print("\n🔹 **Pesticides:**")
            for name, data in extracted_data["Pesticides"].items():
                print(f"{name}: {data}")


# ✅ Function to save COA data as JSON
def save_coa_data_to_json(data, file_path="coa_data.json"):
    with open(file_path, "w", encoding="utf-8") as json_file:
        json.dump(data, json_file, indent=4)
    print(f"\n✅ Data saved to {file_path}")

# ✅ Update to collect and save all PDFs' data
def process_all_pdfs(folder_path):
    all_data = []

    for file_name in os.listdir(folder_path):
        if file_name.lower().endswith(".pdf"):
            pdf_path = os.path.join(folder_path, file_name)
            print(f"\n🔹 **Processing {file_name}**\n")

            extracted_data = extract_data_from_pdf(pdf_path)
            terpene_data, total_terpenes = extract_terpenes(pdf_path)
            
            extracted_data["Terpenes"] = terpene_data
            extracted_data["Sample Information"]["Total Terpenes"] = total_terpenes
            extracted_data["Sample Information"]["File Name"] = file_name

            all_data.append(extracted_data)

    # ✅ Save all extracted data to JSON
    save_coa_data_to_json(all_data)

process_all_pdfs(PDF_FOLDER_PATH)
print("\n✅ **Processing complete! Data saved to JSON.** ✅")
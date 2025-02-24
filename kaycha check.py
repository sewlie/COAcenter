import pdfplumber
import re
import logging
import os
import csv

# Configure logging
logging.basicConfig(
    filename="single_pdf_analyzer.log",
    level=logging.DEBUG,
    format="%(asctime)s - %(levelname)s - %(message)s",
)

# Path to folder containing PDFs
PDF_FOLDER_PATH = r"C:\Users\lilma\OneDrive\Documentos\NICO CODE\COAcenter"
CSV_FILE_PATH = r"C:\Users\lilma\OneDrive\Documentos\NICO CODE\COAcenter\extracted_terpenes.csv"

def extract_data(text):
    """Extract all potential terpene-related data from the text."""
    data = {}
    lines = text.split("\n")

    print("\n==== STARTING DATA EXTRACTION ====")
    for i, line in enumerate(lines):
        print(f"Line {i + 1}: {line.strip()}")
        if "Terpenes TESTED" in line:
            print(f"Debug: Found start of terpene section at line {i + 1}.")
            data["start_index"] = i
        elif "Total (%)" in line:
            print(f"Debug: Found end of terpene section at line {i + 1}.")
            data["end_index"] = i
            # Extract the total percentage from this line
            total_match = re.search(r"Total \(\%\)\s+(\d+\.\d+)", line)
            if total_match:
                data["total_percentage"] = f"{float(total_match.group(1)):.4f}%"
    print("==== COMPLETED DATA EXTRACTION ====\n")

    return data, lines

def analyze_terpenes(data, lines):
    """Analyze and extract terpene details from the relevant section."""
    terpene_data = {}

    start_index = data.get("start_index", 0)
    end_index = data.get("end_index", len(lines))
    print(f"Debug: Analyzing lines from {start_index} to {end_index}.")

    for line in lines[start_index:end_index]:
        print(f"Analyzing line: {line.strip()}")

        # Match the line structure dynamically
        parts = re.split(r'\s+', line.strip())
        if len(parts) > 3:
            # Dynamically find where the numeric data starts
            terpene_name_parts = []
            for part in parts:
                if re.match(r'^\d+(\.\d+)?$', part):  # First numeric value marks the end of the name
                    break
                terpene_name_parts.append(part)

            terpene_name = " ".join(terpene_name_parts).strip()
            if not terpene_name.isupper():  # Ensure it's a valid uppercase name
                print(f"Debug: Skipping invalid terpene name: {terpene_name}")
                continue

            try:
                # The third numeric value after the name is the percentage
                result_percentage = parts[len(terpene_name_parts) + 2].strip()
                if result_percentage.startswith("<"):
                    result_percentage = "0.0000%"
                else:
                    result_percentage = f"{float(result_percentage):.4f}%"

                terpene_data[terpene_name] = result_percentage
                print(f"Debug: Found terpene {terpene_name}: {result_percentage}")
            except (ValueError, IndexError):
                terpene_data[terpene_name] = "0.0000%"
                print(f"Debug: Invalid or missing percentage for {terpene_name}, set to 0.0000%.")
        else:
            print(f"Debug: Line does not contain enough data: {line.strip()}")

    return terpene_data

def save_to_csv_with_name(terpene_data, csv_file_path, pdf_name, total_percentage):
    """Save the terpene data to a CSV file with the PDF name as the first column."""
    if not os.path.exists(csv_file_path):
        with open(csv_file_path, mode="w", newline="") as file:
            writer = csv.writer(file)

            # Write header
            header = ["Name", "Total Terpenes"] + list(terpene_data.keys())
            writer.writerow(header)

    try:
        with open(csv_file_path, mode="a", newline="") as file:
            writer = csv.writer(file)

            # Write row data
            row = [pdf_name, total_percentage] + list(terpene_data.values())
            writer.writerow(row)

        print(f"Terpene data saved to {csv_file_path}")
    except Exception as e:
        logging.error(f"Error saving to CSV: {e}")
        print(f"Error saving to CSV: {e}")

def extract_and_display(pdf_path, csv_file_path):
    """Extract and display data from the PDF, then save it to a CSV file."""
    try:
        with pdfplumber.open(pdf_path) as pdf:
            text = "".join(page.extract_text() for page in pdf.pages if page.extract_text())
            if not text.strip():
                print(f"No text extracted from {pdf_path}.")
                return

        data, lines = extract_data(text)
        terpene_data = analyze_terpenes(data, lines)

        total_percentage = data.get("total_percentage", "0.0000%")

        if terpene_data:
            print("\n==== TERPENE DATA ====")
            print(f"Total Terpenes: {total_percentage}")
            for terpene, value in terpene_data.items():
                print(f"{terpene}: {value}")
            print("========================\n")

            # Save the data to a CSV file
            pdf_name = os.path.basename(pdf_path).replace(".pdf", "")
            save_to_csv_with_name(terpene_data, csv_file_path, pdf_name, total_percentage)
        else:
            print(f"No terpene data found in {pdf_path}.")

    except Exception as e:
        logging.error(f"Error processing {pdf_path}: {e}")
        print(f"Error processing {pdf_path}: {e}")

def process_all_pdfs_in_folder(folder_path, csv_file_path):
    """Process all PDFs in the given folder."""
    for file_name in os.listdir(folder_path):
        if file_name.lower().endswith(".pdf"):
            pdf_path = os.path.join(folder_path, file_name)
            print(f"Processing {pdf_path}...")
            extract_and_display(pdf_path, csv_file_path)

if __name__ == "__main__":
    print("Processing all Kaycha PDFs...")
    process_all_pdfs_in_folder(PDF_FOLDER_PATH, CSV_FILE_PATH)

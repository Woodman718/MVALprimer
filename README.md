# Sci-Hub Processing
This repository contains scripts and data for processing Sci-Hub data, including checking compressed files, generating file paths, and extracting primers from PDFs.
## Directory Structure
```plaintext
sci_hub_processing/
├── scripts/
│   ├── echo_num.sh
│   ├── move_file.sh
│   ├── Sql_cnn.py
│   ├── Doi_Percent.py
│   ├── ConstureZip.py
│   ├── mv_unzip.py
│   ├── zip_ex.sh
│   ├── map_files.py
│   └── pdf_search_v7.py
├── docs/
│   ├── ReadMe.md
│   └── SCI_HUB_Processing_Flowchart.png
```
## Processing Flowchart

Below is the flowchart of the processing steps:

![SCI_HUB Processing Flowchart](./docs/SCI_HUB_Processing_Flowchart.png)


## Scripts

### 1. Checking Sci-Hub Compressed Files

- **echo_num.sh**: Counts the number of files in subdirectories.
- **move_file.sh**: Moves files based on specified criteria.

### 2. From scimag.sql to file_path.txt

- **Sql_cnn.py**: Connects to the MySQL database and generates `data.tsv`.
- **Doi_Percent.py**: Calculates the percentage of matching DOIs.
- **ConstureZip.py**:  Generates a list of zip files for extraction.
- **mv_unzip.py**: Moves and extracts target zip files.
- **zip_ex.sh**: Extracts zip files using 4 threads by default (e.g., unzip with parallel processing via -j 4).
- **map_files.py**: Generates a PDF processing file list.

### 3. From PDF to summary.tsv

- **pdf_search_v7.py**: Extracts metadata from PDFs and generates `summary.tsv`.

## Usage

### Step 1: Validate Sci-Hub Compressed Files

This step validates compressed files within Sci-Hub directories. It accepts two parameters:

- **`parent_dir`**: Path to the parent directory  
  Example: `/scihub/data/raw`
- **`output_dir`**: Path to the output directory  
  Example: `/scihub/processed`

The process filters files and counts zip archives in subdirectories:
- **Empty directories** are moved to __/zero__.
- **Directories with between 1 and 99** files are moved to __/residue__.

```bash
./scripts/echo_num.sh gao/mqi_1/
./scripts/move_file.sh gao/mqi_1/ .
```

### Step 2: From scimag.sql to file_path.txt

1. **Import scimag.sql(31G)**

   ```bash
   mysql -u root -p < data/input/scimag.sql
   ```

2. **Generate data.tsv**

   ```bash
   python scripts/Sql_cnn.py
   ```

3. **Calculate DOI percentages**

   ```bash
   python scripts/Doi_Percent.py
   ```

4. **Generate ZipName.txt**

   ```bash
   python scripts/ConstureZip.py
   ```

5. **Move and extract zip files**

   ```bash
   python scripts/mv_unzip.py
   ```

6. **Extract zip files**

   ```bash
   bash scripts/zip_ex.sh /s1/SHARE/sci_hub/pub_med/Mingqi/ need_ex.txt
   ```

7. **Generate pdf_list.txt**

   ```bash
   python scripts/map_files.py
   ```

### Step 3: From PDF to summary.tsv
1. **Import necessary libraries and configure settings**  
   Import libraries (`os`, `time`, `re`, `csv`, `pandas`, `PyMuPDF/fitz`) and configure `pdf2doi` settings.

2. **DOI transformation and processing**  
   Define functions to handle DOIs:  
   - `transform_doi`: Standardize DOI format.  
   - `escape_doi`/`unescape_doi`: Escape special characters in DOIs and revert them.

3. **Read PDF file list**  
   Implement `read_pdf_list` to load a list of PDF file paths from a specified input file.

4. **Validate PDF files**  
   Use `PyMuPDF (fitz)` to check:  
   - File size limits.  
   - Page count validity.  
   - Minimum text length per page.

5. **Extract italic text and primer sequences**  
   Extract content via `PyMuPDF (fitz)` and regex patterns:  
   - **Italic text**: Identify text with italic formatting.  
   - **Primer sequences**: Match sequences using regular expressions.

6. **Process PDF files**  
   Run `process_pdf_files` to:  
   - Accept input (PDF list, output directory, optional parameters like `root`).  
   - Validate files.  
   - Extract DOI, italic text, and primer sequences.  
   - Write results to `summary.tsv`.

7. **Execute the main program**  
   In `__main__`:  
   - Set input file path and output directory.  
   - Call `process_pdf_files` to generate the final output.

```bash
python scripts/pdf_search_v7.py
```

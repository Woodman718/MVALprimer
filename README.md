# SCI_HUB Processing
This repository contains scripts and data for processing SCI_HUB data, including checking compressed files, generating file paths, and extracting summaries from PDFs.
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

Below is the flowchart of the SCI_HUB processing steps:

![SCI_HUB Processing Flowchart](./docs/SCI_HUB_Processing_Flowchart.png)

This flowchart provides a visual representation of the steps involved in processing SCI_HUB data, from uploading the initial files to extracting primer sequences from PDFs.

## Scripts

### 1. Checking SCI_HUB Compressed Files

- **echo_num.sh**: Counts the number of files in subdirectories.
- **move_file.sh**: Moves files based on certain criteria.

### 2. From scimag.sql to file_path.txt

- **Sql_cnn.py**: Connects to the MySQL database and generates `data.tsv`.
- **Doi_Percent.py**: Calculates the percentage of matching DOIs.
- **ConstureZip.py**: Generates the list of zip files to extract.
- **mv_unzip.py**: Moves and extracts the required zip files.
- **zip_ex.sh**: Extracts zip files.
- **map_files.py**: Generates the list of PDF files to process.

### 3. From PDF to summary.tsv

- **pdf_search_v7.py**: Extracts information from PDFs and generates `summary.tsv`.

## Usage

### Step 1: Check SCI_HUB Compressed Files

```bash
./scripts/echo_num.sh gao/mqi_1/
./scripts/move_file.sh gao/mqi_1/ .
```

### Step 2: From scimag.sql to file_path.txt

1. **Install MySQL and import scimag.sql**

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

```bash
python scripts/pdf_search_v7.py
```

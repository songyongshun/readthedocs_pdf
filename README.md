# GPAW Documentation Downloader and PDF Creator 
This Python script downloads the entire documentation from the GPAW read-the-docs website, converts each page into a PDF file, and then merges them into one comprehensive PDF with a table of contents. 
## Requirements 
- Python 3.x 
- BeautifulSoup4 (`pip install beautifulsoup4`) 
- requests (`pip install requests`) 
- pdfkit (`pip install pdfkit`) - Note: This also requires wkhtmltopdf installed on your system. 
- PyPDF2 (`pip install PyPDF2`) 

## Usage 
1. Install all the requirements listed above. 
2. Run the script using `python html2pdf.py` in your command line interface. 
3. The script will automatically download, convert, and merge the documentation into a single PDF file named after the book. This file will be saved in the same directory as the script. 
## Features 
- Downloads the entire documentation from the specified base URL. 
- Creates individual PDF files for each chapter/section. 
- Merges all individual PDFs into one complete PDF with a table of contents/bookmarks. 
- Handles multi-level sections (chapters with sub-chapters). 
## Notes 
- Ensure that you have `wkhtmltopdf` installed on your system. It can be downloaded from [wkhtmltopdf.org](https://wkhtmltopdf.org/downloads.html). 
- This script was tested on Windows but should work on other platforms with minor modifications. 

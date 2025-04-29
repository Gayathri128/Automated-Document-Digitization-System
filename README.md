# Automated Document Digitization System

This project digitizes handwritten documents by:
- Extracting text and saving it as a PDF.
- Extracting tables (like attendance sheets) and saving them as Excel files.

It uses **Google Cloud Vision API** for text extraction and **AWS Textract** for table extraction.

---

##  Features

- Extract handwritten text from images and download as editable PDF.
- Extract tabular data (attendance sheets) and download as Excel.
- Preprocessing images to improve OCR accuracy.
- Attendance counting from extracted sheets.

---

## 🛠 Installation

First, install the required Python libraries:

```bash
pip install streamlit opencv-python numpy pillow google-cloud-vision fpdf boto3 pandas xlsxwriter

 Cloud Vision (for pdf_app.py)
1.Go to Google Cloud Console.

2.Create a new project.

3.Enable Vision API.

4.Create a Service Account and download the JSON credentials file.

5.Set the environment variable:
export GOOGLE_APPLICATION_CREDENTIALS="path/to/your/credentials.json"
(Use Command Prompt or Git Bash to set environment variables.)


AWS Textract (for excel_app.py)
1.Create an account at AWS Management Console.

2.Navigate to IAM (Identity and Access Management).

3.Create a user with programmatic access and permissions for Textract.

4.Install and configure AWS CLI:

aws configure
(Provide your Access Key ID, Secret Access Key, Region, and output format.)

Running the Applications
1.To Run PDF Text Extractor:

streamlit run pdf_app.py
2.To Run Excel Table Extractor:
 
streamlit run excel_app.py

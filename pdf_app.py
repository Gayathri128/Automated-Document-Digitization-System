import io
import cv2
import numpy as np
from google.cloud import vision
from PIL import Image
import streamlit as st

# Google Vision OCR function with language hints
def detect_text_google_vision(image_content):
    client = vision.ImageAnnotatorClient()

    # Specify the language hint (adjust as per your requirements)
    image_context = vision.ImageContext(language_hints=["en"])  # You can change "en" to other language codes if needed
    image = vision.Image(content=image_content)

    # Use document_text_detection with language hints for better accuracy
    response = client.document_text_detection(image=image, image_context=image_context)

    if response.error.message:
        raise Exception(f"Google Vision Error: {response.error.message}")

    full_text = []
    for page in response.full_text_annotation.pages:
        for block in page.blocks:
            for paragraph in block.paragraphs:
                paragraph_text = ""
                for word in paragraph.words:
                    word_text = ''.join([symbol.text for symbol in word.symbols])
                    paragraph_text += word_text + " "
                full_text.append(paragraph_text.strip())

    return '\n'.join(full_text)

# Image Preprocessing function (Advanced)
def preprocess_image(image):
    # Convert PIL image to OpenCV format (numpy array)
    img = np.array(image)

    # Convert image to grayscale
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # Resize the image for better OCR accuracy (optional but useful for low-res images)
    height, width = gray.shape
    gray = cv2.resize(gray, (width * 2, height * 2))

    # Apply adaptive thresholding to make the text stand out
    processed_img = cv2.adaptiveThreshold(
        gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2
    )

    # Use GaussianBlur to reduce noise
    processed_img = cv2.GaussianBlur(processed_img, (5, 5), 0)

    return processed_img

# Function to convert OpenCV image to bytes for Google Vision API
def image_to_bytes(image):
    is_success, buffer = cv2.imencode(".png", image)
    io_buf = io.BytesIO(buffer)
    return io_buf.getvalue()

# Main function to handle image upload and processing
def main():
    st.title("AUTOMATED DOCUMENT DIGITIZATION SYSTEM- PDF")

    uploaded_image = st.file_uploader("Upload an Image for Text Extraction", type=["png", "jpg", "jpeg"])

    if uploaded_image is not None:
        # Load image using PIL (streamlit gives a file-like object)
        pil_image = Image.open(uploaded_image)

        # Display uploaded image before processing
        st.image(pil_image, caption="Uploaded Image", use_column_width=True)

        # Preprocess image (advanced preprocessing for better accuracy)
        processed_image = preprocess_image(pil_image)

        # Convert preprocessed image to bytes for Google Vision API
        image_bytes = image_to_bytes(processed_image)

        # Extract text using Google Vision OCR with language hints
        st.info("Extracting text, please wait...")  # Let the user know the process has started
        extracted_text = detect_text_google_vision(image_bytes)

        # Display the extracted text
        st.subheader("Extracted Text:")
        st.text(extracted_text)

        # Allow users to edit the text if needed
        edited_text = st.text_area("Edit the extracted text", extracted_text)

        # Provide download option for the edited text as PDF
        if st.button("Download as PDF"):
            download_pdf(edited_text)

# Function to download edited text as a PDF
from fpdf import FPDF

def download_pdf(text):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.set_font("Arial", size=12)

    for line in text.split('\n'):
        pdf.multi_cell(0, 10, line)

    pdf_output = pdf.output(dest="S").encode('latin1')
    st.download_button(label="Download PDF", data=pdf_output, file_name="extracted_text.pdf", mime="application/pdf")

if __name__ == "__main__":
    main()
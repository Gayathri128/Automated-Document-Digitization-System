import streamlit as st
import boto3
import pandas as pd
import io

# Function to call Amazon Textract and extract table data
def extract_table_with_textract(image_path):
    # Initialize Textract client
    client = boto3.client('textract')

    # Read image bytes
    with open(image_path, 'rb') as document:
        image_bytes = document.read()

    # Call Amazon Textract to detect tables in the image
    response = client.analyze_document(
        Document={'Bytes': image_bytes},
        FeatureTypes=["TABLES"]
    )
    
    # Parse the Textract response to extract table cells
    blocks = response['Blocks']
    table_data = {}
    
    for block in blocks:
        if block['BlockType'] == 'CELL':
            row = block['RowIndex']
            col = block['ColumnIndex']
            text = ""
            if 'Relationships' in block:
                for relationship in block['Relationships']:
                    if relationship['Type'] == 'CHILD':
                        for child_id in relationship['Ids']:
                            child_block = next((item for item in blocks if item['Id'] == child_id), None)
                            if child_block and 'Text' in child_block:
                                text += child_block['Text'] + " "
            
            if row not in table_data:
                table_data[row] = {}
            table_data[row][col] = text.strip()

    # Ensure all columns are captured correctly without merging or shifting
    max_cols = max(max(row.keys()) for row in table_data.values())

    df_rows = []
    for row in sorted(table_data.keys()):
        df_row = [table_data[row].get(col, '') for col in range(1, max_cols + 1)]
        df_rows.append(df_row)

    df = pd.DataFrame(df_rows)

    # Function to split combined values correctly
    def split_combined_values(row):
        new_row = []
        for val in row:
            if len(val) > 1 and all(char in "P/A" for char in val):
                new_row.extend(list(val))  # Split values into separate columns
            else:
                new_row.append(val)
        return new_row

    # Expand data if columns were merged
    expanded_data = [split_combined_values(row) for _, row in df.iterrows()]
    max_len = max(len(row) for row in expanded_data)
    expanded_df = pd.DataFrame([row + [''] * (max_len - len(row)) for row in expanded_data])

    return expanded_df

# Function to count present and absent entries in a specified column
def count_present_absent(df, column):
    present_count = df[column].astype(str).str.contains(r'[/P]', regex=True, na=False).sum()
    absent_count = df[column].astype(str).str.contains(r'[aA]', regex=True, na=False).sum()
    return present_count, absent_count

# Function to save DataFrame to an Excel file
def save_to_excel(df):
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False)
    return output.getvalue()

# Streamlit app to handle image upload and table extraction
def main():
    st.title("Automated Document Digitization System-Excel")
    st.write("Upload an image of an attendance sheet, extract table data, edit it, and download as an Excel file.")

    uploaded_file = st.file_uploader("📤 Upload Image (PNG, JPG, JPEG)", type=["png", "jpg", "jpeg"])

    if uploaded_file:
        # Save the uploaded image locally
        image_path = uploaded_file.name
        with open(image_path, "wb") as f:
            f.write(uploaded_file.getbuffer())

        # Display the uploaded image
        st.image(image_path, caption="🖼 Uploaded Image", use_column_width=True)

        # Extract table using Textract
        df = extract_table_with_textract(image_path)

        if df.empty:
            st.error("⚠️ No table detected! Please upload a clearer image.")
        else:
            # Display extracted table with editing option
            st.write("📋 **Extracted Table Data (Editable):**")
            edited_df = st.data_editor(df, num_rows="dynamic", use_container_width=True)

            # Select column for attendance count
            if len(edited_df.columns) > 3:
                date_columns = edited_df.columns[3:]  # Exclude first 3 columns (Name, Register Number, etc.)
                selected_column = st.selectbox("📅 Select a date column for attendance count", date_columns)

                if selected_column:
                    present_count, absent_count = count_present_absent(edited_df, selected_column)
                    st.write(f"✅ **Present Count in '{selected_column}':** {present_count}")
                    st.write(f"❌ **Absent Count in '{selected_column}':** {absent_count}")

            # Save edited data to Excel
            excel_data = save_to_excel(edited_df)

            # Download button for Excel file
            st.download_button(
                label="📥 Download Excel",
                data=excel_data,
                file_name="attendance_sheet.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )

if __name__ == "__main__":
    main()
import streamlit as st
import os
import pandas as pd
from gpt import generate_text_to_image
from PIL import Image
from io import BytesIO
import zipfile

ROOT_SAVE_FOLDER = "saved_folders"
os.makedirs(ROOT_SAVE_FOLDER, exist_ok=True)

def login_page():
   
    # Input fields for username and password
    _, col2, _ = st.columns([0.5, 1, 0.5])
    with col2:
        st.title("Login")

        username = st.text_input("Username")
        password = st.text_input("Password", type="password")

        if st.button("Login"):
            
            if username == st.secrets['UNAME'] and password == st.secrets['PASSWD']:
                st.session_state.logged_in = True
                st.success("Login successful!")
                st.rerun()  # Refresh the page after login
            else:
                st.error("Invalid username or password. Please try again.")

# Helper function to save prompt and image info in a CSV file
def save_prompt_image(prompt, age, resolution, img_path, folder):
    with open(os.path.join(folder, "prompts.csv"), "a") as f:
        f.write(f"{prompt},{age},{resolution},{img_path}\n")

# Helper function to load saved data (prompts and images)
def load_saved_data(folder_path):
    csv_path = os.path.join(folder_path, "prompts.csv")
    if os.path.exists(csv_path):
        data = pd.read_csv(csv_path, header=None, names=["Prompt", "Age", "Resolution", "Image_Path"])
        return data
    return pd.DataFrame(columns=["Prompt", "Age", "Resolution", "Image_Path"])

# Helper function to delete a prompt-image pair
def delete_prompt_image(image_path, data, index, folder):
    if os.path.exists(image_path):
        os.remove(image_path)  # Delete the image file
    data = data.drop(index)  # Remove the entry from the dataframe
    data.to_csv(os.path.join(folder, "prompts.csv"), header=False, index=False)  # Update CSV
    st.success(f"Deleted {image_path}")

# Helper function to delete a folder
def delete_folder(folder_name):
    folder_path = os.path.join(ROOT_SAVE_FOLDER, folder_name)
    if os.path.exists(folder_path):
        for file in os.listdir(folder_path):
            os.remove(os.path.join(folder_path, file))
        os.rmdir(folder_path)
        st.success(f"Folder '{folder_name}' deleted successfully!")

# Page: Create Folder
def create_folder_page():
    _, col1, _ = st.columns([0.5, 1, 0.5])
    with col1:
        st.title("Create a New Folder")
        new_folder_name = st.text_input("Enter folder name:")
        if st.button("Create Folder"):
            if new_folder_name:
                new_folder_path = os.path.join(ROOT_SAVE_FOLDER, new_folder_name)
                os.makedirs(new_folder_path, exist_ok=True)
                st.success(f"Folder '{new_folder_name}' created successfully!")
            else:
                st.warning("Please enter a folder name.")

# Function to convert image to bytes for downloading
def get_image_bytes(image_path):
    img = Image.open(image_path)
    img_byte_arr = BytesIO()
    img.save(img_byte_arr, format='PNG')  # You can change the format if needed
    img_byte_arr = img_byte_arr.getvalue()
    return img_byte_arr


def create_zip_from_folder(saved_data):
    zip_buffer = BytesIO()
    with zipfile.ZipFile(zip_buffer, "w") as zip_file:
        for _, row in saved_data.iterrows():
            image_path = row["Image_Path"]
            img_name = os.path.basename(image_path)  # Get the image file name
            zip_file.write(image_path, img_name)  # Add image to zip
    zip_buffer.seek(0)  # Move the buffer position to the beginning
    return zip_buffer

# Page: View Folder and Items
def view_folder_page():
    
    _, col1, _ = st.columns([0.7, 1, 0.5])
    with col1:
        st.title("View Folders and Items")

    folders = [f for f in os.listdir(ROOT_SAVE_FOLDER) if os.path.isdir(os.path.join(ROOT_SAVE_FOLDER, f))]
    
    # Display folders as clickable buttons
    columns_per_row = 8
    
    # Display folders as clickable buttons, with 8 buttons per row
    for i in range(0, len(folders), columns_per_row):
        cols = st.columns(columns_per_row)  # Create 8 columns
        for j, folder in enumerate(folders[i:i + columns_per_row]):
            with cols[j]:
                if st.button(f"📂 {folder}"):
                    st.session_state.selected_folder = folder

    if "selected_folder" in st.session_state:
        folder = st.session_state.selected_folder
        st.subheader(f"Viewing Folder: {folder}")
        
        current_folder = os.path.join(ROOT_SAVE_FOLDER, folder)
        saved_data = load_saved_data(current_folder)
        
        if not saved_data.empty:
            columns_per_row = 4  # Display 4 images per row
            for i in range(0, len(saved_data), columns_per_row):
                cols = st.columns(columns_per_row)  # Create 4 columns
                for j, (index, row) in enumerate(saved_data.iloc[i:i + columns_per_row].iterrows()):
                    with cols[j]:  # Ensure each image and button are in the same column
                        # Display the image
                        st.image(row["Image_Path"], caption=f"Prompt: {row['Prompt']} (Age: {row['Age']}, Resolution: {row['Resolution']})", width=300)
                        
                        image_bytes = get_image_bytes(row["Image_Path"])
                        
                        
                        col21, col22, _ = st.columns([1, 1, 1])
                        with col21:
                            st.download_button(
                                label="Download",
                                data=image_bytes,
                                file_name=f"image_{index + 1}.png",  # You can customize the file name
                                mime="image/png"
                            )
                        with col22:
                            # Align the button at the bottom of the container
                            if st.button(f"🗑️ Delete", key=f"delete_{index}"):
                                delete_prompt_image(row["Image_Path"], saved_data, index, current_folder)
                                st.rerun()  # Refresh after deletion

            st.write('')
            st.write('')
            st.write('')
            
            zip_buffer = create_zip_from_folder(saved_data)
            st.download_button(
                label="Download Folder",
                data=zip_buffer,
                file_name=f"{current_folder}.zip",
                mime="application/zip"
            )
        else:
            st.write("No images in this folder.")
        
        # Button to delete the folder
        if st.button(f"🗑️ Delete Folder"):
            delete_folder(folder)
            del st.session_state.selected_folder
            st.rerun()

# Page: Add Item (Generate Image)
def add_item_page():
    if "selected_folder" not in st.session_state:
        st.warning("Please select a folder from 'View Folder' page.")
        return

    _, col1, _ = st.columns([0.7, 1, 0.5])
    with col1:
        st.title(f"Add Item to Folder: {st.session_state.selected_folder}")

    age = st.selectbox("Select Age Group:", ["child", "teen", "adult"])
    prompt = st.text_input("Enter the image prompt:")
    resolution = st.selectbox("Select Expected Resolution:", ["1024x1024", "1024x1792", "1792x1024"])

    if st.button("Generate Image"):
        if prompt:
            folder = os.path.join(ROOT_SAVE_FOLDER,st.session_state.selected_folder)
            img_path = generate_text_to_image(prompt, age, resolution, folder)
            save_prompt_image(prompt, age, resolution, img_path, folder)
            st.image(img_path, caption="Generated Image", width=600)
            st.success(f"Image generated and saved in folder: {folder}")
        else:
            st.warning("Please enter a prompt.")

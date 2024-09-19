import streamlit as st
import os
import pandas as pd
from gpt import generate_text_to_image


ROOT_SAVE_FOLDER = "saved_folders"
os.makedirs(ROOT_SAVE_FOLDER, exist_ok=True)

def login_page():
    st.title("Login")

    # Input fields for username and password
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
    st.title("Create a New Folder")

    new_folder_name = st.text_input("Enter folder name:")
    if st.button("Create Folder"):
        if new_folder_name:
            new_folder_path = os.path.join(ROOT_SAVE_FOLDER, new_folder_name)
            os.makedirs(new_folder_path, exist_ok=True)
            st.success(f"Folder '{new_folder_name}' created successfully!")
        else:
            st.warning("Please enter a folder name.")

# Page: View Folder and Items
def view_folder_page():
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
                cols = st.columns(columns_per_row)
                for j, (index, row) in enumerate(saved_data.iloc[i:i + columns_per_row].iterrows()):
                    with cols[j]:
                        st.image(row["Image_Path"], caption=f"Prompt: {row['Prompt']} (Age: {row['Age']}, Resolution: {row['Resolution']})", width=300)
                        if st.button(f"🗑️ Delete Image {index + 1}", key=f"delete_{index}"):
                            delete_prompt_image(row["Image_Path"], saved_data, index, current_folder)
                            st.rerun()  # Refresh after deletion
        else:
            st.write("No images in this folder.")
        
        # Button to delete the folder
        if st.button(f"🗑️ Delete Folder '{folder}'"):
            delete_folder(folder)
            del st.session_state.selected_folder
            st.rerun()

# Page: Add Item (Generate Image)
def add_item_page():
    if "selected_folder" not in st.session_state:
        st.warning("Please select a folder from 'View Folder' page.")
        return

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

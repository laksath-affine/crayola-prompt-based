import streamlit as st
import os
from PIL import Image
import pandas as pd
from gpt import generate_text_to_image

# Set page layout to occupy full width
st.set_page_config(layout="wide")

ROOT_SAVE_FOLDER = "saved_folders"
os.makedirs(ROOT_SAVE_FOLDER, exist_ok=True)

# Session state management for selected folder
if "selected_folder" not in st.session_state:
    st.session_state.selected_folder = None

# Helper function to generate an image (placeholder)
def generate_dalle_image(selected_folder, exp_prompt_text: str = '', age: str = 'child', exp_resolution: str = '1024x1024'):
    return generate_text_to_image(exp_prompt_text, age, exp_resolution, selected_folder)

# Function to save prompt and image info in a CSV file
def save_prompt_image(prompt, age, resolution, img_path):
    with open(os.path.join(st.session_state.selected_folder, "prompts.csv"), "a") as f:
        f.write(f"{prompt},{age},{resolution},{img_path}\n")

# Function to load saved data (prompts and images) from the selected folder
def load_saved_data(folder_path):
    csv_path = os.path.join(folder_path, "prompts.csv")
    if os.path.exists(csv_path):
        data = pd.read_csv(csv_path, header=None, names=["Prompt", "Age", "Resolution", "Image_Path"])
        return data
    else:
        return pd.DataFrame(columns=["Prompt", "Age", "Resolution", "Image_Path"])

# Function to delete a prompt-image pair
def delete_prompt_image(image_path, data, index):
    if os.path.exists(image_path):
        os.remove(image_path)  # Delete the image file
    data = data.drop(index)  # Remove the entry from the dataframe
    data.to_csv(os.path.join(st.session_state.selected_folder, "prompts.csv"), header=False, index=False)  # Update CSV
    st.success(f"Deleted {image_path}")

# Function to delete a folder
def delete_folder(folder_name):
    folder_path = os.path.join(ROOT_SAVE_FOLDER, folder_name)
    if os.path.exists(folder_path):
        for file in os.listdir(folder_path):
            os.remove(os.path.join(folder_path, file))
        os.rmdir(folder_path)
        st.success(f"Folder '{folder_name}' deleted successfully!")

# Streamlit UI
st.title("Prompt-based Image Generation Application")

# Section to create new folder
st.header("1. Create New Folder")
new_folder_name = st.text_input("Enter folder name:")
if st.button("Create Folder"):
    if new_folder_name:
        new_folder_path = os.path.join(ROOT_SAVE_FOLDER, new_folder_name)
        os.makedirs(new_folder_path, exist_ok=True)
        st.success(f"Folder '{new_folder_name}' created successfully!")
        st.session_state.selected_folder = new_folder_name
    else:
        st.warning("Please enter a folder name.")

# Section to view folders as clickable buttons
st.header("2. View Folders and Items")
folders = [f for f in os.listdir(ROOT_SAVE_FOLDER) if os.path.isdir(os.path.join(ROOT_SAVE_FOLDER, f))]

if folders:
    for folder in folders:
        if st.button(f"📂 {folder}"):
            st.session_state.selected_folder = folder

if st.session_state.selected_folder:
    st.subheader(f"Folder: {st.session_state.selected_folder}")
    
    # Show folder contents (prompts and images)
    current_folder = os.path.join(ROOT_SAVE_FOLDER, st.session_state.selected_folder)
    saved_data = load_saved_data(current_folder)
    
    if not saved_data.empty:
        for index, row in saved_data.iterrows():
            st.image(row["Image_Path"], caption=f"Prompt: {row['Prompt']} (Age: {row['Age']}, Resolution: {row['Resolution']})", use_column_width=True)
            if st.button(f"🗑️ Delete Image {index + 1}", key=f"delete_{index}"):
                delete_prompt_image(row["Image_Path"], saved_data, index)
                st.rerun()  # Refresh after deletion
    else:
        st.write("No images in this folder.")

    # Delete folder button
    if st.button(f"🗑️ Delete Folder '{st.session_state.selected_folder}'"):
        delete_folder(st.session_state.selected_folder)
        st.session_state.selected_folder = None
        st.rerun()

# Section to add new items (prompts and images)
if st.session_state.selected_folder:
    st.header(f"3. Add Item to Folder '{st.session_state.selected_folder}'")
    
    age = st.selectbox("Select Age Group:", ["child", "teen", "adult"])
    prompt = st.text_input("Enter the image prompt:")
    resolution = st.selectbox("Select Expected Resolution:", ["1024x1024", "1024x1792", "1792x1024"])

    if st.button("Generate Image"):
        if prompt:
            img_path = generate_dalle_image(st.session_state.selected_folder, prompt, age, resolution)
            save_prompt_image(prompt, age, resolution, img_path)
            st.image(img_path, caption="Generated Image", use_column_width=True)
            st.success(f"Image generated and saved in folder: {st.session_state.selected_folder}")
        else:
            st.warning("Please enter a prompt.")

import streamlit as st
import os
from PIL import Image
import pandas as pd
from gpt import generate_text_to_image

ROOT_SAVE_FOLDER = "saved_folders"
os.makedirs(ROOT_SAVE_FOLDER, exist_ok=True)

# Helper function to generate an image (placeholder)
def generate_dalle_image(selected_folder, exp_prompt_text: str = '', age: str = 'child', exp_resolution: str = '1024x1024'):
    return generate_text_to_image(exp_prompt_text, age, exp_resolution, selected_folder)

# Function to save prompt and image info in a CSV file
def save_prompt_image(prompt, age, resolution, img_path):
    with open(os.path.join(current_folder, "prompts.csv"), "a") as f:
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
    data.to_csv(os.path.join(current_folder, "prompts.csv"), header=False, index=False)  # Update CSV
    st.success(f"Deleted {image_path}")

# Streamlit UI
st.title("Prompt-based Image Generation Application")

# Home page - List all folders and option to create new folder
st.header("Home - Select or Create Folder")

# List existing folders
folders = [f for f in os.listdir(ROOT_SAVE_FOLDER) if os.path.isdir(os.path.join(ROOT_SAVE_FOLDER, f))]
selected_folder = st.selectbox("Select a folder:", folders)

# Option to create a new folder
new_folder_name = st.text_input("Create a new folder (enter name):")
if st.button("Create Folder"):
    if new_folder_name:
        new_folder_path = os.path.join(ROOT_SAVE_FOLDER, new_folder_name)
        os.makedirs(new_folder_path, exist_ok=True)
        st.success(f"Folder '{new_folder_name}' created successfully!")
        selected_folder = new_folder_name
    else:
        st.warning("Please enter a folder name.")

if selected_folder:
    # Set the current folder path
    current_folder = os.path.join(ROOT_SAVE_FOLDER, selected_folder)

    # Display all prompt-image sets in the selected folder
    st.header(f"Viewing Folder: {selected_folder}")
    saved_data = load_saved_data(current_folder)
    
    if not saved_data.empty:
        for index, row in saved_data.iterrows():
            st.image(row["Image_Path"], caption=f"Prompt: {row['Prompt']} (Age: {row['Age']}, Resolution: {row['Resolution']})", use_column_width=True)
            if st.button(f"Expand Image {index + 1}", key=f"expand_{index}"):
                st.image(row["Image_Path"], caption=row['Prompt'], use_column_width=True)
            if st.button(f"Delete Image {index + 1}", key=f"delete_{index}"):
                delete_prompt_image(row["Image_Path"], saved_data, index)
                st.experimental_rerun()  # Refresh the page after deletion
    else:
        st.write("No saved images or prompts in this folder.")

    # Option to create a new image in the selected folder
    st.header("Create a New Image")

    age = st.selectbox("Select Age Group:", ["child", "teen", "adult"])
    prompt = st.text_input("Enter the image prompt:")
    resolution = st.selectbox("Select Expected Resolution:", ["1024x1024", "1024x1792", "1792x1024"])

    if st.button("Generate Image"):
        if prompt:
            img_path = generate_dalle_image(selected_folder, prompt, age, resolution)
            save_prompt_image(prompt, age, resolution, img_path)
            st.image(img_path, caption="Generated Image", use_column_width=True)
            st.success(f"Image generated and saved in folder: {selected_folder}")
        else:
            st.warning("Please enter a prompt before generating the image.")

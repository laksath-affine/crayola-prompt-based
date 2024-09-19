import streamlit as st
from utils import create_folder_page, view_folder_page, add_item_page

# Set page layout to occupy full width and include a sidebar
st.set_page_config(layout="wide", page_title="Prompt-based Image Generation")

# Sidebar for navigation
st.sidebar.title("Navigation")
page = st.sidebar.radio("Go to", ["Create Folder", "View Folder", "Add Item"])

# Map sidebar options to pages
if page == "Create Folder":
    create_folder_page()
elif page == "View Folder":
    view_folder_page()
elif page == "Add Item":
    add_item_page()

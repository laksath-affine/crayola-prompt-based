import streamlit as st
from utils import create_folder_page, view_folder_page, add_item_page, login_page

# Set page layout to occupy full width and include a sidebar
st.set_page_config(layout="wide", page_title="Prompt-based Image Generation")

# Initialize session state for login
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

# Sidebar for navigation
if st.session_state.logged_in:
    st.sidebar.title("Navigation")
    page = st.sidebar.radio("Go to", ["Create Folder", "View Folder", "Add Item"])

    # Map sidebar options to pages
    if page == "Create Folder":
        create_folder_page()
    elif page == "View Folder":
        view_folder_page()
    elif page == "Add Item":
        add_item_page()
else:
    login_page()  # If not logged in, show the login page

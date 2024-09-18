from datetime import datetime
from openai import AzureOpenAI
import os
import requests
from PIL import Image
from io import BytesIO
from gpt_prompt_gen import get_text_api_result, generate_dalle_3_image
import base64
import json
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

def generate_coloring_page_child(prompt):
    return (f"Design a very simple, young child-friendly black and white coloring page based on the theme: '{prompt}'. "
            "Ensure the image features clear, well-defined black outlines with no grey shading, making it easy for young children to color within the lines. "
            "All areas intended for coloring should be completely white and free of any pre-filled colors. "
            "Keep the design uncomplicated and engaging, suitable for a 5-year-old. "
            "Every part of the image should be left entirely white, allowing for creative and imaginative coloring.")

def generate_coloring_page_teenager(prompt):
    return (f"Create an enjoyable, child-friendly black and white coloring page based on the theme: '{prompt}'. "
            "The image should feature clear, well-defined black outlines with no grey shading, making it suitable for coloring. "
            "All areas intended for coloring should be left completely white and free of any pre-filled colors. "
            "Incorporate additional detail and complexity into the design, ensuring it is appropriate and engaging for kids aged 12-14, without being overly intricate. "
            "Every part of the image should be left entirely white, allowing for creative and imaginative coloring.")

def generate_coloring_page_adult(prompt):
    return (f"Craft a detailed, adult-friendly black and white coloring page inspired by the theme: '{prompt}'. "
            "The image should feature fine, well-defined black outlines with no grey shading, designed for detailed coloring. "
            "All areas intended for coloring and should be left completely white and free of any pre-filled colors. "
            "Ensure the design is complex and engaging, catering to adults who enjoy detailed and intricate coloring activities. "
            "Every part of the image should be colorable and left entirely white to provide a satisfying and immersive coloring experience.")

def generate_correction_prompt(prompt):
    return f"Correct any grammatical or spelling errors in the following text, and return only the corrected text: {prompt}"

def dalle_text_to_image(prompt, model_name, size):
    client = AzureOpenAI(
        api_key=os.getenv("AZURE_OPENAI_API_KEY"),  
        api_version="2024-02-01",
        azure_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
    )

    response = client.images.generate(
        model=model_name, #"dall-e-3"
        prompt=prompt,
        size=size,
        quality="standard",
        n=1
    )
    
    image_url = response.data[0].url
    return image_url

def fetch_and_convert_image(file_path):
    """
    Read an image from the local file system, convert it to greyscale, and return the greyscale image.

    :param file_path: The path to the image file on the local file system.
    :return: The greyscale image.
    """
    try:
        image = Image.open(file_path)

        grey_image = image.convert('L')
        grey_image.save(file_path)
        
        print("Conversion Complete")
        
        return grey_image
    except IOError as e:
        print(f"Failed to open or convert image: {e}")
        return None

def get_filename(output_path, model_name, age):
    if not os.path.exists(output_path):
        os.makedirs(output_path)
        print(f'Created output path:{output_path}')
        
    time_str = f"{datetime.now().strftime('%Y%m%d-%H%M%S')}"
    filename = f'{output_path}/{time_str}_{model_name}_{age}.png'
    return filename
      
def save_image_from_url(url, file_name):
    try:
        response = requests.get(url)
        response.raise_for_status()  # Check if the request was successful
        image = Image.open(BytesIO(response.content))
        image.save(file_name)
        
        print(f"Image saved as {file_name}")
    except requests.exceptions.RequestException as e:
        print(f"Failed to retrieve image: {e}")
    except IOError as e:
        print(f"Failed to save image: {e}")
    print()

def generate_text_to_image(prompt, age, size, output_folder):
    print(prompt, age, size)
    
    correction_prompt = generate_correction_prompt(prompt)
    corrected_prompt = get_text_api_result(correction_prompt)
    
    if age=='adult':
        coloring_page_prompt = generate_coloring_page_adult(corrected_prompt)
    elif age=='teen':
        coloring_page_prompt = generate_coloring_page_teenager(corrected_prompt)
    else:
        coloring_page_prompt = generate_coloring_page_child(corrected_prompt)
    
    model_name = 'aicoe_dalle3'
    output_url = generate_dalle_3_image(coloring_page_prompt, model_name, size)
  
    print(f"Original Prompt: {prompt}\n")
    print(f"Correction Prompt: {correction_prompt}\n")
    print(f"GPT4's Corrected Prompt: {corrected_prompt}\n")
    print(f"Coloring Page Prompt: {coloring_page_prompt}\n")
    filename = get_filename(output_folder, model_name, age)
    print(f"filename: {filename}")
    
    save_image_from_url(output_url, filename)
    fetch_and_convert_image(filename)
    
    return filename
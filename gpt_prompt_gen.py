import os
from openai import AzureOpenAI
import streamlit as st

completion_client = AzureOpenAI(
    azure_endpoint = st.secrets["AZURE_OPENAI_AI_PRACTICES_ENDPOINT"],
    api_key = st.secrets['AZURE_OPENAI_AI_PRACTICES_API_KEY'],
    api_version = "2024-02-01"
)

dalle_client = AzureOpenAI(
    azure_endpoint = st.secrets["AZURE_OPENAI_ALLBIRDS_ENDPOINT"],
    api_key = st.secrets['AZURE_OPENAI_ALLBIRDS_API_KEY'],
    api_version = "2024-02-01"
)

def create_message_text(question):
    return [
    {
        "role":"system",
        "content":"You are an AI assistant that helps people find information."
    },
    {
            "role": "user",
            "content": question
    }
        ]

def get_text_api_result(question):
    completion = completion_client.chat.completions.create(
    #   model="gpt-4o-05-13",
      model="gpt-4o-08-06",
      messages = create_message_text(question),
      temperature=0.7,
    #   max_tokens=3000,
      top_p=0.95,
      frequency_penalty=0,
      presence_penalty=0,
      stop=None
    )
    return completion.choices[0].message.content

def generate_dalle_3_image(prompt, model_name, size):
    response = dalle_client.images.generate(
        model=model_name,
        prompt=prompt,
        size=size,
        quality="standard",
        n=1
    )
    
    image_url = response.data[0].url
    return image_url
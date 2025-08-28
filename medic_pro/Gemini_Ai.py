import os
from .credentials import gemini_api_key
import google.generativeai as genai
from .files_reading import read_file
from doctor.models import *
from .Ai_Tasks import *
from .appointment_instructions import SHOW_DOCTORS_TABLE_TO_USER, FIX_APOINTMENT_DETAILS
genai.configure(api_key=gemini_api_key)
# Create the model
generation_config = {
  "temperature": 1,
  "top_p": 0.95,
  "top_k": 64,
  "max_output_tokens": 500,
  "response_mime_type": "text/plain",
}
safety_settings = [
  {
    "category": "HARM_CATEGORY_HARASSMENT",
    "threshold": "BLOCK_MEDIUM_AND_ABOVE",
  },
  {
    "category": "HARM_CATEGORY_HATE_SPEECH",
    "threshold": "BLOCK_MEDIUM_AND_ABOVE",
  },
  {
    "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
    "threshold": "BLOCK_MEDIUM_AND_ABOVE",
  },
  {
    "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
    "threshold": "BLOCK_MEDIUM_AND_ABOVE",
  },
]

model = genai.GenerativeModel(
  model_name="gemini-1.5-flash-latest",
  safety_settings=safety_settings,
  generation_config=generation_config,
)

chat_session = model.start_chat(
  history=[ ]
)

def get_ai_response(prompt):
    data = read_file("./medic_pro/data_set.json")
    instructions = read_file("./medic_pro/instructions.json")
    combined_prompt = f"""
    You are chatbot assistant of Medic-Pro. Here is some important information:
    {data}
    Please follow these instructions:
    {instructions}
    Now, here is the user's question: 
    {prompt}
    """
    response = chat_session.send_message(combined_prompt)
    response = response.text
    if "User_Selected: " in response:
      print(response)
      print("Send Doctors Data to AI.")
      response = response.replace("User_Selected: ","")
      response = response.replace(" ","")
      print(response)
      response = response.replace("<br>","")
      print(response)
      data, found = find_doctors_by_specialization(response.strip())
      print(data, found)
      if found:
         newResponse = chat_session.send_message(f"{SHOW_DOCTORS_TABLE_TO_USER} \n {data} \n {FIX_APOINTMENT_DETAILS}")
         response = newResponse.text
         response.replace("```html", '')
         response.replace("```", '')
      else:
         response = "Sorry, we couldn't find any doctors matching your criteria."
    return response
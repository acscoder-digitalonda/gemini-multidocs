import os
import google.generativeai as genai
from dotenv import load_dotenv
load_dotenv()
import streamlit as st
from gdocs import gdocs
 

GOOGLE_API_KEY = st.secrets('GOOGLE_API_KEY')

genai.configure(api_key=GOOGLE_API_KEY)

def messages_to_text(messages):
    text = ""
    for message in messages:
        text += message["role"] + ": " + message["content"] + "\n"
    return text
def send_llm(prompt,data):
    last_prompt = st.session_state.the_last_prompt
    last_reply = st.session_state.the_last_reply
    system_prompting = "You are a helpful assistant."
    if len(data):
        system_prompting += "Based on these "+str(len(data))+" documents provided below, please complete the task requested by the user:" 
        c = 0
        for title,chunk in data:
            c += 1
            system_prompting += "\n\n"
            system_prompting += "Document #"+str(c)+" :"+title
            system_prompting += "\n\n"
            system_prompting += "\n\n".join(chunk)
            system_prompting += "--------------------------------------------------"
            system_prompting += "\n\n"

    chat_model = genai.GenerativeModel('gemini-pro')
    
    our_sms = []
    our_sms.append({"role": "system", "content": system_prompting })
    if last_prompt != "":
        our_sms.append( {"role": "user", "content": last_prompt})
    if last_reply != "":
        our_sms.append( {"role": "assistant", "content": last_reply})
    our_sms.append( {"role": "user", "content": prompt})

     
    response = chat_model.generate_content(messages_to_text(our_sms))
    return response.text

def get_gdoc(url):
    creds = gdocs.gdoc_creds()
    document_id = gdocs.extract_document_id(url)
    chunks = gdocs.read_gdoc_content(creds,document_id)
    title = gdocs.read_gdoc_title(creds,document_id)
    return document_id,title,chunks

 
with st.sidebar:
  doc_url = st.text_input("Enter your Gooogle Docs url:")
  submit_button = st.button("Add Document")
  st.subheader("Select Your Docs")

  if not "all_docs" in st.session_state:
        st.session_state.all_docs = {}
  all_docs = st.session_state.all_docs

  if submit_button:
    document_id,title,chunks = get_gdoc(doc_url)
    all_docs[document_id] = (title,chunks)
    st.session_state.all_docs = all_docs 
     
    
  doc_options = st.multiselect(
    'Select Your Docs',
    all_docs.keys(),
    format_func = lambda x: all_docs[x][0] if x in all_docs else x,
    )
if not "the_last_reply" in st.session_state:
    st.session_state.the_last_reply = ""
if not "the_last_prompt" in st.session_state:
    st.session_state.the_last_prompt = ""
        
your_prompt = st.chat_input ("Enter your Prompt:" ) 

if your_prompt:
    data = []
    for doc in doc_options:
        data.append(all_docs[doc])
    st.session_state.the_last_prompt = your_prompt
    response = send_llm(your_prompt,data)
    st.session_state.the_last_reply = response
    st.write(response)

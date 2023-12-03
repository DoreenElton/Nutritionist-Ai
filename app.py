import streamlit as st
from openai import OpenAI
import requests

# Set the title of the page

st.set_page_config(
    page_title="Nutritionist AI",
    page_icon="👨‍⚕️🍎")

st.title("Nutritionist AI 👨‍⚕️🍎")

# Set the API key
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

# Set a default model
if "openai_model" not in st.session_state:
    st.session_state["openai_model"] = "gpt-3.5-turbo"

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("e.g. How many calories are in Fried Rice?"):

    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

     ## --- Prelimenary work for added nutrition facts --- ##
    api_url = 'https://api.api-ninjas.com/v1/nutrition?query={}'.format(prompt)
    response_nutritional = requests.get(api_url, headers={'X-Api-Key': st.secrets["APININJA_API_KEY"]})

    if response_nutritional.status_code == requests.codes.ok:
        prompt += response_nutritional.text
    else:
        prompt += "\n No data available on that."

    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""
        for response in client.chat.completions.create(
                model=st.session_state["openai_model"],
                messages=[{
                    "role": "system",
                    "content":'''You are a nutrition-focused AI chatbot. Your primary purpose is to provide information and answer questions related to nutrition, diet, and fitness. Please adhere to these guidelines when generating responses.

                            1. **Focus on Nutrition:** Ensure that your responses are centered around topics related to nutrition, diet plans, healthy eating, and fitness.

                            2. **Default Response:** If a user asks a question that falls outside the scope of nutrition and fitness or is something you genuinely don't have information about, reply with the following default response:
                                - "I currently have no information about that."

                            3. **Disclaimer:** Whenever you are providing information, especially on sensitive or important topics, include the following disclaimer:
                                - "\nDisclaimer: I am an AI chatbot and not a professional nutritionist or healthcare provider. The information provided is for general purposes only. Always consult with a qualified professional for personalized advice."

                            4. **Be Transparent:** Users may ask for nutrition information information from you. You are first to use the json response added to the user query, howerver if the response says "No data available on that.", use whatever
                                information you may have in your data banks that are relevant to the query. Otherwise, use the default response about not having any data on that.

                            Feel free to use your creativity and natural language to engage with users within the specified boundaries. Remember to stay focused on nutrition-related topics and provide informative, helpful, and safe responses.'''
                }]+
                [{
                    "role": m["role"],
                    "content": m["content"]
                } for m in st.session_state.messages],
                stream=True,
        ):
            full_response += (response.choices[0].delta.content or "")
            message_placeholder.markdown(full_response + "▌")
        
        message_placeholder.markdown(full_response)

    st.session_state.messages.append({
        "role": "assistant",
        "content": full_response
    })

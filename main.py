import streamlit as st
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
import openai
import json
import time
from openai.error import RateLimitError

# from google.oauth2 import service_account

#Authentication

# open AI
openai.api_key = (st.secrets["openai_api_key"])


#   Firebase

#Try to initialize app, but if it already exists, pass
# try:
    # Use the private key file of the service account directly.



    # cred = credentials.Certificate("firestore-key.json")
    # app = firebase_admin.initialize_app(cred)
try:
    key_dict = json.loads(st.secrets["textkey"])
    cred = credentials.Certificate(key_dict)
    app = firebase_admin.initialize_app(cred)

except ValueError:
    pass

firestore_client = firestore.client()

def create_doc(email_input, topic_input):
    coll_ref = firestore_client.collection("tasks")
    create_time, doc_ref = coll_ref.add(
        {
            "email": email_input,
            "topic": topic_input,
            "status": False
        }
    )

    # st.write(f"{doc_ref.id} is created at {create_time}")


def is_topic_relevant_to_debate(topic):
    if len(topic) == 0:
        return False
    is_relevant_prompt = "Is the following topic relevant to high school debate: '" + topic + "'"
    is_relevant_prompt += "\n Respond with 'Yes' or 'No' only. Do not include anything else is response"
    is_relevant_response = openai.ChatCompletion.create(model="gpt-3.5-turbo", temperature=0.2, max_tokens=500,
                                                        frequency_penalty=0,
                                                        messages=[{"role": "assistant", "content": is_relevant_prompt}])
    return (str(is_relevant_response.choices[0].message.content).find("Yes") >= 0)

def is_topic_offensive(topic):
    if len(topic) == 0:
        return False
    is_offensive_prompt = "Is the following topic offensive (contains sexism, racism, homophobia, etc.): '" + topic + "'"
    is_offensive_prompt += "\n Respond with 'Yes' or 'No' only. Do not include anything else is response"
    is_offensive_response = openai.ChatCompletion.create(model="gpt-3.5-turbo", temperature=0.2, max_tokens=500,
                                                        frequency_penalty=0,
                                                        messages=[{"role": "assistant", "content": is_offensive_prompt}])
    return (str(is_offensive_response.choices[0].message.content).find("Yes") >= 0)

def is_email(email):
    if len(email) == 0:
        return False
    is_email_prompt = "Is the following email valid: '" + email + "'"
    is_email_prompt += "\n Respond with 'Yes' or 'No' only. Do not include anything else in the response"
    is_email_response = openai.ChatCompletion.create(model="gpt-3.5-turbo", temperature=0.2, max_tokens=500,
                                                        frequency_penalty=0,
                                                        messages=[{"role": "assistant", "content": is_email_prompt}])
    return (str(is_email_response.choices[0].message.content).find("Yes") >= 0)

# def check_email(email):
#     pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b'
#     if regex.match(pattern, email):
#         return True
#     else:
#         return False

# set the title
st.title("📝 Card Cutter")

st.info("This card cutter finds and cuts paragraphs from research articles, and provides you with a paragraph of evidence, links and author names.",icon='❓')



with st.form("email and topic", clear_on_submit=False):
    email_input = st.text_input(label='Email')
    topic_input = st.text_input(label='Card Topic')
    submitted = st.form_submit_button("Submit")
    try:
        if submitted:

            # st.write(email_input, topic_input)

            if is_topic_relevant_to_debate(topic_input):
                create_doc(email_input, topic_input)

                if not is_topic_offensive(topic_input):
                    st.success("Awesome! Your cards will be created, and sent to the email address provided.")
                else:
                    st.error("The entered topic contains offensive content. Please provide a valid and respectful topic for debate. If you believe this is an error, please contact support at debatecardcreator@gmail.com")
            else:
                st.error("That doesn't look relevant to debate. Try restructing your prompt to be more argumentative, and resubmit.")

            progress_text = "Submission in progress. Please wait."
            my_bar = st.progress(0, text=progress_text)

            for percent_complete in range(100):

                    time.sleep(0.1)
                    my_bar.progress(percent_complete + 1, text=progress_text)
    except RateLimitError:
        st.error("Slow down.")
        time.sleep(20)



coll_ref = firestore_client.collection("tasks")




#
# # Read firebase database
# docs = coll_ref.stream()
# for doc in docs:
#     st.write(f'{doc.id} = {doc.to_dict()}')


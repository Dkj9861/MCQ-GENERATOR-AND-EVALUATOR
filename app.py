import os
import json
import traceback
import pandas as pd
from dotenv import load_dotenv
import streamlit as st
from mcqgenerator.utils import read_file,get_table_data
from langchain_community.callbacks.manager import get_openai_callback
from mcqgenerator.mcqg import generate_evaluate_chain
from mcqgenerator.logger import logging
from mcqgenerator.MCQG1 import generator_chain1,evaluator_chain1,generate_mcqs_from_text_file,evaluate_mcqs_from_text_file

#loading json file

with open('Response.json', 'r') as file:
    RESPONSE_JSON = json.load(file)

#creating a title for the app
st.title("MCQs Creator Application with LangChain")

#Create a form using st.form
with st.form("user_inputs"):
    #File Upload
    uploaded_file=st.file_uploader("Uplaod a PDF or txt file")

    #Input Fields
    mcq_count=st.number_input("No. of MCQs", min_value=3, max_value=100)

    #Subject
    subject=st.text_input("Insert Subject",max_chars=20)

    # Quiz Tone
    tone=st.text_input("Complexity Level Of Questions", max_chars=20, placeholder="Simple")

    #Add Button
    button=st.form_submit_button("Create MCQs")

    # Check if the button is clicked and all fields have input

    if button and uploaded_file is not None and mcq_count and subject and tone:
        with st.spinner("loading..."):
            try:
                text=read_file(uploaded_file)
                #Count tokens and the cost of API call
                with get_openai_callback() as cb:
                    response=generate_evaluate_chain(
                        {
                        "text": text,
                        "number": mcq_count,
                        "subject":subject,
                        "tone": tone,
                        "response_json": json.dumps(RESPONSE_JSON)
                            }
                    )
                #st.write(response)

            except Exception as e:
                traceback.print_exception(type(e), e, e.__traceback__)
                st.error("Error")

            else:
                print(f"Total Tokens:{cb.total_tokens}")
                print(f"Prompt Tokens:{cb.prompt_tokens}")
                print(f"Completion Tokens:{cb.completion_tokens}")
                print(f"Total Cost:{cb.total_cost}")
                if isinstance(response, dict):
                    #Extract the quiz data from the response
                    quiz=response.get("quiz", None)
                    if quiz is not None:
                        table_data=get_table_data(quiz)
                        if table_data is not None:
                            df=pd.DataFrame(table_data)
                            df.index=df.index+1
                            st.table(df)
                            #Display the review in atext box as well
                            st.text_area(label="Review", value=response["review"])
                        else:
                            st.error("Error in the table data")

                else:
                    st.write(response)


# File uploader for MCQs
st.title("MCQ ANSWER GENERATOR AND EVALUATOR")

uploaded_file = st.file_uploader("Upload a text file", type="txt")

if uploaded_file is not None:
    st.write("File uploaded successfully!")

    # Buttons for user actions
    if st.button("Generate MCQ"):
        st.write("Generating MCQs...")
        uploaded_file_content = uploaded_file.read().decode("utf-8")
        generated_mcqs = generate_mcqs_from_text_file(uploaded_file_content)

       # generated_mcqs = generate_mcqs_from_text_file(uploaded_file.read())
        
        st.write("Generated MCQs:")
        for question, data in generated_mcqs.items():
            st.write(f"**Question:** {question}")
            st.write(f"**Options:** {', '.join(data['options'])}")
            st.write(f"**Correct Answer:** {data['correct_answer']}")
            st.write(f"**Explanation:** {data['explanation']}")
            st.write("---")

    if st.button("Evaluate MCQ"):
        st.write("Evaluating MCQs...")
        uploaded_file_content = uploaded_file.read()  # This returns bytes
        evaluated_mcqs = evaluate_mcqs_from_text_file(uploaded_file_content)

        #evaluated_mcqs = evaluate_mcqs_from_text_file(uploaded_file.read())
        
        st.write("Evaluated MCQs:")
        for question, data in evaluated_mcqs.items():
            st.write(f"**Question:** {question}")
            st.write(f"**Correct Answer:** {data['correct_answer']}")
            st.write(f"**Explanation:** {data['explanation']}")
            st.write("---")

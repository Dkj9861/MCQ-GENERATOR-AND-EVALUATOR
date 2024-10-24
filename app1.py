import os
import json
import traceback
import pandas as pd
from dotenv import load_dotenv
import streamlit as st
from mcqgenerator.utils import read_file, get_table_data
from langchain_community.callbacks.manager import get_openai_callback
from mcqgenerator.mcqg import generate_evaluate_chain
from mcqgenerator.logger import logging
from mcqgenerator.MCQG1 import generator_chain1, evaluator_chain1, generate_mcqs_from_text_file, evaluate_mcqs_from_text_file

# Adding some basic styling for titles and headers
st.markdown("""
    <style>
    .title {
        font-size: 36px;
        
        color: #3A64D8;
        text-align: center;
        border: 2px solid #3A64D8;
        padding: 10px;
        border-radius: 10px;
        background-color: #003366;
        margin-bottom: 40px;
    }
    .header {
        font-size: 24px;
        color: #003366;
        margin-bottom: 20px;
        text-align: center;
        border: 0.5px solid #3A64D8; 
        padding: 5px;             
        border-radius: 2px;      
        background-color: #D3D3D3; 
    }
    .sidebar-text {
        font-size: 18px;
        color: #4A9D66;
    }
    </style>
""", unsafe_allow_html=True)

# Title for the whole app
st.markdown("<div class='title'>MCQ Generator & Evaluator Application</div>", unsafe_allow_html=True)

# Creating two columns for the layout
col1, col2 = st.columns(2)

# Column 1: MCQ Generator
with col1:
    st.markdown("<div class='header'>📝 MCQ Generator(Content)</div>", unsafe_allow_html=True)

    # Create a form using st.form
    with st.form("user_inputs"):
        # File Upload
        uploaded_file = st.file_uploader("Upload a PDF or text file", type=['pdf', 'txt'])

        # Input Fields
        mcq_count = st.number_input("No. of MCQs", min_value=3, max_value=100)

        # Subject
        subject = st.text_input("Insert Subject", max_chars=20)

        # Quiz Tone
        tone = st.text_input("Complexity Level Of Questions", max_chars=20, placeholder="Simple")

        # Add Button
        button = st.form_submit_button("Create MCQs")

        # Check if the button is clicked and all fields have input
        if button and uploaded_file is not None and mcq_count and subject and tone:
            with st.spinner("Generating MCQs..."):
                try:
                    text = read_file(uploaded_file)
                    # Count tokens and the cost of API call
                    with get_openai_callback() as cb:
                        response = generate_evaluate_chain(
                            {
                                "text": text,
                                "number": mcq_count,
                                "subject": subject,
                                "tone": tone,
                                "response_json": json.dumps(RESPONSE_JSON)
                            }
                        )
                except Exception as e:
                    traceback.print_exception(type(e), e, e.__traceback__)
                    st.error("Error generating MCQs.")
                else:
                    st.success("MCQs successfully generated!")
                    if isinstance(response, dict):
                        # Extract the quiz data from the response
                        quiz = response.get("quiz", None)
                        if quiz is not None:
                            table_data = get_table_data(quiz)
                            if table_data is not None:
                                df = pd.DataFrame(table_data)
                                df.index = df.index + 1
                                st.table(df)
                                # Display the review in a text box as well
                                st.text_area(label="Review", value=response["review"])
                            else:
                                st.error("Error in table data.")
                    else:
                        st.write(response)

# Column 2: MCQ Evaluator
with col2:
    st.markdown("<div class='header'>🧪 MCQ Answer Evaluator and Generator</div>", unsafe_allow_html=True)

    # File uploader for MCQs
    uploaded_file = st.file_uploader("Upload a text file for evaluation", type="txt", key="eval")

    if uploaded_file is not None:
        st.write("File uploaded successfully!")

        # Buttons for user actions
        if st.button("Generate MCQ", key="generate"):
            st.write("Generating MCQs...")
            uploaded_file_content = uploaded_file.read().decode("utf-8")
            generated_mcqs = generate_mcqs_from_text_file(uploaded_file_content)

            st.write("Generated MCQs:")
            for question, data in generated_mcqs.items():
                st.write(f"**Question:** {question}")
                st.write(f"**Options:** {', '.join(data['options'])}")
                st.write(f"**Correct Answer:** {data['correct_answer']}")
                st.write(f"**Explanation:** {data['explanation']}")
                st.write("---")

        if st.button("Evaluate MCQ", key="evaluate"):
            st.write("Evaluating MCQs...")
            uploaded_file_content = uploaded_file.read()  # This returns bytes
            evaluated_mcqs = evaluate_mcqs_from_text_file(uploaded_file_content)

            st.write("Evaluated MCQs:")
            for question, data in evaluated_mcqs.items():
                st.write(f"**Question:** {question}")
                st.write(f"**Correct Answer:** {data['correct_answer']}")
                st.write(f"**Explanation:** {data['explanation']}")
                st.write("---")

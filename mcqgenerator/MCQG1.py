import streamlit as st
import json
from langchain_community.chat_models import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain

# Define the evaluator prompt template
evaluator_template = """
You are an MCQ evaluator. Given the following MCQ, identify the correct answer and provide a concise explanation for it.
MCQ: 
"{question}"
Options: 
1. {option1}
2. {option2}
3. {option3}
4. {option4}

Format the response as JSON with the following keys: 
"correct_answer" (a string), 
"explanation" (a string).
"""

# Define the generator prompt template
generator_template = """
You are an MCQ generator. Given the following question, generate 4 options, specify the correct answer, and provide a brief explanation for the correct answer.
Question: "{question}"
Format the response as JSON with the following keys: "options" (an array of strings), "correct_answer" (a string), and "explanation" (a string).
"""

# Set up the models and chains
api_key = 'sk-n6za9NK7QXoKEWoFa29e5GSM_Y_fRQxwaSu193_B44T3BlbkFJceQ8Nex1KdlYJMh9Cl_OtG6wShxw_ILQGp2T3P1G4A'

llm = ChatOpenAI(openai_api_key=api_key, model_name='gpt-3.5-turbo', temperature=0.3)

# Chains for MCQ evaluation and generation
evaluator_prompt = PromptTemplate(input_variables=["question", "option1", "option2", "option3", "option4"], template=evaluator_template)
evaluator_chain1 = LLMChain(llm=llm, prompt=evaluator_prompt)

generator_prompt = PromptTemplate(input_variables=["question"], template=generator_template)
generator_chain1 = LLMChain(llm=llm, prompt=generator_prompt)

# Function to extract question and options from MCQ text
def extract_question_and_options(mcq_text):
    lines = mcq_text.split('\n')
    question = lines[0]
    options = [line[3:].strip() for line in lines[1:5]]
    return question, options

# Function to evaluate existing MCQs from text file
# Updated evaluate_mcqs_from_text_file function
import re

def evaluate_mcqs_from_text_file(text_file):
    mcqs = {}

    # Read the file content only once
    content = text_file.decode("utf-8").strip()

    # Debug: Print the full content
    

    # Split the content into individual MCQs using regex to detect questions
    mcq_list = re.split(r'(?=(What|Which|Who|Where|When|How|Why)[^?]*\?)', content)

    # Merge question text with the part of options (split can break the question text)
    mcq_list = [" ".join(mcq_list[i:i+2]).strip() for i in range(1, len(mcq_list), 2)]

    # Debug: Print each MCQ to ensure splitting works as expected
    

    for mcq_text in mcq_list:
        if mcq_text.strip():  # Ensure there's content to process
            # Debug: Show the current MCQ being processed
            '''st.write("Processing MCQ:")
            st.write(mcq_text)'''

            try:
                # Extract question and options using a custom function
                question, options = extract_question_and_options(mcq_text)

                # Debug: Print the extracted question and options
                

                input_data = {
                    "question": question,
                    "option1": options[0],
                    "option2": options[1],
                    "option3": options[2],
                    "option4": options[3]
                }

                # Call the evaluator chain and get the result
                response = evaluator_chain1.run(input_data)

                # Debug: Print the response from the evaluator
                

                mcqs[question] = json.loads(response)  # Store the correct answer and explanation

            except Exception as e:
                st.error(f"Error processing MCQ: '{mcq_text}'")
                st.error(f"Exception: {e}")

    return mcqs



# Function to generate new MCQs from question-only text file
def generate_mcqs_from_text_file(text_file):
    mcqs = {}
    
    #questions = text_file.read().decode("utf-8").splitlines()
    questions = text_file.splitlines()
    
    for question in questions:
        question = question.strip()  # Clean up any extra whitespace
        if question:  # Ensure the question isn't empty
            input_data = {
                "question": question  # Prepare input data with the question
            }
            try:
                response = generator_chain1.run(input_data)  # Run the chain
                mcqs[question] = json.loads(response)  # Store the generated MCQ
            except Exception as e:
                st.error(f"Error generating MCQ for question: '{question}'")
                st.error(f"Exception: {e}")
    
    return mcqs
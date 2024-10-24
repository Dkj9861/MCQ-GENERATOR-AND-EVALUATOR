from setuptools import setup, find_packages

setup(
    name='MCQ12345',
    version='0.1',
    packages=find_packages(),
    install_requires=[
        "openai",
        "pypdf2",
        "streamlit",
        "langchain",
        "langchain_community",
        "python-dotenv"
    ]
)


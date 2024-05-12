import streamlit as st # type: ignore

st.title("LLM Project: Industrial Generative AI Q&A System for Refrigeration Field Engineers")
st.write("""
         [![view source code ](https://img.shields.io/badge/GitHub%20Repository-gray?logo=github)](https://github.com/Okeysir198/LLM-project)
         [![linkedin ](https://img.shields.io/badge/Nguyen%20Thanh%20Trung-blue?logo=linkedin&color=blue)](https://www.linkedin.com/in/nttrung198/)
""")

st.header("Problem Statement")
st.write("""
         Design and implement a Q&A system to assist field engineers in the refrigeration domain. The system should facilitate the diagnosis of faulty equipment by utilizing installation and maintenance manuals.
""")

st.header("Solution Overview")
st.write("""
         This project implements a chatbot system utilizing LangChain and Streamlit. The system comprises the following key components:
         - **Fontend**: A web-based application developed using Streamlit that provides the user interface for interacting with the chatbot.
         - **Backend**: Powered by LangChain, the backend leverages large language model (LLM) tools for storing data, processing user input and generating relevant responses.
""")


st.image("asset/01_SolutionAchitecture.svg", caption="Solution Achitecture")
st.image("asset/02_Backend.svg", caption="Backend")
st.image("asset/03_Frontend.svg", caption="Frontend")
st.image("asset/04_Deployment.svg", caption="Deployment")
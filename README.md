# LLM Project: Industrial Generative AI Q&A System for Refrigeration Field Engineers

[![view source code ](https://img.shields.io/badge/GitHub%20Repository-gray?logo=github)](https://github.com/Okeysir198/LLM-project)

## Problem Statement

Design and implement a Q&A system to assist field engineers in the refrigeration domain. The system should facilitate the diagnosis of faulty equipment by utilizing installation and maintenance manuals.

## Solution Overview

This project implements a chatbot system utilizing LangChain and Streamlit. The system comprises the following key components:

* **Frontend:** A web-based application developed using Streamlit that provides the user interface for interacting with the chatbot.
* **Backend:** Powered by LangChain, the backend leverages large language model (LLM) tools for storing data, processing user input, and generating relevant responses.

## ️ Running locally

```shell
# Run main streamlit app
$ pip install langchain==0.1.17 langchain_community==0.0.36 langchain_openai==0.1.4 langchainhub==0.1.15 streamlit==1.33.0 openai==1.25.0 pypdf==4.2.0 docarray==0.40.0

# Run the main streamlit app
$ streamlit run Home.py

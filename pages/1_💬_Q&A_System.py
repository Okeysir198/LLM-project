import utils
import streamlit as st                                              # type: ignore

import os
from langchain.embeddings.openai import OpenAIEmbeddings            # type: ignore
from langchain_openai import ChatOpenAI                             # type: ignore
from langchain.memory import ConversationBufferMemory               # type: ignore
from langchain.chains import ConversationalRetrievalChain           # type: ignore
from langchain_community.document_loaders import PyPDFLoader        # type: ignore
from langchain.text_splitter import RecursiveCharacterTextSplitter  # type: ignore
from langchain_community.vectorstores import DocArrayInMemorySearch # type: ignore
from langchain.callbacks.base import BaseCallbackHandler            # type: ignore

st.set_page_config(page_title="Q&A System", page_icon="")
st.header('Question Answering System')
st.write('This system provides access to a comprehensive collection of domain-specific documents. It leverages this knowledge base to respond to user queries by intelligently referencing relevant content within those documents.')
st.write('[![view source code ](https://img.shields.io/badge/GitHub%20Repository-gray?logo=github)](https://github.com/Okeysir198/LLM-project)')


# Define a list to store frequent asked questions 
predefined_questions = [
    "What are preventive measures to mitigate the risk of electric shock?",
    "What are the most important components of the compressor unit?",
    "What considerations should be made regarding the installation site when setting up the compressor?",
    "What precautions should be taken prior to initiating the compressor to prevent issues?",
    "What are the potential factors and solutions for addressing the compressor unit's cessation of operation prior to reaching the desired discharge pressure level?",
    "What are potential solutions to address the absence or inadequate discharge capability?",
    "Which factors should engineers consider and what preparations are necessary when inspecting the safety valve?",
    "What steps are necessary when shutting down the plant for a prolonged duration?",
    "What is the noise level of Compressor and refrigeration dryer on air receiver (RSDK-B 5.5)?",
    "What is the difference between on and off status of the pressure switch?"
]


class StreamHandler(BaseCallbackHandler):
    """
    StreamHandler (LangChain): Updates container with LLM's streaming output.
    - container (Any): Target element (e.g., Streamlit text box).
    - on_llm_new_token(token: str): Appends token, updates container with markdown.
    """
    def __init__(self, container, initial_text=""):
        self.container = container
        self.text = initial_text

    def on_llm_new_token(self, token: str, **kwargs):
        self.text += token
        self.container.markdown(self.text)

class DomainDocumentsChatbot:
    """
    DomainDocumentsChatbot: Handles domain-specific chatbot using uploaded PDFs.
    - Uses OpenAI for LLM interaction and processes uploaded PDFs for retrieval.
    - Provides methods for:
        - setup_qa_chain: Loads/processes PDFs, creates QA chain for retrieval.
        - get_query_response: Processes user query, retrieves answer & references.
    - Utilizes StreamHandler for real-time response display.
    """
    def __init__(self):
        self.openai_model = utils.configure_openai()  
        self.qa_chain = None
        self.documents_loaded = {}

    def save_file(self, file):
        folder = "tmp"
        os.makedirs(folder, exist_ok=True)
        file_path = os.path.join(folder, file.name)
        with open(file_path, "wb") as f:
            f.write(file.getvalue())
        return file_path

    @st.spinner('Loading information...')
    def setup_qa_chain(self, uploaded_files=None):
        documents = []
        new_files = False

        # Check for uploaded files and update document list
        if uploaded_files:
            for file in uploaded_files:
                file_hash = hash(file.getvalue())
                if file_hash not in self.documents_loaded:
                    self.documents_loaded[file_hash] = True
                    new_files = True
                    file_path = self.save_file(file)
                    loader = PyPDFLoader(file_path)
                    documents.extend(loader.load())

        # Load default documents if no new files and not loaded before
        if not new_files and not self.documents_loaded:
            loader = PyPDFLoader("docs/compressor_user_manual.pdf")
            documents.extend(loader.load())
            self.documents_loaded = True

        # Process documents
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=2500, chunk_overlap=150)
        splits = text_splitter.split_documents(documents)
        embeddings = OpenAIEmbeddings()
        vectordb = DocArrayInMemorySearch.from_documents(splits, embeddings)
        # retriever = vectordb.as_retriever(search_type="similarity", search_kwargs={"k": 2}) # not used
        retriever = vectordb.as_retriever(search_type='mmr', search_kwargs={'k':2, 'fetch_k':4})

        # Contextual conversation memory
        memory = ConversationBufferMemory(memory_key="chat_history", output_key="answer", return_messages=True)

        # Create qa_chain only on first call or with new files
        if not self.qa_chain or new_files:
            self.qa_chain = ConversationalRetrievalChain.from_llm(
                llm=ChatOpenAI(model_name=self.openai_model, temperature=0, streaming=True),
                retriever=retriever,
                memory=memory,
                return_source_documents=True,
            )
        return self.qa_chain

    def get_query_response(self, user_query):
        """
        get_query_response(self, user_query): Processes user query and displays response.
        - Displays user query and uses qa_chain to invoke retrieval and get answer.
        - Updates session state with response and shows references in popovers.
        - Utilizes StreamHandler for real-time response visualization.
        """
        utils.display_msg(user_query, "user")
        with st.chat_message("assistant"):
            st_cb = StreamHandler(st.empty())
            result = self.qa_chain.invoke(
                {"question": user_query},
                {"callbacks": [st_cb]},
            )
            response = result["answer"]
            st.session_state.messages.append({"role": "assistant", "content": response})

            # Show references
            for idx, doc in enumerate(result["source_documents"], 1):
                filename = os.path.basename(doc.metadata["source"])
                page_num = doc.metadata["page"]
                ref_title = f":blue[Reference {idx}: *{filename} - page.{page_num}*]"
                with st.popover(ref_title):
                    st.caption(doc.page_content)
        

    @utils.enable_chat_history  
    def main(self):
        # User uploaded files
        uploaded_files = st.sidebar.file_uploader(label="Upload PDF files", type=["pdf"], accept_multiple_files=True)

        # Call setup_qa_chain only if documents changed or not initialized
        self.qa_chain = self.setup_qa_chain(uploaded_files)

        #  Display FA questions 
        st.sidebar.header("Frequent Asked Questions")
        for question in predefined_questions:
            if st.sidebar.button(question):
                self.get_query_response(question)

        # User query
        user_query = st.chat_input(placeholder="Ask me anything!")
        if user_query:
            self.get_query_response(user_query)
        
if __name__ == "__main__":
    obj = DomainDocumentsChatbot()
    obj.main()


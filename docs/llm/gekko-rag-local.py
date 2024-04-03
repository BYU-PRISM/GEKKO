# Retrieval-Augmented Generation (RAG) provides context for a
#  Gekko AI Assistant LLM answers questions about modeling,
#  optimization, and advanced control.
# See https://apmonitor.com/dde/index.php/Main/RAGLargeLanguageModel
# Use https://apmonitor.com/docs for an online chat version of this script
import ollama
import pandas as pd
import chromadb

# Loading and preparing the ChromaDB with data
def setup_chromadb():
    # read Gekko LLM training data
    url='https://raw.githubusercontent.com'
    path='/BYU-PRISM/GEKKO/master/docs/llm/train.jsonl'
    qa = pd.read_json(url+path,lines=True)
    documents = []
    metadatas = []
    ids = []

    for i in range(len(qa)):
        s = f"### Question: {qa['question'].iloc[i]} ### Answer: {qa['answer'].iloc[i]}"
        documents.append(s)
        metadatas.append({'qid': f'qid_{i}'})
        ids.append(str(i))

    cc = chromadb.Client()
    cdb = cc.create_collection(name='gekko')
    cdb.add(documents=documents, metadatas=metadatas, ids=ids)
    return cdb

# Ollama LLM function
def ollama_llm(question, context):
    formatted_prompt = f"Question: {question}\n\nContext: {context}"
    response = ollama.chat(model='mistral', messages=[{'role': 'user', 'content': formatted_prompt}])
    return response['message']['content']

# Define the RAG chain
def rag_chain(question, cdb):
    context = cdb.query(query_texts=[question],
                        n_results=5, include=['documents'])
    formatted_context = "\n\n".join(x for x in context['documents'][0])
    formatted_context += "\n\nYou are a professional and technical assistant trained to answer questions about Gekko, which is a high-performance Python package for optimization, simulation, machine learning, data-science, model predictive control, and parameter estimation. In addition, you can also help with answering questions about programming in Python, particularly in relation to the aforementioned topics. Your primary goal is to assist users in finding solutions and gaining knowledge in these areas. You are trained on hundreds of examples and will continue to improve."
    result = ollama_llm(question, formatted_context)
    return result

# Setup ChromaDB
cdb = setup_chromadb()

# Use Gekko AI Assistant (local)
question = 'What are you trained to do?'
out = rag_chain(question, cdb)
print(out)

# rag_document_searcher.py
# Bank Compliance Document Searcher
# Powered by LangChain + Groq AI + RAG

import os
from pathlib import Path
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.document_loaders import TextLoader, DirectoryLoader
from langchain_groq import ChatGroq
from langchain_core.prompts import PromptTemplate
from langchain.chains import RetrievalQA
import warnings
warnings.filterwarnings('ignore')

print("🏦 Bank Compliance Document Searcher")
print("   Powered by LangChain + Groq AI + RAG")
print("=" * 50)

# ================================================
# PHASE 1 — LOAD DOCUMENTS
# ================================================
print("\n📄 Phase 1: Loading Bank documents...")

loader = DirectoryLoader(
    'bank_docs/',
    glob="*.txt",
    loader_cls=TextLoader
)
documents = loader.load()
print(f"✅ Loaded {len(documents)} policy documents")
for doc in documents:
    print(f"   → {Path(doc.metadata['source']).name}")

# ================================================
# PHASE 2 — SPLIT INTO CHUNKS
# ================================================
print("\n✂️ Phase 2: Splitting into chunks...")

text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=500,
    chunk_overlap=50,
    separators=["\n\n", "\n", ".", " "]
)
chunks = text_splitter.split_documents(documents)
print(f"✅ Created {len(chunks)} searchable chunks")

# ================================================
# PHASE 3 — CREATE EMBEDDINGS + VECTOR STORE
# ================================================
print("\n🔢 Phase 3: Building vector database...")

embeddings = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2",
    model_kwargs={'device': 'cpu'}
)
vectorstore = FAISS.from_documents(chunks, embeddings)
print("✅ Vector database ready!")

# ================================================
# PHASE 4 — CONNECT GROQ AI
# ================================================
print("\n🤖 Phase 4: Connecting Groq AI...")

# Get API key from environment variable (safe!)
groq_api_key = os.environ.get("GROQ_API_KEY")
if not groq_api_key:
    print("❌ GROQ_API_KEY not found!")
    print("   Run: $env:GROQ_API_KEY='your_key'")
    exit(1)

# Initialize Groq LLM
llm = ChatGroq(
    groq_api_key=groq_api_key,
    model_name="llama-3.3-70b-versatile",
    temperature=0,                 # 0 = consistent answers
    max_tokens=500                 # Limit response length
)
print("✅ Groq AI connected!")
print("   Model: Llama 3 8B")

# ================================================
# PHASE 5 — CREATE BANK PROMPT
# ================================================
print("\n📝 Phase 5: Setting up Bank prompt...")

# This tells AI HOW to answer
bank_prompt = PromptTemplate(
    template="""You are a Bank compliance assistant.
Answer questions using ONLY the provided policy documents.
If the answer is not in the documents, say "This is not covered in current policies."
Always cite which policy document your answer comes from.
Be concise and professional.

Policy Documents:
{context}

Question: {question}

Answer:""",
    input_variables=["context", "question"]
)

# ================================================
# PHASE 6 — BUILD RAG CHAIN
# ================================================
print("\n⛓️ Phase 6: Building RAG chain...")

# This connects everything:
# Question → Search → AI → Answer
rag_chain = RetrievalQA.from_chain_type(
    llm=llm,
    chain_type="stuff",          # stuff = put all chunks together
    retriever=vectorstore.as_retriever(
        search_kwargs={"k": 3}   # Find top 3 relevant chunks
    ),
    chain_type_kwargs={
        "prompt": bank_prompt
    },
    return_source_documents=True  # Show which docs were used
)
print("✅ RAG chain ready!")

# ================================================
# PHASE 7 — INTERACTIVE Q&A
# ================================================
print("\n" + "=" * 50)
print("🏦 Bank AI Compliance Assistant Ready!")
print("=" * 50)
print("Commands: 'history' = past questions, 'quit' = exit")
print()

question_history = []

while True:
    question = input("❓ Your question: ").strip()

    if question.lower() in ['quit', 'exit', 'q']:
        print("\n👋 Goodbye!")
        break

    if not question:
        continue

    if question.lower() == 'history':
        print("\n📜 Questions asked today:")
        if question_history:
            for i, q in enumerate(question_history, 1):
                print(f"   {i}. {q}")
        else:
            print("   No questions yet!")
        continue

    question_history.append(question)

    print("\n🤔 AI is thinking...")

    try:
        # Run RAG chain — search + generate answer
        result = rag_chain.invoke({"query": question})

        # Show AI generated answer
        print(f"\n🤖 AI Answer:")
        print("-" * 40)
        print(result["result"])

        # Show source documents used
        print(f"\n📄 Sources Used:")
        sources_used = set()
        for doc in result["source_documents"]:
            source = Path(doc.metadata['source']).name
            if source not in sources_used:
                print(f"   → {source}")
                sources_used.add(source)

    except Exception as e:
        print(f"❌ Error: {e}")

    print("\n" + "=" * 50)
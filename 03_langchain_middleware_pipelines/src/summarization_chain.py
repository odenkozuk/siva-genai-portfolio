"""
LangChain Summarization Chain with Azure OpenAI.
Implements map-reduce summarization for long enterprise documents.
"""

import os
from dotenv import load_dotenv
from langchain_openai import AzureChatOpenAI
from langchain.chains.summarize import load_summarize_chain
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema import Document
from langchain.prompts import PromptTemplate

load_dotenv()

MAP_PROMPT = PromptTemplate(
    input_variables=["text"],
    template="""Summarize the following text, focusing on key facts, figures, and decisions:

{text}

CONCISE SUMMARY:""",
)

COMBINE_PROMPT = PromptTemplate(
    input_variables=["text"],
    template="""You have been given summaries of multiple document sections.
Combine them into a single coherent executive summary highlighting:
- Key decisions made
- Important metrics and figures
- Action items and next steps

SUMMARIES:
{text}

EXECUTIVE SUMMARY:""",
)


def build_llm() -> AzureChatOpenAI:
    return AzureChatOpenAI(
        azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
        api_key=os.getenv("AZURE_OPENAI_API_KEY"),
        azure_deployment=os.getenv("AZURE_OPENAI_DEPLOYMENT", "gpt-4o"),
        api_version="2024-02-01",
        temperature=0,
    )


def summarize_text(text: str, chain_type: str = "map_reduce") -> str:
    """Summarize a long text using map-reduce or stuff strategy."""
    llm = build_llm()
    splitter = RecursiveCharacterTextSplitter(chunk_size=4000, chunk_overlap=200)
    chunks = splitter.split_text(text)
    docs = [Document(page_content=chunk) for chunk in chunks]

    if chain_type == "map_reduce":
        chain = load_summarize_chain(
            llm,
            chain_type="map_reduce",
            map_prompt=MAP_PROMPT,
            combine_prompt=COMBINE_PROMPT,
            verbose=False,
        )
    else:
        chain = load_summarize_chain(llm, chain_type="stuff")

    result = chain.invoke({"input_documents": docs})
    return result["output_text"]


def summarize_documents(documents: list[str]) -> list[str]:
    """Batch summarize multiple documents."""
    return [summarize_text(doc) for doc in documents]


if __name__ == "__main__":
    sample = """
    Q3 Financial Review Meeting - October 2024
    Revenue for Q3 reached $4.2M, exceeding the target of $4.0M by 5%.
    Operating expenses were $2.8M, resulting in an operating margin of 33%.
    The enterprise sales team closed 12 new contracts worth $1.8M combined.
    Customer churn decreased from 8% to 5.5% following the new success program.
    Key decisions: Expand headcount by 15 in Q4, increase marketing budget by $200K.
    Action items: CFO to prepare Q4 budget by Nov 1; Sales VP to present pipeline review Nov 15.
    """
    summary = summarize_text(sample)
    print("Summary:", summary)

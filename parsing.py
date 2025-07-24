import json
from typing import Dict, Any
import openai
from dotenv import load_dotenv
import os

load_dotenv()
client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

SECTION_HEADERS = [
    "Company Overview",
    "Financials",
    "Market Opportunity",
    "Risks"
]

def split_sections_with_llm(text: str) -> Dict[str, str]:
    """Use GPT-4 to intelligently split the text into relevant sections"""
    prompt = f"""Please analyze the following CIM (Confidential Information Memorandum) text and split it into the following sections:
    - Company Overview
    - Financials
    - Market Opportunity
    - Risks

    For each section, extract the relevant information from the text. If a section isn't clearly present, 
    try to infer it from related content. Return the results in a JSON format with these exact section names as keys.

    Text to analyze:
    {text}

    Return only the JSON object with the following structure:
    {{
        "Company Overview": "extracted text...",
        "Financials": "extracted text...",
        "Market Opportunity": "extracted text...",
        "Risks": "extracted text..."
    }}
    """

    response = client.chat.completions.create(
        model="gpt-4.1",
        messages=[
            {"role": "system", "content": "You are a financial document analysis expert. Extract and organize content precisely."},
            {"role": "user", "content": prompt}
        ],
        temperature=0,
        max_tokens=3000,
        response_format={"type": "json_object"}
    )

    try:
        sections = json.loads(response.choices[0].message.content)
        return sections
    except json.JSONDecodeError:
        return {header: "" for header in SECTION_HEADERS}

def extract_company_info(text: str) -> Dict[str, str]:
    """Extract company information using LLM"""
    prompt = f"""Extract the following information from the text in JSON format:
    - company_name: The name of the company
    - location: Company headquarters or main location
    - industry: Company's industry or sector

    Text:
    {text}

    Return only the JSON object."""

    response = client.chat.completions.create(
        model="gpt-4.1",
        messages=[
            {"role": "system", "content": "You are a financial document analysis expert. Extract company information precisely."},
            {"role": "user", "content": prompt}
        ],
        temperature=0,
        response_format={"type": "json_object"}
    )

    try:
        info = json.loads(response.choices[0].message.content)
        return {k: v for k, v in info.items() if v and v.strip()}
    except json.JSONDecodeError:
        return {}
def parse_sections(pdf_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Enhanced section parser that uses LLM for intelligent parsing
    """
    text = pdf_data['text']
    financial_metrics = pdf_data.get('financial_metrics', {})
    
    sections = split_sections_with_llm(text)
    
    company_info = extract_company_info(text)
    
    
    return {
        'sections': sections,
        'company_info': company_info,
        'financial_metrics': financial_metrics
    }
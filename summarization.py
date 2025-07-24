import openai
from typing import Dict, List, Any
from dotenv import load_dotenv
import os
from parsing import SECTION_HEADERS

load_dotenv()
client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def summarize_text(section_name: str, section_text: str) -> str:
    """
    Generate a professional investment-focused summary using the OpenAI API.
    Each section type has specific formatting and focus points.
    """
    section_prompts = {
        "Company Overview": """Analyze and summarize the following company overview for an investment memorandum. 
        Focus on:
        1. Core business model and value proposition
        2. Key competitive advantages
        3. Market position and scale
        4. Management team highlights (if available)
        
        Provide a concise, professional summary that would be suitable for an investment committee.
        
        Content to analyze:""",
        
        "Financials": """Analyze the financial section of this investment memorandum. 
        Extract and summarize:
        1. Key financial metrics and their trends
        2. Revenue and profitability highlights
        3. Growth trajectory and financial health indicators
        4. Notable financial achievements or milestones
        
        Present the information in a clear, analyst-style format.
        
        Content to analyze:""",
        
        "Market Opportunity": """Evaluate the market opportunity described in this investment memorandum.
        Highlight:
        1. Total addressable market (TAM) size and growth
        2. Key market trends and drivers
        3. Competitive landscape overview
        4. Company's market penetration potential
        
        Provide a balanced assessment suitable for investment analysis.
        
        Content to analyze:""",
        
        "Risks": """Analyze the risk factors presented in this investment memorandum.
        Focus on:
        1. Key business and operational risks
        2. Market and competitive risks
        3. Financial risks
        4. Regulatory or compliance concerns
        
        Present a clear risk assessment that maintains objectivity.
        
        Content to analyze:"""
    }
    
    base_prompt = section_prompts.get(section_name, "Summarize the following section professionally:")
    full_prompt = f"{base_prompt}\n\n{section_text}"
    
    response = client.chat.completions.create(
        model="gpt-4.1",
        messages=[
            {"role": "system", "content": "You are an expert investment analyst providing clear, concise, and professional summaries for investment memorandums."},
            {"role": "user", "content": full_prompt}
        ],
        temperature=0,
        max_tokens=500
    )
    
    return response.choices[0].message.content.strip()

def summarize_sections(parsed_data: Dict[str, Any]) -> Dict[str, str]:
    """
    Process each section of the CIM and generate professional summaries
    focused on investment relevance.
    """
    sections = parsed_data['sections']
    summary = {}
    for section in SECTION_HEADERS:
        if section in sections and sections[section].strip():
            summary[section] = summarize_text(section, sections[section])
        else:
            summary[section] = "Information not available in the document."
    
    return summary

def extract_financial_metrics(financial_text: str) -> Dict[str, Any]:
    """Extract structured financial metrics using AI analysis"""
    prompt = """Extract key financial metrics from the following text. Return them in this exact format:
    {
        "revenue": "latest annual revenue with unit (e.g., $100M)",
        "revenue_growth": "growth rate as percentage",
        "ebitda": "latest EBITDA with unit",
        "ebitda_margin": "margin as percentage"
    }
    Only include metrics if they are explicitly mentioned in the text.
    
    Text to analyze:
    """
    
    response = client.chat.completions.create(
        model="gpt-4.1",
        messages=[
            {"role": "system", "content": "You are a financial analyst extracting key metrics in a structured format."},
            {"role": "user", "content": prompt + "\n" + financial_text}
        ],
        temperature=0,
        max_tokens=200
    )
    
    try:
        import json
        metrics = json.loads(response.choices[0].message.content.strip())
        return metrics
    except:
        return {}

def extract_company_info(overview_text: str) -> Dict[str, Any]:
    """Extract structured company information using AI analysis"""
    prompt = """Extract key company information from the following text. Return them in this exact format:
    {
        "name": "company name",
        "sector": "industry sector",
        "location": "headquarters location",
        "business_model": "1-2 sentence description of core business"
    }
    Only include information if explicitly mentioned in the text.
    
    Text to analyze:
    """
    
    response = client.chat.completions.create(
        model="gpt-4.1",
        messages=[
            {"role": "system", "content": "You are a business analyst extracting company information in a structured format."},
            {"role": "user", "content": prompt + "\n" + overview_text}
        ],
        temperature=0,
        max_tokens=200
    )
    
    try:
        import json
        info = json.loads(response.choices[0].message.content.strip())
        return info
    except:
        return {}

def extract_market_info(market_text: str) -> Dict[str, Any]:
    """Extract structured market information using AI analysis"""
    prompt = """Extract key market information from the following text. Return them in this exact format:
    {
        "market_size": "total addressable market size with unit",
        "growth_rate": "market growth rate as percentage",
        "competition": "1-2 sentence overview of competitive landscape"
    }
    Only include information if explicitly mentioned in the text.
    
    Text to analyze:
    """
    
    response = client.chat.completions.create(
        model="gpt-4.1",
        messages=[
            {"role": "system", "content": "You are a market analyst extracting market information in a structured format."},
            {"role": "user", "content": prompt + "\n" + market_text}
        ],
        temperature=0,
        max_tokens=200
    )
    
    try:
        import json
        info = json.loads(response.choices[0].message.content.strip())
        return info
    except:
        return {}

def extract_investment_highlights(all_sections_text: str) -> List[str]:
    """Extract key investment highlights using AI analysis"""
    prompt = """Based on the following information about a company, generate the top 5 most compelling investment highlights.
    Each highlight should be:
    1. Specific and data-backed when possible
    2. Focused on value creation potential
    3. Clear and concise (1-2 sentences each)
    4. Ordered by importance
    
    Text to analyze:
    """
    
    response = client.chat.completions.create(
        model="gpt-4.1",
        messages=[
            {"role": "system", "content": "You are an investment banker creating compelling investment highlights."},
            {"role": "user", "content": prompt + "\n" + all_sections_text}
        ],
        temperature=0,
        max_tokens=300
    )
    
    highlights = response.choices[0].message.content.strip().split("\n")

    highlights = [h.strip().lstrip("1234567890. ") for h in highlights if h.strip()]
    return highlights[:5]

def process_for_presentation(parsed_data: Dict[str, Any]) -> Dict[str, Any]:
    """Process all data needed for presentation generation"""
    sections = parsed_data['sections']
    presentation_data = {
        'analysis': {
            'company_info': {},
            'market_info': {},
            'key_highlights': []
        },
        'financial_metrics': {}
    }
    
    if 'Company Overview' in sections:
        presentation_data['analysis']['company_info'] = extract_company_info(sections['Company Overview'])
    
    if 'Market Opportunity' in sections:
        presentation_data['analysis']['market_info'] = extract_market_info(sections['Market Opportunity'])
    
    if 'Financials' in sections:
        presentation_data['financial_metrics'] = extract_financial_metrics(sections['Financials'])
    
    all_text = " ".join(sections.values())
    presentation_data['analysis']['key_highlights'] = extract_investment_highlights(all_text)
    
    return presentation_data

def format_summary(summary_dict: Dict[str, str], parsed_data: Dict[str, Any]) -> str:
    """Format the investment memorandum summary in a professional markdown structure"""
    md = "# Investment Memorandum Executive Summary\n\n"
    
    if "Company Overview" in summary_dict:
        md += "## Business Overview & Value Proposition\n" + summary_dict["Company Overview"] + "\n\n"
    
    if "Financials" in summary_dict:
        md += "## Financial Performance Analysis\n" + summary_dict["Financials"] + "\n\n"
    
    if "Market Opportunity" in summary_dict:
        md += "## Market Opportunity & Competitive Position\n" + summary_dict["Market Opportunity"] + "\n\n"
    
    if "Risks" in summary_dict:
        md += "## Investment Considerations & Risk Factors\n" + summary_dict["Risks"] + "\n\n"
    
    return md
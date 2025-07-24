import os
from PyPDF2 import PdfReader
# import pytesseract
# from pdf2image import convert_from_path
import openai
from dotenv import load_dotenv
import json

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

class PDFProcessor:
    def __init__(self):
        self.client = openai.OpenAI()
        
    def extract_financial_metrics_ai(self, text: str) -> dict:
        """Extract financial metrics using AI"""
        prompt = """Extract the following financial metrics from the text. Return ONLY a JSON object with these keys:
        - revenue: Latest revenue figure (with unit like M or B)
        - revenue_growth: Latest revenue growth rate (as percentage)
        - ebitda: Latest EBITDA figure (with unit)
        - ebitda_margin: Latest EBITDA margin (as percentage)
        - market_size: Total addressable market size (if mentioned)
        
        For each metric, include the time period if mentioned (e.g., "2024: $100M" or "FY2023: 15%").
        If a metric is not found, set its value to null.
        
        Text to analyze:
        {text}
        """
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4.1",
                messages=[
                    {"role": "system", "content": "You are a financial analyst extracting key metrics from business documents. Return response in valid JSON format."},
                    {"role": "user", "content": prompt.format(text=text)}
                ],
                temperature=0
            )
            
            content = response.choices[0].message.content.strip()
            return json.loads(content)
        except Exception as e:
            print(f"AI extraction failed: {e}")
            return self._fallback_metric_extraction(text)
            
    def _fallback_metric_extraction(self, text):
        """Fallback to regex-based extraction if AI fails"""
        patterns = {
            'revenue': r'(?:revenue|sales).*?\$?\s*([\d,.]+)\s*(?:million|m|billion|b)?',
            'ebitda': r'ebitda.*?\$?\s*([\d,.]+)\s*(?:million|m|billion|b)?',
            'revenue_growth': r'(?:revenue growth|sales growth).*?(\d+(?:\.\d+)?)\s*%',
            'ebitda_margin': r'(?:ebitda margin).*?(\d+(?:\.\d+)?)\s*%',
            'market_size': r'(?:market size|tam|total addressable market).*?\$?\s*([\d,.]+)\s*(?:million|m|billion|b)?'
        }

    # def extract_text_with_ocr(self, pdf_path):
    #     """Extract text from PDF pages using OCR"""
    #     images = convert_from_path(pdf_path)
    #     text = ""
    #     for image in images:
    #         img = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
    #         text += pytesseract.image_to_string(img) + "\n"
    #     return text

    def analyze_text_with_ai(self, text: str) -> dict:
        """Analyze text content using AI to extract structured information"""
        prompt = """Analyze this business document and extract the following information in JSON format:
        1. company_info:
           - name: Company name
           - sector: Industry sector
           - location: Headquarters location
           - business_model: Brief description of business model
        2. financial_metrics: Latest financial metrics
        3. market_info:
           - market_size: Total addressable market size
           - growth_rate: Market growth rate
           - competition: Key competitive position
        4. key_highlights: List of 3-5 most important investment highlights
        
        Text to analyze:
        {text}
        """
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4.1",
                messages=[
                    {"role": "system", "content": "You are a financial analyst extracting key information from business documents. Return response in valid JSON format."},
                    {"role": "user", "content": prompt.format(text=text)}
                ],
                temperature=0
            )
            content = response.choices[0].message.content.strip()
            return json.loads(content)
        except Exception as e:
            print(f"AI analysis failed: {e}")
            return {}

    def extract_financial_metrics(self, text):
        """Extract financial metrics using AI with regex fallback"""
        try:
            return self.extract_financial_metrics_ai(text)
        except Exception as e:
            print(f"Falling back to regex extraction: {e}")
            return self._fallback_metric_extraction(text)

def ingest_file(filepath):
    """Main function to process PDF files"""
    ext = os.path.splitext(filepath)[-1].lower()
    if ext == '.pdf':
        return process_pdf(filepath)
    elif ext in ['.txt', '.md']:
        with open(filepath, 'r', encoding='utf-8') as f:
            return f.read()
    else:
        raise ValueError("Unsupported file type. Please provide a PDF or text file.")

def process_pdf(filepath):
    """Process PDF and extract all relevant information using AI"""
    processor = PDFProcessor()
    
    reader = PdfReader(filepath)
    text = ""
    for page in reader.pages:
        text += page.extract_text() or ""
    
    # if not text.strip():
    #     text = processor.extract_text_with_ocr(filepath)
    
    analysis = processor.analyze_text_with_ai(text)
    
    metrics = processor.extract_financial_metrics(text)
    
    return {
        'text': text,
        'analysis': analysis,
        'financial_metrics': metrics
    }
import json
import os

from anthropic import Anthropic
from dotenv import load_dotenv


load_dotenv()

client = Anthropic(
    api_key=os.getenv("ANTHROPIC_API_KEY")
)


MODEL = "claude-sonnet-4-5"


def ask_claude(prompt):
    response = client.messages.create(
        model=MODEL,
        max_tokens=1500,
        messages=[
            {
                "role": "user",
                "content": prompt,
            }
        ],
    )

    return response.content[0].text


def analyze_competitors(products):
    data = json.dumps(
        products,
        indent=2,
        ensure_ascii=False,
    )

    prompt = f"""
You are a competitive intelligence analyst
working for Reliance Digital.

Analyze the following REAL product data collected
from Reliance Digital and Vijay Sales.

Do not invent data.

PRODUCT DATA:
{data}

Provide a concise competitive intelligence report
covering:

1. Price differences
2. Discount patterns
3. Brand presence
4. Category coverage
5. Products where competitors appear significantly
   cheaper or more expensive
6. Potential competitive risks
7. Important opportunities for Reliance Digital

Only make claims supported by the supplied data.

Clearly distinguish observations from interpretation.

Return the answer with these headings:

PRICE ANALYSIS
DISCOUNT ANALYSIS
BRAND ANALYSIS
CATEGORY ANALYSIS
COMPETITIVE RISKS
OPPORTUNITIES
KEY TAKEAWAYS
"""

    return ask_claude(prompt)
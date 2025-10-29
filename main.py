from fastapi import FastAPI, Response
from pydantic import BaseModel
from openai import OpenAI
import os
from dotenv import load_dotenv

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

app = FastAPI(title="LLM Direct HTML Proposal Generator")

class ClientProposal(BaseModel):
    proposal_text: str

@app.post("/generate-html-direct/")
async def generate_html_direct(data: ClientProposal):

    prompt = f"""
    You are a professional project proposal writer.

    Task:
    - Read the client proposal below.
    - Break it into sections as listed:
      0. Project Overview
      1. We aim to
      2. Detailed Scope of Work
      3. Core Features
      4. Advanced Features
      5. Monetization System
      6. Admin & Backend Features
      7. Design & Branding
      8. Tech Stack table format
      9. Price & Timeline Breakdown table format 
      10. Requirements from Client
      11. Deliverables
      12. Support & Maintenance
      13. Testing and Quality
      14. Conclusion
    - Generate **valid HTML** with headings, lists, and tables.
    - DO NOT include triple backticks or escape characters like \\n.
    - Respond ONLY with clean HTML, ready to render in browser.

    Proposal Text:
    \"\"\"{data.proposal_text}\"\"\"
    """

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are an expert HTML proposal generator."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.2
    )

    html_output = response.choices[0].message.content.strip()
    html_output = html_output.replace("```html", "").replace("```", "").strip()


    return Response(content=html_output, media_type="text/html")

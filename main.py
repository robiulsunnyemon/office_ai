from fastapi import FastAPI, Response
from pydantic import BaseModel
from openai import OpenAI
import os
from dotenv import load_dotenv
import requests


load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

app = FastAPI(title="LLM Direct HTML Proposal Generator")


@app.get("/")
async def root():
    return {"message": "Hello MTS"}



class ClientProposal(BaseModel):
    client_text: str

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
    \"\"\"{data.client_text}\"\"\"
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



class ClientAreaData(BaseModel):
    client_text: str


@app.post("/generate-population-report/")
async def generate_population_report(data: ClientAreaData):
    prompt = f"""
    You are an expert population-data report writer.

    Task:
    - Read the area data below (raw client text) and produce a clear, professional population report.
    - Break the report into the following sections (use these exact headings in the HTML):
      0. Area Overview
      1. Population Summary
      2. Gender Breakdown
      3. Age Distribution
      4. Household & Housing
      5. Population Density
      6. Growth & Projections
      7. Migration & Demographics Notes
      8. Data Sources & Methodology
      9. Tables (summary tables shown as HTML <table>)
      10. Conclusions & Recommendations
    - Include for relevant sections:
      - Absolute counts (e.g., total population, number of males, number of females).
      - Percentages (e.g., % male, % female, % in each age group).
      - Basic metrics like average household size, population per km² (if area size provided), and annual growth rate (if past data provided).
      - At least two HTML tables: one for gender & totals, one for age-groups breakdown. Use additional tables where helpful.
    - Formatting rules:
      - Generate valid, well-structured HTML only (<!doctype html>, <html>, <head> with a sensible <title>, and <body>).
      - Use semantic headings (<h1>, <h2>, <h3>), paragraphs (<p>), lists (<ul>/<ol>), and tables (<table> with <thead>/<tbody>).
      - DO NOT include triple backticks or escape characters like \\n.
      - DO NOT output anything except the clean HTML document (no explanations, no extra notes).
    - Data handling:
      - If the client text includes numeric values (population counts, area in km², census years), use them directly and compute derived fields (percentages, density, growth) with clear labeled values.
      - If some data is missing, clearly state in the relevant section which items are missing and show results that can be computed from available data.
      - Round percentages to one decimal place and rates to two decimal places where appropriate.
    - Example table column headers to produce: "Category", "Count", "Percentage".
    - At the end include a short bulleted "Requirements from Client" list of any missing data needed to improve accuracy (e.g., area in km², previous census year counts, household definitions, source links).

    Client Area Data:
    \"\"\"{data.client_text}\"\"\"
    """

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are an expert HTML demographic data analyst."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.2
    )

    html_output = response.choices[0].message.content.strip()
    html_output = html_output.replace("```html", "").replace("```", "").strip()

    return Response(content=html_output, media_type="text/html")


class LocationCoordinates(BaseModel):
    latitude: float
    longitude: float


def reverse_geocode(lat: float, lon: float) -> str:
    """Reverse geocode latitude & longitude to get location name."""
    url = f"https://nominatim.openstreetmap.org/reverse"
    params = {
        "lat": lat,
        "lon": lon,
        "format": "json",
        "zoom": 10,
        "addressdetails": 1
    }
    headers = {"User-Agent": "GeoAPI/1.0"}
    response = requests.get(url, params=params, headers=headers)
    if response.status_code == 200:
        data = response.json()
        return data.get("display_name", "অজানা স্থান")
    return "অজানা স্থান"


@app.post("/generate-tourist-info-coordinates/")
async def generate_tourist_info_coordinates(data: LocationCoordinates):
    # Step 1: Convert coordinates to location name
    location_name = reverse_geocode(data.latitude, data.longitude)

    # Step 2: Build Bengali prompt
    prompt = f"""
    আপনি একজন অভিজ্ঞ ভ্রমণ ও পর্যটন বিষয়ক কনটেন্ট লেখক।

    কাজ:
    - নিচের স্থানটির জন্য একটি বিস্তারিত, তথ্যবহুল এবং আকর্ষণীয় ভ্রমণ গাইড তৈরি করুন।
    - আউটপুটটি অবশ্যই **পূর্ণাঙ্গ HTML** আকারে হবে।
    - নিচের সেকশনগুলো অনুসরণ করে লিখুন:
      0. পরিচিতি
      1. স্থান সম্পর্কে সংক্ষিপ্ত বিবরণ
      2. প্রধান দর্শনীয় স্থানসমূহ
      3. কেন আপনি এখানে ভ্রমণে যাবেন
      4. স্থানীয় সংস্কৃতি ও খাবার
      5. ভ্রমণের উপযুক্ত সময়
      6. যাতায়াত ও পৌঁছানোর উপায়
      7. থাকার ব্যবস্থা
      8. করণীয় ও অভিজ্ঞতা
      9. ভ্রমণ পরামর্শ
      10. নিরাপত্তা ও আচরণবিধি
      11. পরিবেশ সচেতনতা
      12. উপসংহার
    - শিরোনামগুলোর জন্য <h1>, <h2> এবং অনুচ্ছেদগুলোর জন্য <p> ট্যাগ ব্যবহার করুন।
    - প্রয়োজনমতো <ul>/<li> লিস্ট ও <table> ব্যবহার করতে পারেন।
    - Markdown, ব্যাকটিক বা \n জাতীয় কোনো এস্কেপ ক্যারেক্টার ব্যবহার করবেন না।
    - লেখাটি যেন প্রাকৃতিক, সাবলীল ও পাঠযোগ্য হয় — ভ্রমণ ব্লগ বা ম্যাগাজিনের মতো।
    - জায়গাটির প্রাকৃতিক সৌন্দর্য, সংস্কৃতি, ইতিহাস, খাবার এবং মানুষ সম্পর্কে বাস্তবসম্মত তথ্য অন্তর্ভুক্ত করুন।
    - যদি নির্দিষ্ট তথ্য পাওয়া না যায়, তবে অঞ্চলভিত্তিক বাস্তবসম্মত সাধারণ অনুমান ব্যবহার করুন।
    - সব টেক্সট **বাংলা ভাষায়** লিখবেন, কিন্তু HTML ট্যাগ ইংরেজিতেই রাখবেন।

    স্থান: "{location_name}"

    অবস্থান (Coordinates): অক্ষাংশ {data.latitude}, দ্রাঘিমাংশ {data.longitude}
    """

    # Step 3: Get AI-generated HTML
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "আপনি একজন পেশাদার বাংলা HTML ভ্রমণবিষয়ক কনটেন্ট জেনারেটর।"},
            {"role": "user", "content": prompt}
        ],
        temperature=0.7
    )

    html_output = response.choices[0].message.content.strip()
    html_output = html_output.replace("```html", "").replace("```", "").strip()

    # Step 4: Return HTML response
    return Response(content=html_output, media_type="text/html")
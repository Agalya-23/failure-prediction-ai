
import os
import json
from pathlib import Path
from dotenv import load_dotenv
from google import genai

env_file = Path(__file__).resolve().parent.parent / ".env"
if env_file.exists():
    load_dotenv(dotenv_path=env_file)
else:
    load_dotenv()

client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))

PROMPT = """You are a market research analyst. Analyse this project and respond with JSON only.

Project: {project_name} ({project_type})
Industry: {industry} | Business model: {business_model}
Target market: {target_market} | Budget: ${budget}
Description: {description}

Return exactly this JSON shape:
{{
  "market": {{
    "tam": "e.g. $2.4B",
    "sam": "e.g. $850M",
    "som": "e.g. $12M",
    "growth_rate": "e.g. 8.2% CAGR",
    "summary": "2-3 sentence market overview",
    "trends": [
      {{"year": 2022, "market_size_usd_bn": 1.8}}
    ],
    "opportunities": ["..."],
    "challenges": ["..."]
  }},
  "competitors": [
    {{
      "competitor_name": "...",
      "competitor_type": "direct or indirect",
      "market_position": "1-2 sentences",
      "competitive_risk": "Low, Medium or High"
    }}
  ]
}}

Give trends for 2022-2026 and 3-5 real, existing competitors.
All figures are estimates. Do not invent real-world facts."""

def analyse_market(project) -> dict:
    prompt = PROMPT.format(
        project_name=project.project_name,
        project_type=project.project_type,
        industry=project.industry,
        business_model=project.business_model,
        target_market=project.target_market,
        budget=project.budget,
        description=project.description
    )

    format_config = {
        "type": "text",
        "mime_type": "application/json",
        "schema": {
            "type": "object",
            "properties": {
                "market": {
                    "type": "object",
                    "properties": {
                        "tam": {"type": "string"},
                        "sam": {"type": "string"},
                        "som": {"type": "string"},
                        "growth_rate": {"type": "string"},
                        "summary": {"type": "string"},
                        "trends": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "year": {"type": "integer"},
                                    "market_size_usd_bn": {"type": "number"}
                                },
                                "required": ["year", "market_size_usd_bn"]
                            }
                        },
                        "opportunities": {
                            "type": "array",
                            "items": {"type": "string"}
                        },
                        "challenges": {
                            "type": "array",
                            "items": {"type": "string"}
                        }
                    },
                    "required": [
                        "tam", "sam", "som", "growth_rate",
                        "summary", "trends", "opportunities", "challenges"
                    ]
                },
                "competitors": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "competitor_name": {"type": "string"},
                            "competitor_type": {"type": "string"},
                            "market_position": {"type": "string"},
                            "competitive_risk": {"type": "string"}
                        },
                        "required": [
                            "competitor_name", "competitor_type",
                            "market_position", "competitive_risk"
                        ]
                    }
                }
            },
            "required": ["market", "competitors"]
        }
    }

    primary_model = os.getenv("GEMINI_MODEL", "gemini-3.1-flash-lite")
    models_to_try = [primary_model]
    for fallback in ["gemini-3.1-flash-lite", "gemini-3.5-flash", "gemini-3.8-flash"]:
        if fallback not in models_to_try:
            models_to_try.append(fallback)

    response = None
    last_error = None
    for model_name in models_to_try:
        try:
            response = client.interactions.create(
                model=model_name,
                input=prompt,
                response_format=format_config
            )
            if response and getattr(response, "output_text", None):
                break
        except Exception as e:
            last_error = e
            continue

    if response is None or not getattr(response, "output_text", None):
        raise last_error or RuntimeError("All Gemini models failed to generate a response.")

    output = response.output_text.strip()
    if output.startswith("```json"):
        output = output[7:]
    elif output.startswith("```"):
        output = output[3:]
    if output.endswith("```"):
        output = output[:-3]
    return json.loads(output.strip())

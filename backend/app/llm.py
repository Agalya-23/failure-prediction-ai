
import os
import json
import re
from pathlib import Path
from dotenv import load_dotenv
from google import genai

def get_client():
    env_file = Path(__file__).resolve().parent.parent / ".env"
    if env_file.exists():
        load_dotenv(dotenv_path=env_file, override=True)
    else:
        load_dotenv(override=True)
    return genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))

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

RISK_PROMPT = """You are an elite venture capitalist and startup failure risk assessment expert.
Analyse the failure probability, strategic risks, and SWOT for this project. Respond with JSON only.

Project: {project_name} ({project_type})
Industry: {industry} | Business model: {business_model}
Target market: {target_market} | Budget: ${budget}
Description: {description}
{market_context}

Return exactly this JSON structure:
{{
  "overall_risk_score": 72,
  "risk_level": "High Risk",
  "success_probability": 35,
  "feasibility_score": 42,
  "feasibility_status": "Moderate Feasibility with Significant Improvements Needed",
  "financial_sustainability": 38,
  "team_capability": 50,
  "competitive_advantage": 35,
  "resource_availability": 65,
  "key_risk_factors": [
    {{
      "factor": "Team Expertise",
      "description": "Limited technical and execution experience for target project scope"
    }},
    {{
      "factor": "Innovation Gap",
      "description": "Lack of high-defensibility IP or proprietary moat against incumbents"
    }},
    {{
      "factor": "Capital Runway",
      "description": "Budget may be insufficient for high customer acquisition cost in this market"
    }}
  ],
  "swot": {{
    "strengths": [
      "Unique value proposition tailored for modern user needs",
      "Agile execution structure and low initial operational overhead",
      "Early mover advantage in regional niche segment"
    ],
    "weaknesses": [
      "Limited marketing budget relative to category leaders",
      "Low initial brand awareness and customer trust",
      "Dependency on third-party service providers and key personnel"
    ],
    "opportunities": [
      "Rapidly rising market demand and digitization trends",
      "Potential strategic distribution partnerships",
      "Expansion into adjacent vertical offerings"
    ],
    "threats": [
      "Aggressive price competition from well-funded incumbents",
      "Rapidly changing technology landscape and consumer preferences",
      "Evolving regulatory compliance and platform dependency risks"
    ]
  }}
}}

Guidelines:
1. overall_risk_score: Integer from 0 to 100 (higher means higher risk of failure).
2. risk_level: One of "Low Risk" (0-30), "Moderate Risk" (31-50), "High Risk" (51-70), "Critical Risk" (71-100).
3. success_probability: Integer from 5 to 95 (percentage chance of commercial success).
4. feasibility_score: Integer from 0 to 100.
5. feasibility_status: A 1-sentence assessment summarizing overall feasibility.
6. Assessment metrics (financial_sustainability, team_capability, competitive_advantage, resource_availability): Each an integer from 0 to 100.
7. key_risk_factors: 3 to 5 realistic risk factors with short explanation.
8. swot: 3 to 5 clear, insightful bullet points for each category (strengths, weaknesses, opportunities, threats).
All figures and evaluations must be customized to the specific industry, business model, and project details."""

def _execute_gemini_call(prompt: str, format_config: dict | None = None) -> dict:
    client = get_client()
    primary_model = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
    models_to_try = [primary_model]
    for fallback in ["gemini-2.5-flash", "gemini-2.0-flash", "gemini-1.5-flash", "gemini-3.1-flash-lite", "gemini-3.5-flash"]:
        if fallback not in models_to_try:
            models_to_try.append(fallback)

    response_text = None
    last_error = None

    for model_name in models_to_try:
        # Try interactions.create first if available
        if hasattr(client, "interactions"):
            try:
                kwargs = {"model": model_name, "input": prompt}
                if format_config:
                    kwargs["response_format"] = format_config
                resp = client.interactions.create(**kwargs)
                if resp and getattr(resp, "output_text", None):
                    response_text = resp.output_text
                    break
            except Exception as e:
                last_error = e

        # Fallback to models.generate_content
        if hasattr(client, "models"):
            try:
                resp = client.models.generate_content(
                    model=model_name,
                    contents=prompt
                )
                if resp and getattr(resp, "text", None):
                    response_text = resp.text
                    break
            except Exception as e:
                last_error = e

    if not response_text:
        raise last_error or RuntimeError("All Gemini model attempts failed to produce output.")

    cleaned = response_text.strip()
    if cleaned.startswith("```json"):
        cleaned = cleaned[7:]
    elif cleaned.startswith("```"):
        cleaned = cleaned[3:]
    if cleaned.endswith("```"):
        cleaned = cleaned[:-3]
    cleaned = cleaned.strip()

    # In case there is text before or after json
    match = re.search(r"(\{.*\})", cleaned, re.DOTALL)
    if match:
        cleaned = match.group(1)

    return json.loads(cleaned)

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

    return _execute_gemini_call(prompt, format_config)

SWOT_PROMPT = """You are a senior strategic business consultant.
Perform a thorough, realistic SWOT Analysis for this project based on real market conditions and competitive landscape. Respond with JSON only.

Project: {project_name} ({project_type})
Industry: {industry} | Business model: {business_model}
Target market: {target_market} | Budget: ${budget}
Description: {description}
{market_context}

Return exactly this JSON structure:
{{
  "strengths": [
    "e.g. Unique technological algorithm providing 2x faster results",
    "e.g. Agile team with low burn rate"
  ],
  "weaknesses": [
    "e.g. Limited initial marketing budget compared to established players",
    "e.g. Lack of proven brand trust in enterprise segment"
  ],
  "opportunities": [
    "e.g. Rapidly growing demand in underserved regional markets",
    "e.g. Strategic partnership possibilities with existing vendors"
  ],
  "threats": [
    "e.g. Entrenched incumbents with significant price-slashing capability",
    "e.g. Shifting regulatory compliances"
  ],
  "summary": "A concise 2-sentence executive summary of the SWOT findings."
}}

Give 3 to 5 realistic, concrete bullet points for each quadrant."""

FEASIBILITY_PROMPT = """You are an expert technical and operational project feasibility auditor.
Assess the feasibility of this project covering Resources, Timeline, Advantages, Proofs, and Overall Feasibility. Respond with JSON only.

Project: {project_name} ({project_type})
Industry: {industry} | Business model: {business_model}
Target market: {target_market} | Budget: ${budget}
Description: {description}
{market_context}

Return exactly this JSON structure:
{{
  "resources": "Detail key human capital, cloud infrastructure, domain expertise, and tools needed vs budget adequacy.",
  "timeline": "Estimated realistic timeline to MVP and market launch (e.g. 3-6 months prototype, 6-12 months launch).",
  "advantages": "Core defensible competitive advantages and value propositions that make this feasible.",
  "proofs": "Market validations, proof of concept signals, consumer adoption indicators or comparable success cases.",
  "feasibility_score": 74.5,
  "feasibility_status": "High Feasibility with Strong Market Potential"
}}

Guidelines:
1. feasibility_score: Number between 0 and 100.
2. feasibility_status: Brief status like 'High Feasibility', 'Moderate Feasibility with Significant Improvements Needed', etc.
3. Be realistic based on budget and complexity."""

RISK_INPUTS_ESTIMATE_PROMPT = """You are an expert venture analyst evaluating startup risk parameters on a 1 to 5 scale (1 = lowest/worst, 5 = highest/best/most favorable).
Evaluate these 7 parameters for the given project:

Project: {project_name} ({project_type})
Industry: {industry} | Business model: {business_model}
Target market: {target_market} | Budget: ${budget}
Description: {description}

Return JSON with 7 integers between 1 and 5:
{{
  "budget_adequacy": 3,
  "market_validation": 3,
  "technical_readiness": 3,
  "team_experience": 3,
  "resource_availability": 3,
  "competition_intensity": 4,
  "regulatory_complexity": 2
}}"""

def generate_swot(project) -> dict:
    market_context = ""
    if getattr(project, "market_analysis", None):
        m = project.market_analysis
        market_context = f"\nMarket Summary: {m.summary} | Growth Rate: {m.growth_rate}"
        if getattr(project, "competitors", None):
            comps = ", ".join([c.competitor_name for c in project.competitors[:4]])
            market_context += f"\nKnown Competitors: {comps}"

    prompt = SWOT_PROMPT.format(
        project_name=project.project_name,
        project_type=project.project_type,
        industry=project.industry,
        business_model=project.business_model,
        target_market=project.target_market,
        budget=project.budget,
        description=project.description,
        market_context=market_context
    )

    format_config = {
        "type": "text",
        "mime_type": "application/json",
        "schema": {
            "type": "object",
            "properties": {
                "strengths": {"type": "array", "items": {"type": "string"}},
                "weaknesses": {"type": "array", "items": {"type": "string"}},
                "opportunities": {"type": "array", "items": {"type": "string"}},
                "threats": {"type": "array", "items": {"type": "string"}},
                "summary": {"type": "string"}
            },
            "required": ["strengths", "weaknesses", "opportunities", "threats", "summary"]
        }
    }

    return _execute_gemini_call(prompt, format_config)

def generate_feasibility(project) -> dict:
    market_context = ""
    if getattr(project, "market_analysis", None):
        m = project.market_analysis
        market_context = f"\nMarket Summary: {m.summary} | Growth Rate: {m.growth_rate}"

    prompt = FEASIBILITY_PROMPT.format(
        project_name=project.project_name,
        project_type=project.project_type,
        industry=project.industry,
        business_model=project.business_model,
        target_market=project.target_market,
        budget=project.budget,
        description=project.description,
        market_context=market_context
    )

    format_config = {
        "type": "text",
        "mime_type": "application/json",
        "schema": {
            "type": "object",
            "properties": {
                "resources": {"type": "string"},
                "timeline": {"type": "string"},
                "advantages": {"type": "string"},
                "proofs": {"type": "string"},
                "feasibility_score": {"type": "number"},
                "feasibility_status": {"type": "string"}
            },
            "required": ["resources", "timeline", "advantages", "proofs", "feasibility_score", "feasibility_status"]
        }
    }

    return _execute_gemini_call(prompt, format_config)

def estimate_risk_inputs(project) -> dict:
    prompt = RISK_INPUTS_ESTIMATE_PROMPT.format(
        project_name=project.project_name,
        project_type=project.project_type,
        industry=project.industry,
        business_model=project.business_model,
        target_market=project.target_market,
        budget=project.budget,
        description=project.description
    )

    try:
        res = _execute_gemini_call(prompt)
        keys = ["budget_adequacy", "market_validation", "technical_readiness", "team_experience", "resource_availability", "competition_intensity", "regulatory_complexity"]
        return {k: max(1, min(5, int(res.get(k, 3)))) for k in keys}
    except Exception:
        return {
            "budget_adequacy": 3,
            "market_validation": 3,
            "technical_readiness": 3,
            "team_experience": 3,
            "resource_availability": 3,
            "competition_intensity": 3,
            "regulatory_complexity": 2
        }

import requests
import json
import time
import csv # Added for CSV output
from typing import List, Optional, Any
from pydantic import BaseModel, Field, HttpUrl, model_validator
from datetime import datetime

# 1. Define the Pydantic Model
class Company(BaseModel):
    name: str
    headquarters: Optional[str] = None
    certified_since_timestamp: Optional[int] = Field(alias="initialCertificationDateTimestamp", default=None)
    certified_since_date: Optional[datetime] = None # Will be derived
    industry: Optional[str] = None
    sector: Optional[str] = None
    operates_in: List[str] = Field(default_factory=list, alias="countries")
    website_url: Optional[HttpUrl] = None # Will be derived
    description: Optional[str] = None
    overall_impact_score_str: Optional[str] = Field(alias="latestVerifiedScore", default=None)
    overall_impact_score_float: Optional[float] = None # Will be derived
    company_slug: Optional[str] = Field(alias="slug", default=None) # Keep original slug

    @model_validator(mode='before')
    @classmethod
    def prepare_data(cls, data: Any) -> Any:
        if isinstance(data, dict):
            # Construct Headquarters
            hq_parts = []
            if data.get("hqCity"): hq_parts.append(data["hqCity"])
            if data.get("hqProvince"): hq_parts.append(data["hqProvince"])
            if data.get("hqCountry"): hq_parts.append(data["hqCountry"])
            data["headquarters"] = ", ".join(hq_parts) if hq_parts else None

            # Convert Certified Since Timestamp to Datetime
            ts = data.get("initialCertificationDateTimestamp")
            if ts:
                try:
                    data["certified_since_date"] = datetime.fromtimestamp(int(ts) / 1000)
                except (ValueError, TypeError):
                    data["certified_since_date"] = None
            else:
                data["certified_since_date"] = None

            # Convert Overall Impact Score to Float
            score_str = data.get("latestVerifiedScore")
            if score_str:
                try:
                    data["overall_impact_score_float"] = float(score_str)
                except (ValueError, TypeError):
                    data["overall_impact_score_float"] = None
            else:
                data["overall_impact_score_float"] = None

            # Construct Website URL from slug
            slug = data.get("slug")
            if slug:
                data["website_url"] = f"https://www.bcorporation.net/en-us/find-a-b-corp/company/{slug}"
            elif data.get("website"): # Fallback
                 data["website_url"] = data.get("website")
            else:
                data["website_url"] = None
        return data

# --- API Request Details ---
headers = {
    'accept': 'application/json, text/plain, */*',
    'accept-language': 'en-US,en;q=0.7',
    'content-type': 'text/plain',
    'origin': 'https://www.bcorporation.net',
    'priority': 'u=1, i',
    'referer': 'https://www.bcorporation.net/',
    'sec-ch-ua': '"Chromium";v="136", "Brave";v="136", "Not.A/Brand";v="99"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
    'sec-fetch-dest': 'empty',
    'sec-fetch-mode': 'cors',
    'sec-fetch-site': 'cross-site',
    'sec-gpc': '1',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36',
}

api_key_params = {
    'x-typesense-api-key': 'IpJoOPZUczKNxR54gCnU8sjVNGCyXj21',
}

base_url = 'https://94eo8lmsqa0nd3j5p.a1.typesense.net/multi_search'

# --- Main Scraping Logic ---
all_companies_data: List[Company] = []
current_page = 1
per_page_limit = 250
total_companies_found = 0

search_payload_template_dict = {
    "searches": [{
        "query_by": "name,description,websiteKeywords,countries,industry,sector,hqCountry,hqProvince,hqCity,hqPostalCode,provinces,cities,size,demographicsList",
        "exhaustive_search": True,
        "sort_by": "initialCertificationDateTimestamp:desc",
        "highlight_full_fields": "name,description,websiteKeywords,countries,industry,sector,hqCountry,hqProvince,hqCity,hqPostalCode,provinces,cities,size,demographicsList",
        "collection": "companies-production-en-us",
        "q": "*",
        "facet_by": "countries,demographicsList,hqCountry,industry,size",
        "max_facet_values": 10,
        "page": current_page,
        "per_page": per_page_limit
    }]
}

print("Starting to fetch B Corp company data...")

while True:
    current_payload_dict = json.loads(json.dumps(search_payload_template_dict))
    current_payload_dict["searches"][0]["page"] = current_page
    current_payload_str = json.dumps(current_payload_dict)

    print(f"Fetching page {current_page}...")

    try:
        response = requests.post(base_url, params=api_key_params, headers=headers, data=current_payload_str)
        response.raise_for_status()
        response_json = response.json()
    except requests.exceptions.RequestException as e:
        print(f"Request failed for page {current_page}: {e}")
        if response:
             print(f"Response content: {response.text[:500]}")
        time.sleep(5)
        break
    except json.JSONDecodeError:
        print(f"Failed to decode JSON for page {current_page}. Response text: {response.text[:500]}")
        break

    if not response_json.get("results") or not isinstance(response_json["results"], list) or not response_json["results"]:
        print("No 'results' array in response or it's empty. Stopping.")
        break

    search_result = response_json["results"][0]

    if current_page == 1:
        total_companies_found = search_result.get("found", 0)
        if total_companies_found == 0:
            print("API reported 0 companies found. Exiting.")
            break
        print(f"Total companies to fetch: {total_companies_found}")

    hits = search_result.get("hits", [])
    if not hits:
        print(f"No 'hits' on page {current_page}, but expected more. Ending.")
        break

    for hit in hits:
        doc = hit.get("document")
        if doc:
            try:
                company_obj = Company(**doc)
                all_companies_data.append(company_obj)
            except Exception as e:
                print(f"Error processing company: {doc.get('name', 'Unknown name')}. Error: {e}")
                print(f"Problematic document data: {json.dumps(doc, indent=2)}")
        else:
            print(f"Found a hit without a 'document' field on page {current_page}")

    print(f"Fetched {len(hits)} companies from page {current_page}. Total collected: {len(all_companies_data)}")

    if total_companies_found > 0 and len(all_companies_data) >= total_companies_found:
        print("All companies fetched based on 'found' count.")
        break
    
    if len(hits) < per_page_limit and current_page > 1:
        print(f"Received less than {per_page_limit} hits on page {current_page}, assuming end of results.")
        break

    current_page += 1
    time.sleep(0.5)

print(f"\n--- Successfully extracted {len(all_companies_data)} companies ---")

# --- Example: Print details for the first 5 companies and Save to JSON/CSV ---
if all_companies_data:
    print("\n--- Sample of Extracted Data (First 5 Companies) ---")
    for i, company in enumerate(all_companies_data[:5]):
        print(f"\n--- Company {i+1} ---")
        print(f"Name: {company.name}")
        print(f"Headquarters: {company.headquarters}")
        certified_date_str = company.certified_since_date.strftime('%Y-%m-%d') if company.certified_since_date else "N/A"
        print(f"Certified Since: {certified_date_str}")
        print(f"Industry: {company.industry}")
        print(f"Sector: {company.sector}")
        print(f"Operates In: {', '.join(company.operates_in) if company.operates_in else 'N/A'}")
        print(f"Website: {company.website_url}")
        description_preview = company.description[:100] + '...' if company.description and len(company.description) > 100 else company.description
        print(f"Description: {description_preview}")
        print(f"Overall Impact Score: {company.overall_impact_score_float}")

    # --- Save all data to a JSON file ---
    try:
        output_data_json = [company.model_dump(mode='json') for company in all_companies_data]
    except AttributeError: # Fallback for Pydantic v1
        output_data_json = [company.dict() for company in all_companies_data]

    json_filename = "b_corp_companies_data.json"
    with open(json_filename, "w", encoding="utf-8") as f:
        json.dump(output_data_json, f, indent=2, ensure_ascii=False)
    print(f"\nFull data for {len(all_companies_data)} companies saved to {json_filename}")

    # --- Save all data to a CSV file ---
    csv_filename = "b_corp_companies_data.csv"
    csv_headers = [
        "Name",
        "Headquarters",
        "Certified Since",
        "Industry",
        "Sector",
        "Operates In",
        "Website",
        "Description",
        "Overall Impact Score"
    ]

    with open(csv_filename, "w", newline='', encoding="utf-8") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(csv_headers) # Write the header

        for company in all_companies_data:
            certified_date_str = company.certified_since_date.strftime('%Y-%m-%d') if company.certified_since_date else ''
            operates_in_str = ", ".join(company.operates_in) if company.operates_in else ''
            website_str = str(company.website_url) if company.website_url else ''
            
            writer.writerow([
                company.name or '',
                company.headquarters or '',
                certified_date_str,
                company.industry or '',
                company.sector or '',
                operates_in_str,
                website_str,
                company.description or '',
                company.overall_impact_score_float if company.overall_impact_score_float is not None else ''
            ])
    print(f"Full data for {len(all_companies_data)} companies also saved to {csv_filename}")

else:
    print("\nNo company data was extracted.")
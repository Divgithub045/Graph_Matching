from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict
import json
from datetime import datetime
import sys
import os
import logging

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Add lib to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from lib.ml_inference import WastePredictor
from lib.graph_matching import GraphMatcher
from lib.buyer_database import BuyerDatabase

app = FastAPI(title="Graph Matching API", version="1.0.0")

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services
try:
    predictor = WastePredictor()
    buyer_db = BuyerDatabase(r".\data\waste_buyers_india_updated_cities.csv")
    matcher = GraphMatcher(buyer_db)
    logger.info("Services initialized successfully")
except Exception as e:
    logger.error(f"Error initializing services: {e}")

# ============= REQUEST/RESPONSE MODELS =============

class OperationalData(BaseModel):
    industry: str
    product: str
    process: str
    machinery: str
    scale: str
    location: str
    units_per_month: int = 1000  # Default value

class FormSubmission(BaseModel):
    operational_data: OperationalData
    timestamp: Optional[str] = None

class MatchResult(BaseModel):
    id: int
    company: str
    type: str
    materialMatch: float
    qualityFit: float
    distance: float
    costSaving: float
    environmentalImpact: Dict
    compliance: str
    overallScore: float

# ============= ENDPOINTS =============

@app.get("/")
async def root():
    return {"message": "Graph Matching API is running"}

@app.post("/api/predict-waste")
async def predict_waste(data: OperationalData):
    """
    Predict waste profile from operational data
    """
    try:
        logger.info(f"Predicting waste for: {data.model_dump()}")
        facility_input = data.model_dump()
        waste_profile = predictor.predict(facility_input)
        logger.info(f"Prediction successful")
        return {"success": True, "waste_profile": waste_profile}
    except Exception as e:
        logger.error(f"Error in predict_waste: {str(e)}", exc_info=True)
        raise HTTPException(status_code=400, detail=str(e))

# @app.post("/api/find-matches")
# async def find_matches(data: OperationalData):
#     """
#     Find waste buyer matches based on operational data
#     """
#     try:
#         logger.info(f"Finding matches for: {data.model_dump()}")
#         # Predict waste profile
#         facility_input = data.model_dump()
#         waste_profile = predictor.predict(facility_input)
        
#         # Get buyers from database
#         buyers = buyer_db.search_by_location(data.location)
        
#         # Get facility location coordinates from first buyer in that city (or use defaults)
#         facility_lat, facility_lng = 0, 0
#         for buyer in buyers:
#             if buyer.get('city', '').lower() == data.location.lower():
#                 facility_lat = buyer.get('lat', 0)
#                 facility_lng = buyer.get('lng', 0)
#                 break
        
#         # Add location to waste profile with proper coordinates
#         waste_profile['location'] = {
#             'name': data.location,
#             'lat': facility_lat,
#             'lng': facility_lng
#         }
#         waste_profile['facility_industry'] = data.industry
        
#         # Build graph and find matches
#         graph = matcher.build_graph(waste_profile, buyers)
#         matches = matcher.find_optimal_matches(graph, waste_profile)
        
#         logger.info(f"Found {len(matches)} matches")
#         return {"success": True, "matches": matches}
#     except Exception as e:
#         logger.error(f"Error in find_otpimal_matches: {str(e)}", exc_info=True)
#         raise HTTPException(status_code=400, detail=str(e))
@app.post("/api/find-matches")
async def find_matches(data: OperationalData):
    """
    Find waste buyer matches based on operational data
    """
    try:
        logger.info(f"Finding matches for: {data.model_dump()}")
        # Predict waste profile
        facility_input = data.model_dump()
        waste_profile = predictor.predict(facility_input)
        
        # Get buyers from database
        buyers = buyer_db.search_by_location(data.location)
        
        # Get facility location coordinates from first buyer in that city (or use defaults)
        facility_lat, facility_lng = 0, 0
        for buyer in buyers:
            if buyer.get('city', '').lower() == data.location.lower():
                facility_lat = buyer.get('lat', 0)
                facility_lng = buyer.get('lng', 0)
                break
        
        # Add location to waste profile with proper coordinates
        waste_profile['location'] = {
            'name': data.location,
            'lat': facility_lat,
            'lng': facility_lng
        }
        waste_profile['facility_industry'] = data.industry
        
        # Find optimal matches (method builds graph internally)
        matches = matcher.find_optimal_matches(waste_profile)
        
        logger.info(f"Found {len(matches)} matches")
        return {"success": True, "matches": matches}
    except Exception as e:
        logger.error(f"Error in find_matches: {str(e)}", exc_info=True)
        raise HTTPException(status_code=400, detail=str(e))
@app.post("/api/save-form")
async def save_form(submission: FormSubmission):
    """
    Save form submission data to file
    """
    try:
        timestamp = submission.timestamp or datetime.now().isoformat()
        
        # Save to JSON file
        output_file = "output/form_submissions.json"
        
        # Create output directory if it doesn't exist
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        
        # Load existing submissions
        submissions = []
        if os.path.exists(output_file):
            with open(output_file, 'r') as f:
                submissions = json.load(f)
        
        # Add new submission
        submissions.append({
            "timestamp": timestamp,
            "data": submission.operational_data.model_dump()
        })
        
        # Save back
        with open(output_file, 'w') as f:
            json.dump(submissions, f, indent=2)
        
        logger.info(f"Form saved successfully at {timestamp}")
        return {"success": True, "message": "Form saved successfully"}
    except Exception as e:
        logger.error(f"Error in save_form: {str(e)}", exc_info=True)
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/api/save-matches")
async def save_matches(matches: List[MatchResult]):
    """
    Save match results to file
    """
    try:
        output_file = "output/matches.json"
        
        # Create output directory if it doesn't exist
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        
        with open(output_file, 'w') as f:
            json.dump([m.model_dump() for m in matches], f, indent=2)
        
        logger.info(f"Saved {len(matches)} matches")
        return {"success": True, "message": "Matches saved successfully"}
    except Exception as e:
        logger.error(f"Error in save_matches: {str(e)}", exc_info=True)
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/api/submissions")
async def get_submissions():
    """
    Get all saved form submissions
    """
    try:
        output_file = "output/form_submissions.json"
        
        if not os.path.exists(output_file):
            return {"submissions": []}
        
        with open(output_file, 'r') as f:
            submissions = json.load(f)
        
        return {"submissions": submissions}
    except Exception as e:
        logger.error(f"Error in get_submissions: {str(e)}", exc_info=True)
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/api/add-buyer")
async def add_buyer(buyer_data: dict):
    """
    Add a new buyer to the CSV database
    """
    try:
        import csv
        import pandas as pd
        
        csv_path = r".\data\waste_buyers_india_updated_cities.csv"
        
        # Read existing CSV to get the last buyer_id
        df = pd.read_csv(csv_path)
        
        # Generate new buyer_id
        if len(df) > 0:
            last_id = df['buyer_id'].iloc[-1]  # e.g., "B103"
            id_number = int(last_id[1:]) + 1  # Extract number and increment
            new_buyer_id = f"B{id_number:03d}"  # Format with zero-padding
        else:
            new_buyer_id = "B001"
        
        # Prepare new row with all required fields
        new_row = {
            'buyer_id': new_buyer_id,
            'company_name': buyer_data.get('company_name', ''),
            'company_type': buyer_data.get('company_type', ''),
            'accepted_waste_types': buyer_data.get('accepted_waste_types', ''),
            'accepted_categories': buyer_data.get('accepted_categories', ''),
            'min_quality_grade': buyer_data.get('min_quality_grade', ''),
            'min_monthly_volume_tons': buyer_data.get('min_monthly_volume_tons', 0),
            'max_monthly_volume_tons': buyer_data.get('max_monthly_volume_tons', 0),
            'city': buyer_data.get('city', ''),
            'state': buyer_data.get('state', ''),
            'lat': buyer_data.get('lat', 0.0),
            'lng': buyer_data.get('lng', 0.0),
            'pricing_model': buyer_data.get('pricing_model', ''),
            'certifications': buyer_data.get('certifications', ''),
            'contact_email': buyer_data.get('contact_email', ''),
            'contact_name': buyer_data.get('contact_name', '')
        }
        
        # Append to CSV
        new_df = pd.DataFrame([new_row])
        new_df.to_csv(csv_path, mode='a', header=False, index=False)
        
        logger.info(f"Successfully added new buyer: {new_buyer_id}")
        
        return {
            "success": True,
            "message": f"Buyer {new_buyer_id} added successfully",
            "buyer_id": new_buyer_id
        }
    
    except Exception as e:
        logger.error(f"Error in add_buyer: {str(e)}", exc_info=True)
        raise HTTPException(status_code=400, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
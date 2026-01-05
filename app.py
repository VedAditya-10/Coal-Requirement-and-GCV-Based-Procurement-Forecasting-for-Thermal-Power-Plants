from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import pandas as pd
import numpy as np
import lightgbm as lgb
import pickle
import calendar
import os
import sys
from pathlib import Path

app = FastAPI(title="Coal Demand Forecasting")

app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv("ALLOWED_ORIGINS", "*").split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

try:
    base_model = lgb.Booster(model_file='plf_base_model.txt')
    enhanced_model = lgb.Booster(model_file='plf_enhanced_model.txt')
    print("Models loaded successfully")
except Exception as e:
    print(f"ERROR: Failed to load models: {e}")
    print("Please ensure plf_base_model.txt and plf_enhanced_model.txt exist in the project directory.")
    sys.exit(1)

try:
    with open('generalized_model_metadata.pkl', 'rb') as f:
        metadata = pickle.load(f)
    print(" Metadata loaded successfully")
except Exception as e:
    print(f" ERROR: Failed to load metadata: {e}")
    print("Please ensure generalized_model_metadata.pkl exists in the project directory.")
    sys.exit(1)

try:
    df_reference = pd.read_csv('FINAL_MERGED_DATA.csv')
    df_reference = df_reference[df_reference['Capacity'].notna()]
    print(f"Reference data loaded: {len(df_reference['plant_key'].unique())} plants available")
except Exception as e:
    print(f" ERROR: Failed to load reference data: {e}")
    print("Please ensure FINAL_MERGED_DATA.csv exists in the project directory.")
    sys.exit(1)

class ForecastRequest(BaseModel):
    is_new_plant: bool
    year: int
    month: int
    plant_key: str = None
    capacity: float = None
    technology: str = None

def calculate_electricity_generation(capacity_mw, plf, year, month):
    days = calendar.monthrange(year, month)[1]
    return capacity_mw * plf * 24 * days * 1000

def calculate_coal_requirement(electricity_kwh, heat_rate, gcv, aux_consumption):
    aux = aux_consumption / 100 if aux_consumption > 1 else aux_consumption
    coal_kg = (electricity_kwh * heat_rate) / (gcv * (1 - aux))
    return coal_kg / 1000

app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "coal-demand-forecasting",
        "models_loaded": True,
        "plants_available": len(df_reference['plant_key'].unique())
    }

@app.get("/", response_class=HTMLResponse)
async def home():
    with open('static/index.html', 'r') as f:
        return f.read()

@app.get("/plants")
async def get_plants():
    return sorted(df_reference['plant_key'].unique().tolist())

@app.post("/forecast")
async def predict(request: ForecastRequest):
    try:
        if request.is_new_plant:
            capacity = request.capacity
            technology = request.technology
            
            capacity_norm = (capacity - metadata['capacity_stats']['mean']) / metadata['capacity_stats']['std']
            
            if capacity < 500:
                band = 'Small'
            elif capacity < 1500:
                band = 'Medium'
            else:
                band = 'Large'
            
            tech_encoded = metadata['tech_map'][technology]
            band_encoded = metadata['band_map'][band]
            
            tech_month_avg = pd.DataFrame(metadata['tech_month_avg'])
            band_month_avg = pd.DataFrame(metadata['band_month_avg'])
            
            avg_tech = tech_month_avg[(tech_month_avg['Technology'] == technology) & 
                                      (tech_month_avg['Month'] == request.month)]['avg_plf_tech_month'].values[0]
            avg_band = band_month_avg[(band_month_avg['capacity_band'] == band) & 
                                      (band_month_avg['Month'] == request.month)]['avg_plf_band_month'].values[0]
            
            features = pd.DataFrame([{
                'technology_encoded': tech_encoded,
                'capacity_normalized': capacity_norm,
                'capacity_band_encoded': band_encoded,
                'Month': request.month,
                'quarter': (request.month-1)//3 + 1,
                'month_sin': np.sin(2 * np.pi * request.month / 12),
                'month_cos': np.cos(2 * np.pi * request.month / 12),
                'is_summer': 1 if request.month in [4,5,6] else 0,
                'is_monsoon': 1 if request.month in [7,8,9] else 0,
                'is_winter': 1 if request.month in [11,12,1,2] else 0,
                'avg_plf_tech_month': avg_tech,
                'avg_plf_band_month': avg_band,
            }])
            
            raw_plf = base_model.predict(features)[0]
            predicted_plf = np.clip(raw_plf, 0.30, 1.0)
            
            if technology == 'Ultra Supercritical':
                heat_rate = 2500
                gcv = 6500
                coal_grade = 'G3'
            elif technology == 'Supercritical':
                heat_rate = 2700
                gcv = 6000
                coal_grade = 'G6'
            else:
                heat_rate = 2850
                gcv = 5000
                coal_grade = 'G9'
            
            aux_consumption = 8.0
            plant_name = f"New {technology} Plant ({capacity} MW)"
            
        else:
            plant_data = df_reference[df_reference['plant_key'] == request.plant_key]
            if len(plant_data) == 0:
                return JSONResponse(status_code=404, content={"error": "Plant not found"})
            
            latest = plant_data.iloc[-1]
            capacity = latest['Capacity']
            technology = latest['Technology']
            heat_rate = latest.get('Actual SHR', 2750)
            gcv = latest['Estimated_GCV_kcal_per_kg']
            coal_grade = latest['Coal_Grade']
            aux_consumption = latest.get('Auxiliary consumption (%)', 8.0)
            plant_name = latest.get('Name of TPS', request.plant_key)
            
            capacity_norm = (capacity - metadata['capacity_stats']['mean']) / metadata['capacity_stats']['std']
            
            if capacity < 500:
                band = 'Small'
            elif capacity < 1500:
                band = 'Medium'
            else:
                band = 'Large'
            
            tech_encoded = metadata['tech_map'].get(technology, 0)
            band_encoded = metadata['band_map'][band]
            
            tech_month_avg = pd.DataFrame(metadata['tech_month_avg'])
            band_month_avg = pd.DataFrame(metadata['band_month_avg'])
            
            avg_tech = tech_month_avg[(tech_month_avg['Technology'] == technology) & 
                                      (tech_month_avg['Month'] == request.month)]['avg_plf_tech_month'].values[0]
            avg_band = band_month_avg[(band_month_avg['capacity_band'] == band) & 
                                      (band_month_avg['Month'] == request.month)]['avg_plf_band_month'].values[0]
            
            features = pd.DataFrame([{
                'technology_encoded': tech_encoded,
                'capacity_normalized': capacity_norm,
                'capacity_band_encoded': band_encoded,
                'Month': request.month,
                'quarter': (request.month-1)//3 + 1,
                'month_sin': np.sin(2 * np.pi * request.month / 12),
                'month_cos': np.cos(2 * np.pi * request.month / 12),
                'is_summer': 1 if request.month in [4,5,6] else 0,
                'is_monsoon': 1 if request.month in [7,8,9] else 0,
                'is_winter': 1 if request.month in [11,12,1,2] else 0,
                'avg_plf_tech_month': avg_tech,
                'avg_plf_band_month': avg_band,
            }])
            
            predicted_plf = np.clip(base_model.predict(features)[0], 0, 1)
        
        electricity_kwh = calculate_electricity_generation(capacity, predicted_plf, request.year, request.month)
        coal_required = calculate_coal_requirement(electricity_kwh, heat_rate, gcv, aux_consumption)
        
        return {
            'plant_name': plant_name,
            'capacity_mw': float(capacity),
            'plf_percentage': float(predicted_plf * 100),
            'electricity_mwh': float(electricity_kwh / 1000),
            'coal_required_tonnes': float(coal_required),
            'coal_grade': coal_grade,
            'gcv_kcal_kg': float(gcv),
        }
        
    except Exception as e:
        return JSONResponse(status_code=400, content={"error": str(e)})

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)

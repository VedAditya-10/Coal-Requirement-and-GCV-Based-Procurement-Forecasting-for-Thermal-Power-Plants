# Coal Demand Forecasting System

Hybrid ML + Physics system for predicting coal requirements at thermal power plants.

## Features

- **ML Component**: Predicts Plant Load Factor (PLF) using LightGBM with <10% RMSE
- **Physics Component**: Calculates coal requirements using thermodynamic energy balance equations
- **Dual Mode**: Supports both existing plants (historical data) and new plants (capacity-based predictions)
- **Web Interface**: Clean, minimal dark-themed UI for easy predictions
- **Health Monitoring**: Built-in health check endpoint for deployment platforms

## Quick Start (Local Development)

1. **Install dependencies**:
```bash
pip install -r requirements.txt
```

2. **Run the web interface**:
```bash
python app.py
```

3. **Open browser**: http://localhost:8000

## Deployment to Render (Recommended)

### Why Render?
✅ **Best for this app** - Supports large model files (>100MB)  
✅ Free tier with persistent storage  
✅ Automatic HTTPS and custom domains  
✅ Zero configuration needed  

### Deployment Steps

1. **Push code to GitHub** (if not already done):
```bash
git init
git add .
git commit -m "Initial commit"
git branch -M main
git remote add origin <your-repo-url>
git push -u origin main
```

2. **Deploy on Render**:
   - Go to [render.com](https://render.com) and sign up/login
   - Click **"New +"** → **"Web Service"**
   - Connect your GitHub repository
   - Configure:
     - **Name**: `coal-demand-forecasting`
     - **Environment**: `Python 3`
     - **Build Command**: `pip install -r requirements.txt`
     - **Start Command**: `uvicorn app:app --host 0.0.0.0 --port $PORT`
     - **Plan**: Free
   - Click **"Create Web Service"**

3. **Wait for deployment** (5-10 minutes for first deploy due to model files)

4. **Access your app** at: `https://coal-demand-forecasting-xxxx.onrender.com`

### Environment Variables (Optional)

In Render dashboard, add these environment variables:
- `ALLOWED_ORIGINS`: Comma-separated list of allowed origins (default: `*`)
- `PORT`: Automatically set by Render

## API Endpoints

### `GET /health`
Health check endpoint for monitoring
```json
{
  "status": "healthy",
  "service": "coal-demand-forecasting",
  "models_loaded": true,
  "plants_available": 123
}
```

### `GET /plants`
Returns list of available existing plants

### `POST /forecast`
Predict coal demand for a plant

**Request Body (Existing Plant)**:
```json
{
  "is_new_plant": false,
  "plant_key": "PLANT_NAME",
  "year": 2026,
  "month": 6
}
```

**Request Body (New Plant)**:
```json
{
  "is_new_plant": true,
  "capacity": 1000,
  "technology": "Supercritical",
  "year": 2026,
  "month": 6
}
```

**Response**:
```json
{
  "plant_name": "Example Plant",
  "capacity_mw": 1000,
  "plf_percentage": 75.5,
  "electricity_mwh": 543600,
  "coal_required_tonnes": 245000,
  "coal_grade": "G6",
  "gcv_kcal_kg": 6000
}
```

## Model Performance

- **Test RMSE**: < 0.10 (10% error on PLF prediction)
- **Features**: Seasonality, plant characteristics, technology type, capacity bands
- **Training Data**: Historical data from 100+ thermal power plants

## Project Structure

```
├── app.py                              # FastAPI web application
├── static/
│   ├── index.html                      # Frontend UI
│   ├── script.js                       # Frontend logic
│   └── style.css                       # Styling
├── plf_base_model.txt                  # LightGBM model for new plants
├── plf_enhanced_model.txt              # LightGBM model for existing plants
├── plf_prediction_model.txt            # LightGBM prediction model
├── generalized_model_metadata.pkl      # Model metadata and encodings
├── requirements.txt                    # Python dependencies
└── README.md                           # This file
```

## Troubleshooting

**Issue**: Models not loading  
**Solution**: Ensure all `.txt` and `.pkl` files are in the project root

**Issue**: CORS errors  
**Solution**: Set `ALLOWED_ORIGINS` environment variable to your frontend domain

**Issue**: Port already in use  
**Solution**: Change port with `PORT=8001 python app.py`

## Technology Stack

- **Backend**: FastAPI, Python 3.11+
- **ML**: LightGBM, scikit-learn, pandas, numpy
- **Frontend**: Vanilla JavaScript, HTML5, CSS3
- **Deployment**: Render (recommended) or any Python hosting platform

---

## Project Overview

This project focuses on building a data-driven coal demand forecasting model for thermal power plants. Coal is a critical input for power generation, and inaccurate demand estimation can lead to production disruptions or excess inventory costs.

### Problem Statement
Power plants rely heavily on uninterrupted coal supply. Coal demand fluctuates due to changes in power generation, plant efficiency, fuel quality, and operational conditions. Manual or heuristic-based planning often fails to capture these dynamics, leading to inefficiencies. This project aims to provide a reliable forecasting framework to support better inventory and production planning.

### Data Description
The model uses cleaned and merged datasets including:
- Plant-wise and time-series coal consumption
- Power generation and capacity-related features
- Fuel quality parameters such as Gross Calorific Value (GCV)
- Normalized plant identifiers to enable consistent data merging

Special care is taken to handle inconsistent plant naming and heterogeneous data sources.

### Data Source 

This dataset contains plant-level monthly coal data for **Indian thermal power plants**, compiled and standardised from 22 official monthly reports spanning January 2024 to October 2025.

The raw data was sourced from the [National Power Portal (NPP)](https://npp.gov.in/dgrReports), the Government of India's official platform for power sector statistics.

While the original reports are publicly available, they are released as complex, semi-structured Excel files with multi-row headers, regional groupings, embedded totals, and summary tables, making direct analysis difficult. This dataset transforms those raw files into a single, clean, analysis-ready time-series dataset at the individual power plant level.

## License

MIT License - Feel free to use for your projects!

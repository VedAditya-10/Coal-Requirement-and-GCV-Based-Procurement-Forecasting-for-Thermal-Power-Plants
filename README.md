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
├── generalized_model_metadata.pkl      # Model metadata and encodings
├── FINAL_MERGED_DATA.csv               # Reference data for existing plants
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

## License

MIT License - Feel free to use for your projects!


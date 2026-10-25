from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd
from sklearn.ensemble import IsolationForest

app = FastAPI(title="PipeWatch Triage API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory storage for the MVP
telemetry_data = []
active_alerts = []

# Initialize ML Model
model = IsolationForest(contamination=0.1, random_state=42)

@app.post("/api/telemetry")
async def ingest_telemetry(request: Request):
    global telemetry_data, active_alerts
    data = await request.json()
    
    telemetry_data.append(data)
    if len(telemetry_data) > 100:
        telemetry_data.pop(0)
        
    # Run ML model on rolling window
    if len(telemetry_data) > 10:
        df = pd.DataFrame(telemetry_data)
        features = df[['flow_rate', 'pressure']]
        
        model.fit(features.values)
        predictions = model.predict(features.values)
        
        # Evaluate the newest incoming data point
        if predictions[-1] == -1: 
            active_alerts = [{
                "block_id": data.get('block_id', 'Marshalltown-A'),
                "flow_rate": round(float(data.get('flow_rate', 0)), 2),
                "pressure": round(float(data.get('pressure', 0)), 2),
                "asset_risk": "CRITICAL DEGRADATION"
            }]
        else:
            active_alerts = []
            
    return {"status": "success"}

@app.get("/api/triage")
async def get_triage_data():
    return {"alerts": active_alerts}

# Explicitly serve the HTML dashboard on the root URL
@app.get("/")
async def serve_dashboard():
    return FileResponse("static/index.html")

# Mount the static directory for any additional assets
app.mount("/", StaticFiles(directory="static", html=True), name="static")
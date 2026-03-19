import os
from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from google import genai

# Initialize the FastAPI app
app = FastAPI(title="Baranaja AI & Live Tracking Backend")

# Setup CORS to allow your HTML/JS frontend to communicate with this backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize the Gemini Client securely using environment variables
# Ensure you have added GEMINI_API_KEY in your Render environment variables
api_key = os.environ.get("AIzaSyDtR5bheAVr4uCogM9em_fbx4Gb-nXb868")
client = genai.Client(api_key=api_key)

# Define the expected data structure for the REST API
class FarmLocation(BaseModel):
    latitude: float
    longitude: float

# --- 1. REST API ENDPOINT: Gemini LLM Crop Prediction ---
@app.post("/api/predict-yield")
async def predict_yield(location: FarmLocation):
    try:
        # Mock environmental data for the hackathon prototype
        mock_elevation = 1200 
        
        # Create a prompt for Gemini instructing it to act as an agronomist
        prompt = f"""
        Act as an expert agronomist in Uttarakhand. 
        A farmer's land is located at latitude {location.latitude} and longitude {location.longitude} 
        with an elevation of {mock_elevation} meters. 
        Based on this mountainous terrain, suggest the best traditional Baranaja crops to plant 
        and give a short weather resilience tip. Keep it concise.
        """
        
        # Call the Gemini API to generate the content
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt
        )
        
        return {
            "status": "success",
            "coordinates": {"lat": location.latitude, "lon": location.longitude},
            "elevation_meters": mock_elevation,
            "ai_recommendation": response.text,
            "message": "Successfully generated insights with Gemini!"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# --- 2. WEBSOCKET ENDPOINT: Live Location Tracking ---
@app.websocket("/ws/live-location")
async def live_location_tracker(websocket: WebSocket):
    # Accept the incoming WebSocket connection from the frontend
    await websocket.accept()
    try:
        while True:
            # Wait for a message (GPS coordinates) from the client
            data = await websocket.receive_json()
            lat = data.get("latitude")
            lon = data.get("longitude")
            
            print(f"Farmer live location received: Lat {lat}, Lon {lon}")
            
            # You can trigger real-time ML analysis or alerts here in the future
            
            # Send a continuous confirmation back to the frontend
            await websocket.send_json({
                "status": "Tracking active", 
                "message": f"Location {lat}, {lon} synced successfully."
            })
            
    except WebSocketDisconnect:
        # Handle the event when the farmer closes the app or loses connection
        print("Farmer disconnected from live tracking.")

# --- 3. HEALTH CHECK ENDPOINT ---
@app.get("/")
def read_root():
    return {"message": "Baranaja AI API with Gemini and WebSockets is up and running!"}
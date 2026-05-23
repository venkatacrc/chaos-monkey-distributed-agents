import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
import uvicorn

# Load .env file manually if it exists
if os.path.exists(".env"):
    with open(".env") as f:
        for line in f:
            if line.strip() and not line.startswith("#"):
                try:
                    key, val = line.strip().split("=", 1)
                    os.environ[key.strip()] = val.strip().strip('"').strip("'")
                except ValueError:
                    pass

# Import target agent simulation
try:
    import target_agent
except ImportError:
    # Handle import if running from subdirectories, but typically it will be in the same folder
    import sys
    sys.path.append(os.path.dirname(os.path.abspath(__file__)))
    import target_agent

app = FastAPI(title="Chaos Engineering for Agentic Infrastructure API")

# Enable CORS for local development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class SimulationRequest(BaseModel):
    user_prompt: str
    use_chaos: bool = False
    use_defense: bool = False
    chaos_type: str = "type_coercion"
    custom_chaos_prompt: str = ""

@app.get("/api/health")
def health_check():
    return {
        "status": "healthy",
        "api_key_configured": bool(os.environ.get("GEMINI_API_KEY"))
    }

@app.post("/api/simulate")
def run_api_simulation(request: SimulationRequest):
    # Ensure GEMINI_API_KEY is configured
    if not os.environ.get("GEMINI_API_KEY"):
        raise HTTPException(
            status_code=500,
            detail="GEMINI_API_KEY is not configured in the backend environment. Please set it in a .env file or environment variables."
        )
    try:
        result = target_agent.run_simulation(
            user_prompt=request.user_prompt,
            use_chaos=request.use_chaos,
            use_defense=request.use_defense,
            chaos_type=request.chaos_type,
            custom_chaos_prompt=request.custom_chaos_prompt
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Mount static files directory
# We check and serve static files
static_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "static")
if os.path.exists(static_dir):
    app.mount("/", StaticFiles(directory=static_dir, html=True), name="static")
else:
    @app.get("/")
    def read_root():
        return HTMLResponse("<h1>Chaos Monkey Web App Dashboard</h1><p>Static files directory 'static' not found.</p>")

if __name__ == "__main__":
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)

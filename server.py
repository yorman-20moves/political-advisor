# File: server.py
# Directory: POLITICAL_ADVISOR/

import asyncio
import logging
from fastapi import FastAPI, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from models.state import SharedState
from config.config import Config
from agents.router_agent import router_agent

# Configure logging
logging.basicConfig(
    filename='app.log',
    level=logging.DEBUG,
    format='%(asctime)s %(levelname)s:%(name)s:%(message)s',
)
logger = logging.getLogger(__name__)

app = FastAPI()

# Allow CORS (adjust origins as needed)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust this in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global state and config
config = Config()
state = SharedState()
state.config = config  # Pass config to state

class SearchRequest(BaseModel):
    user_query: str

@app.post("/api/start_search")
async def start_search(request: SearchRequest, background_tasks: BackgroundTasks):
    try:
        # Reset the state
        state.reset()
        state.user_query = request.user_query
        state.add_log(f"Received search request: {request.user_query}", level="INFO")

        # Start the workflow in the background
        background_tasks.add_task(run_workflow)
        return {"message": "Search initiated successfully."}
    except Exception as e:
        logger.error(f"Error in start_search: {e}")
        return {"message": "Failed to initiate search.", "error": str(e)}

async def run_workflow():
    try:
        while True:
            await router_agent(state)
            if state.next_step == "end":
                state.add_log("Workflow complete", level="INFO")
                break
    except Exception as e:
        state.add_log(f"Error in run_workflow: {e}", level="ERROR")
        logger.error(f"Error in run_workflow: {e}")

@app.get("/api/job_status")
def get_job_status():
    # Return the current state status
    return {
        "next_step": state.next_step,
        "upload_complete": state.upload_complete,
    }

@app.get("/api/logs")
def get_logs():
    return {"logs": state.logs}

@app.get("/api/config")
def get_config():
    # Exclude sensitive information like API keys
    config_data = {
        "NEO4J_URI": config.NEO4J_URI,
        "NEO4J_USER": config.NEO4J_USER,
        # Exclude NEO4J_PASSWORD and API keys
        "USER_AGENT": config.USER_AGENT,
        "LLM_MODEL_NAME": config.LLM_MODEL_NAME,
        "LLM_MAX_TOKENS": config.LLM_MAX_TOKENS,
        "LLM_TEMPERATURE": config.LLM_TEMPERATURE,
        # Include other non-sensitive config parameters as needed
    }
    return {"config": config_data}

# To run the app using Uvicorn:
# if __name__ == "__main__":
#     import uvicorn
#     uvicorn.run("server:app", host="0.0.0.0", port=8000, reload=True)

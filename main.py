# File: main.py
# Directory: my_app/

# Overall Role and Purpose:
# - Acts as the entry point for the backend application.
# - Initializes the configuration and shared state.
# - Starts the API server (via `server.py`) for front-end communication.

# Expected Inputs:
# - None directly from the user.
# - Loads configuration from `config/config.py`.

# Expected Outputs:
# - Starts the application and makes the API endpoints available.
# - Initializes the logging and state management.

import asyncio
from agents.router_agent import router_agent
from models.state import SharedState
from config.config import Config

async def main():
    config = Config()
    state = SharedState(search_terms=["artificial intelligence", "machine learning"])
    state.config = config  # Pass config to state

    while True:
        await router_agent(state)
        if state.next_step == "end":
            print("Workflow complete")
            break

if __name__ == "__main__":
    asyncio.run(main())

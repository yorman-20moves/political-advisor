# File: knowledge_graph_uploader_agent.py
# Directory: my_app/agents/

# Overall Role and Purpose:
# - Uploads the validated data to the knowledge graph database (e.g., Neo4j).

# Expected Inputs:
# - `SharedState` with `reviewed_data`.
# - `Config` with database connection details.

# Expected Outputs:
# - Data is inserted into the knowledge graph.
# - Sets `upload_complete` to `True` in the state upon successful upload.

from models.state import SharedState
from tools.database import KnowledgeGraphUploader

async def knowledge_graph_uploader_agent(state: SharedState):
    state.add_log("Starting knowledge graph upload.")
    uploader = KnowledgeGraphUploader(
        uri=state.config.NEO4J_URI,
        user=state.config.NEO4J_USER,
        password=state.config.NEO4J_PASSWORD,
    )
    for url, data in state.reviewed_data.items():
        await uploader.upload_data(data)
    state.upload_complete = True
    state.add_log("Knowledge graph upload complete.")

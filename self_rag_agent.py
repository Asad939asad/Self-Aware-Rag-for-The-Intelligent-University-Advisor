from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import List, Optional
import uvicorn
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

from graph import app as langgraph_app

class MemoryItem(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    query: str
    window_memory: List[MemoryItem] = []

class CheckpointData(BaseModel):
    checkpoint: int
    label: str
    status: str
    detail: str
    reasoning: Optional[str] = None
    docs_graded: Optional[int] = None
    docs_relevant: Optional[int] = None
    web_search_triggered: Optional[bool] = False
    retries_used: Optional[int] = 0

class ChatResponse(BaseModel):
    answer: str
    path: str
    trace: List[CheckpointData]
    used_web_search: bool
    retry_count: int

app_api = FastAPI(title="XYZ University Advisory Agent API")

app_api.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app_api.post("/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    try:
        # Build initial state including window memory as context
        memory_context = ""
        if request.window_memory:
            memory_context = "\n\nRecent conversation context:\n"
            for item in request.window_memory:
                role_label = "Student" if item.role == "user" else "Advisor"
                memory_context += f"{role_label}: {item.content}\n"
        
        initial_state = {
            "query": request.query,
            "memory_context": memory_context,
            "needs_retrieval": False,
            "retrieval_reasoning": "",
            "retrieved_docs": [],
            "relevant_docs": [],
            "use_web_search": False,
            "web_results": [],
            "generation_context": "",
            "response": "",
            "hallucination_detected": False,
            "retry_count": 0,
            "final_answer": "",
            "trace_steps": [],
            "agent_path": ""
        }
        
        final_state = await langgraph_app.ainvoke(initial_state)
        
        # Build trace from final_state
        trace = final_state.get("trace_steps", [])
        
        return ChatResponse(
            answer=final_state.get("final_answer", "No answer generated."),
            path=final_state.get("agent_path", "unknown"),
            trace=trace,
            used_web_search=final_state.get("use_web_search", False),
            retry_count=final_state.get("retry_count", 0)
        )
    except Exception as e:
        print(f"Error in chat endpoint: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app_api.get("/health")
async def health():
    return {"status": "online", "agent": "XYZ University Advisory Agent"}

# --- SILENCE EXTERNAL NOISE ---
# These endpoints are added to stop 404 logs from external dashboards (VPTQ)
@app_api.get("/api/pipeline/status")
@app_api.get("/api/stats/pipeline-status")
async def pipeline_status():
    return {"status": "idle", "message": "University Advisor Active"}

@app_api.post("/api/stats/run-pipeline")
async def run_pipeline():
    return {"status": "skipped", "message": "Pipeline logic not applicable to RAG Agent"}

# Serve Frontend - This MUST be at the end
# We assume the built frontend is in a directory named 'static'
if os.path.exists("static"):
    app_api.mount("/", StaticFiles(directory="static", html=True), name="static")

    @app_api.get("/{full_path:path}")
    async def serve_frontend(full_path: str):
        # Fallback for SPA routing
        return FileResponse("static/index.html")

if __name__ == "__main__":
    uvicorn.run("self_rag_agent:app_api", host="0.0.0.0", port=7860, reload=False)

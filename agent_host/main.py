from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from contextlib import asynccontextmanager
import os
from dotenv import load_dotenv
from agent_host.orchestrator import AIAgentOrchestrator
from shared.logging_config import setup_logging, get_logger
from shared.config import settings
from shared.exceptions import MCPException
import time

# Setup logging
setup_logging()
logger = get_logger(__name__)

# Load environment variables
load_dotenv()

# Global orchestrator instance
orchestrator = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifecycle"""
    global orchestrator
    
    logger.info("Starting Agent Host application")
    
    openai_api_key = settings.OPENAI_API_KEY or os.getenv("OPENAI_API_KEY")
    if not openai_api_key:
        logger.error("OPENAI_API_KEY environment variable is required")
        raise RuntimeError("OPENAI_API_KEY environment variable is required")
    
    try:
        orchestrator = AIAgentOrchestrator(openai_api_key)
        results = await orchestrator.initialize_servers()
        
        logger.info("Agent Host initialized successfully", 
                   initialization_results=results)
        
        yield
        
        logger.info("Shutting down Agent Host application")
        
    except Exception as e:
        logger.error("Failed to initialize Agent Host", error=str(e))
        raise

app = FastAPI(
    title="AI Agent Host",
    description="Production-ready orchestrator for MCP servers",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request/Response models
class QueryRequest(BaseModel):
    query: str
    max_iterations: int = 10

class QueryResponse(BaseModel):
    request_id: str
    response: str
    success: bool
    metadata: dict

# Middleware for request logging
@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    
    logger.info("Incoming request",
               method=request.method,
               url=str(request.url),
               client=request.client.host if request.client else None)
    
    try:
        response = await call_next(request)
        
        process_time = time.time() - start_time
        logger.info("Request completed",
                   method=request.method,
                   url=str(request.url),
                   status_code=response.status_code,
                   process_time_seconds=process_time)
        
        return response
        
    except Exception as e:
        process_time = time.time() - start_time
        logger.error("Request failed",
                    method=request.method,
                    url=str(request.url),
                    error=str(e),
                    process_time_seconds=process_time)
        raise

# Exception handler for MCP exceptions
@app.exception_handler(MCPException)
async def mcp_exception_handler(request: Request, exc: MCPException):
    logger.error("MCP exception occurred",
                url=str(request.url),
                error=exc.message,
                details=exc.details)
    
    return JSONResponse(
        status_code=500,
        content={
            "error": exc.message,
            "details": exc.details,
            "type": exc.__class__.__name__
        }
    )

@app.post("/query", response_model=QueryResponse)
async def process_query(request: QueryRequest):
    """Process a user query using the AI agent orchestrator"""
    if not orchestrator:
        raise HTTPException(503, "Orchestrator not initialized")
    
    try:
        result = await orchestrator.process_query(
            request.query,
            max_iterations=request.max_iterations
        )
        return QueryResponse(**result)
        
    except Exception as e:
        logger.error("Query processing failed", error=str(e))
        raise HTTPException(500, f"Query processing failed: {str(e)}")

@app.get("/status")
async def get_status():
    """Get comprehensive system status"""
    if not orchestrator:
        return {
            "status": "not_initialized",
            "message": "Orchestrator not initialized"
        }
    
    try:
        status = await orchestrator.get_system_status()
        return status
    except Exception as e:
        logger.error("Failed to get system status", error=str(e))
        raise HTTPException(500, f"Failed to get status: {str(e)}")

@app.get("/tools")
async def get_available_tools():
    """Get all available tools across MCP servers"""
    if not orchestrator:
        return {"tools": [], "message": "Orchestrator not initialized"}
    
    try:
        tools = orchestrator.mcp_manager.get_tools_for_llm()
        return {
            "tools": tools,
            "total_count": len(tools)
        }
    except Exception as e:
        logger.error("Failed to get tools", error=str(e))
        raise HTTPException(500, f"Failed to get tools: {str(e)}")

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    if not orchestrator or not orchestrator.initialized:
        return JSONResponse(
            status_code=503,
            content={"status": "unhealthy", "reason": "not_initialized"}
        )
    
    try:
        health_status = await orchestrator.mcp_manager.health_check_all()
        all_healthy = all(health_status.values())
        
        return {
            "status": "healthy" if all_healthy else "degraded",
            "servers": health_status
        }
    except Exception as e:
        logger.error("Health check failed", error=str(e))
        return JSONResponse(
            status_code=503,
            content={"status": "unhealthy", "error": str(e)}
        )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=settings.AGENT_HOST_PORT,
        log_config=None  # Use our custom logging
    )





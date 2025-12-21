from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import httpx
import os
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="GAVEL Backend Gateway")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configuration for agent services (internal Docker hostnames/ports)
# These defaults assume the service names in docker-compose.yaml
AGENT_URLS = {
    "summarizer": os.getenv("SUMMARIZER_URL", "http://summarizer:8010"),
    "forgery": os.getenv("FORGERY_URL", "http://forgery-checker:8011"),
    "precedent": os.getenv("PRECEDENT_URL", "http://precedent-searcher:8012"),
    "draft": os.getenv("DRAFT_URL", "http://draft-helper:8013"),
}

@app.get("/")
async def root():
    return {"message": "GAVEL Backend Gateway is running", "agents": list(AGENT_URLS.keys())}

@app.get("/health")
async def health():
    return {"status": "healthy"}

async def proxy_request(service_name: str, path: str, request: Request):
    if service_name not in AGENT_URLS:
        raise HTTPException(status_code=404, detail=f"Service {service_name} not found")
    
    base_url = AGENT_URLS[service_name]
    url = f"{base_url}/{path}"
    
    async with httpx.AsyncClient() as client:
        try:
            # Reconstruct the request for the target service
            method = request.method
            headers = dict(request.headers)
            # Remove host header to let httpx handle it
            headers.pop("host", None)
            
            body = await request.body()
            
            response = await client.request(
                method,
                url,
                headers=headers,
                content=body,
                params=request.query_params,
                timeout=60.0
            )
            
            # Check if response is successful before trying to parse JSON
            if response.is_error:
                 raise HTTPException(status_code=response.status_code, detail=response.text)
                 
            return response.json()
        except httpx.RequestError as e:
            raise HTTPException(status_code=502, detail=f"Error communicating with agent {service_name}: {str(e)}")
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

@app.post("/summarize")
async def summarize(request: Request):
    return await proxy_request("summarizer", "summarize", request)

@app.post("/verify")
async def verify(request: Request):
    return await proxy_request("forgery", "verify", request)

@app.post("/search")
async def search(request: Request):
    return await proxy_request("precedent", "search", request)

@app.post("/draft")
async def draft(request: Request):
    return await proxy_request("draft", "draft", request)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

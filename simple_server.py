
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

app = FastAPI(title="Korean Stock Backtesting API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "Korean Stock Backtesting API", "status": "running"}

@app.get("/health")
async def health():
    return {"status": "healthy"}

@app.get("/api/v1/stocks")
async def get_stocks():
    return [
        {"symbol": "005930", "name": "Samsung Electronics", "market": "KOSPI"},
        {"symbol": "000660", "name": "SK Hynix", "market": "KOSPI"},
        {"symbol": "035420", "name": "NAVER", "market": "KOSPI"}
    ]

if __name__ == "__main__":
    print("Starting Korean Stock Backtesting API...")
    print("API Docs: http://localhost:8000/docs")
    print("Press Ctrl+C to stop")
    
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)

from backend.main import app

if __name__ == "__main__":
    import uvicorn
    # The root main.py runs the gateway app from the backend package
    uvicorn.run(app, host="0.0.0.0", port=8080)

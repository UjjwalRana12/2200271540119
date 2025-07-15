import datetime
import os
import uuid
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from logger import FileLogger

app = FastAPI()
LOG = FileLogger()

@app.post("/log")
async def create_log(request: Request):
    try:
        data = await request.json()
        stack = data.get("stack")
        level = data.get("level")
        package = data.get("package")
        message = data.get("message")

        
        LOG.log(stack, level, package, message)

        
        log_id = str(uuid.uuid4())
        return JSONResponse(content={
            "logID": log_id,
            "message": "log created successfully"
        }, status_code=200)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="An unexpected error occurred")

@app.get("/log")
async def get_logs():
    try:
        if not os.path.exists(LOG.log_file):
            return JSONResponse(content={"logs": []}, status_code=200)

        with open(LOG.log_file, "r") as f:
            logs = f.readlines()
        return JSONResponse(content={"logs": logs}, status_code=200)
    except Exception as e:
        raise HTTPException(status_code=500, detail="An unexpected error occurred")
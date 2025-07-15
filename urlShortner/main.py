import datetime
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel, HttpUrl, constr
from loggingMiddleware.logger import FileLogger

app = FastAPI()
LOG = FileLogger()


url_store = {}


class ShortenRequest(BaseModel):
    original_url: HttpUrl 
    suffix: str  
    validate_time: int = 30  


class ShortenResponse(BaseModel):
    short_url: HttpUrl
    expiration_time: datetime.datetime

@app.post("/shorten", response_model=ShortenResponse)
async def create_short_url(request: ShortenRequest):
    try:
        
        if not request.suffix.isalnum():
            raise HTTPException(status_code=400, detail="Suffix must be alphanumeric")

        
        validate_time_seconds = request.validate_time * 60

        
        short_url = f"{request.original_url}/{request.suffix}"

        
        expiration_time = datetime.datetime.now() + datetime.timedelta(seconds=validate_time_seconds)
        url_store[short_url] = {
            "original_url": request.original_url,
            "short_url": short_url,
            "expiration_time": expiration_time
        }

        
        LOG.log(
            stack="backend",
            level="info",
            package="handler",
            message=f"Short URL created: {short_url} (expires at {expiration_time})"
        )

        return ShortenResponse(
            short_url=short_url,
            expiration_time=expiration_time
        )
    except Exception as e:
        LOG.log(
            stack="backend",
            level="error",
            package="handler",
            message=f"An unexpected error occurred: {str(e)}"
        )
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {str(e)}")


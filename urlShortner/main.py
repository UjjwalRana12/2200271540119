import datetime
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel, HttpUrl, constr
from loggingMiddleware.logger import FileLogger

app = FastAPI()
LOG = FileLogger()


url_store = {}
click_data = {}

class ShortenRequest(BaseModel):
    original_url: HttpUrl
    suffix: str
    validate_time: int = 30

class ShortenResponse(BaseModel):
    short_url: HttpUrl
    expiration_time: datetime.datetime

class ShortUrlStatistics(BaseModel):
    original_url: HttpUrl
    creation_date: datetime.datetime
    expiration_date: datetime.datetime
    total_clicks: int
    click_details: list[dict]

@app.post("/shorten", response_model=ShortenResponse)
async def create_short_url(request: ShortenRequest):
    try:
        if not request.suffix.isalnum():
            raise HTTPException(status_code=400, detail="Suffix must be alphanumeric")

        validate_time_seconds = request.validate_time * 60
        short_url = f"{request.original_url}/{request.suffix}"
        creation_date = datetime.datetime.now()
        expiration_date = creation_date + datetime.timedelta(seconds=validate_time_seconds)

        url_store[short_url] = {
            "original_url": request.original_url,
            "creation_date": creation_date,
            "expiration_date": expiration_date
        }
        click_data[short_url] = []

        LOG.log(
            stack="backend",
            level="info",
            package="handler",
            message=f"Short URL created: {short_url} (expires at {expiration_date})"
        )

        return ShortenResponse(
            short_url=short_url,
            expiration_time=expiration_date
        )
    except Exception as e:
        LOG.log(
            stack="backend",
            level="error",
            package="handler",
            message=f"An unexpected error occurred: {str(e)}"
        )
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {str(e)}")

@app.get("/shorturls/{shortcode}", response_model=ShortUrlStatistics)
async def get_short_url_statistics(shortcode: str, request: Request):
    try:
        
        short_url = next((url for url in url_store if url.endswith(shortcode)), None)
        if not short_url:
            raise HTTPException(status_code=404, detail="Short URL not found")

        
        url_details = url_store[short_url]
        clicks = click_data.get(short_url, [])

        
        statistics = {
            "original_url": url_details["original_url"],
            "creation_date": url_details["creation_date"],
            "expiration_date": url_details["expiration_date"],
            "total_clicks": len(clicks),
            "click_details": clicks
        }

        LOG.log(
            stack="backend",
            level="info",
            package="handler",
            message=f"Statistics retrieved for short URL: {short_url}"
        )

        return statistics
    except Exception as e:
        LOG.log(
            stack="backend",
            level="error",
            package="handler",
            message=f"An unexpected error occurred while retrieving statistics: {str(e)}"
        )
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {str(e)}")

@app.post("/click/{shortcode}")
async def register_click(shortcode: str, request: Request):
    try:
        
        short_url = next((url for url in url_store if url.endswith(shortcode)), None)
        if not short_url:
            raise HTTPException(status_code=404, detail="Short URL not found")

        
        click_details = {
            "timestamp": datetime.datetime.now(),
            "referrer": request.headers.get("referer", "unknown"),
            "location": "unknown"  
        }
        click_data[short_url].append(click_details)

        LOG.log(
            stack="backend",
            level="info",
            package="handler",
            message=f"Click registered for short URL: {short_url}"
        )

        return {"message": "Click registered successfully"}
    except Exception as e:
        LOG.log(
            stack="backend",
            level="error",
            package="handler",
            message=f"An unexpected error occurred while registering click: {str(e)}"
        )
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {str(e)}")


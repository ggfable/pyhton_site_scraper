from fastapi import FastAPI, Query
from fastapi.logger import logger
from fastapi.responses import JSONResponse
from scraper import get_job_data
import time


app = FastAPI(title="ggfalbe API",
              description="data scraping",
              version="0.0.1",)



@app.exception_handler(Exception)
def validation_exception_handler(request, err):
    base_error_message = f"Failed to execute: {request.method}: {request.url}"
    return JSONResponse(status_code=400, content={"message": f"{base_error_message}. Detail: {err}"})


@app.middleware("http")
async def add_process_time_header(request, call_next):
    print('inside middleware!')
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(f'{process_time:0.4f} sec')
    return response


@app.get("/")
async def index():
    logger.debug("Handling index request")
    return JSONResponse(content={"message": "Api is running"})


@app.get("/api/v1/parser", response_class=JSONResponse)
async def scrape_website_handler(country: str = Query(default=""), job: str = Query(default="")) -> JSONResponse:
    data = await get_job_data(country, job)
    return data
from __future__ import annotations

from collections import defaultdict, deque
from time import monotonic

from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from .cli import build_service
from .config import get_settings
from .gemini_client import GeminiProviderError
from .schemas import HealthResponse, QueryRequest, QueryResponse

settings = get_settings()
service = build_service()
app = FastAPI(
    title="Northside Dental Fictional Demo RAG",
    version="1.1.0",
    description="CLI-first grounded RAG demo with a secondary HTTP endpoint. Fictional demo data only; not for real patient use.",
)
_requests: dict[str, deque[float]] = defaultdict(deque)


@app.middleware("http")
async def rate_limit(request: Request, call_next):
    if request.url.path == "/api/v1/query":
        key = request.client.host if request.client else "unknown"
        now = monotonic()
        bucket = _requests[key]
        while bucket and now - bucket[0] > 60:
            bucket.popleft()
        if len(bucket) >= settings.rate_limit_per_minute:
            return JSONResponse(status_code=429, content={"detail": "rate limit exceeded"})
        bucket.append(now)
    return await call_next(request)


@app.exception_handler(RequestValidationError)
async def validation_error(_: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=422,
        content={"detail": "invalid request: query must be a non-empty string of at most 2000 characters"},
    )


@app.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    return HealthResponse(
        status="ok",
        service="northside-dental-rag",
        knowledge_base_chunks=len(service.kb.chunks),
        gemini_configured=bool(settings.gemini_api_key),
    )


@app.post("/api/v1/query", response_model=QueryResponse)
def query(request: QueryRequest) -> QueryResponse:
    try:
        return service.answer(request.query)
    except GeminiProviderError as exc:
        status_code = 429 if exc.status_code == 429 else 503
        raise HTTPException(status_code=status_code, detail=str(exc)) from exc
    except RuntimeError as exc:
        message = str(exc)
        if "GEMINI_API_KEY" in message:
            raise HTTPException(status_code=503, detail="Gemini is not configured; set GEMINI_API_KEY in the server environment") from exc
        raise HTTPException(status_code=503, detail="The answer service is temporarily unavailable") from exc
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
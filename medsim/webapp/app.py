"""FastAPI application exposing a lightweight interactive patient simulator."""

from __future__ import annotations

from pathlib import Path
from typing import Dict

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from .session import SessionManager


BASE_DIR = Path(__file__).resolve().parent
STATIC_DIR = BASE_DIR / "static"


app = FastAPI(title="MedAgentSim Interactive Agent", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

_session_manager = SessionManager()


class MessageRequest(BaseModel):
    session_id: str = Field(..., description="Active session identifier")
    message: str = Field(..., min_length=1, description="Doctor message for the patient")


class SessionResponse(BaseModel):
    session_id: str
    session: Dict[str, object]


@app.get("/", response_class=FileResponse)
async def index() -> FileResponse:
    """Serve the single-page application."""

    return FileResponse(STATIC_DIR / "index.html")


@app.post("/api/session", response_model=SessionResponse)
async def create_session() -> SessionResponse:
    session = _session_manager.create_session()
    return SessionResponse(session_id=session.session_id, session=session.to_dict())


@app.post("/api/message")
async def send_message(request: MessageRequest) -> Dict[str, object]:
    try:
        reply, state = _session_manager.handle_message(request.session_id, request.message)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc

    return {"reply": reply, "session": state}


class RevealRequest(BaseModel):
    session_id: str


@app.post("/api/reveal")
async def reveal_diagnosis(request: RevealRequest) -> Dict[str, str]:
    try:
        diagnosis = _session_manager.reveal(request.session_id)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc

    return {"diagnosis": diagnosis}


if __name__ == "__main__":  # pragma: no cover - convenience entrypoint
    import uvicorn

    uvicorn.run("medsim.webapp.app:app", host="0.0.0.0", port=8000, reload=False)

from __future__ import annotations

import json
from pathlib import Path
from typing import Generator, List, Optional

from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from .db import Base, SessionLocal, engine, ensure_data_dir, BASE_DIR
from .models import Idea


ensure_data_dir()
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Museo de Ideas", version="1.0.0")

# CORS abierto para desarrollo; en producción especifica orígenes.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


class IdeaIn(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    description: str = Field(..., min_length=1)
    tags: List[str] = Field(default_factory=list)


class IdeaOut(BaseModel):
    id: int
    title: str
    description: str
    tags: List[str]
    likes: int
    created_at: Optional[str]

    @staticmethod
    def from_model(m: Idea) -> "IdeaOut":
        try:
            tags = json.loads(m.tags_json or "[]")
        except json.JSONDecodeError:
            tags = []
        return IdeaOut(
            id=m.id,
            title=m.title,
            description=m.description,
            tags=tags,
            likes=m.likes,
            created_at=str(m.created_at) if m.created_at else None,
        )


@app.get("/api/health")
def health() -> dict:
    return {"status": "ok"}


@app.get("/api/ideas", response_model=List[IdeaOut])
def list_ideas(db: Session = Depends(get_db)):
    ideas = db.query(Idea).order_by(Idea.id.desc()).all()
    return [IdeaOut.from_model(i) for i in ideas]


@app.post("/api/ideas", status_code=status.HTTP_201_CREATED, response_model=IdeaOut)
def create_idea(payload: IdeaIn, db: Session = Depends(get_db)):
    idea = Idea(
        title=payload.title.strip(),
        description=payload.description.strip(),
        tags_json=json.dumps([t.strip() for t in payload.tags if t.strip()]),
        likes=0,
    )
    db.add(idea)
    db.commit()
    db.refresh(idea)
    return IdeaOut.from_model(idea)


@app.post("/api/ideas/{idea_id}/like", response_model=IdeaOut)
def like_idea(idea_id: int, db: Session = Depends(get_db)):
    idea = db.query(Idea).filter(Idea.id == idea_id).first()
    if not idea:
        raise HTTPException(status_code=404, detail="Idea no encontrada")
    idea.likes += 1
    db.commit()
    db.refresh(idea)
    return IdeaOut.from_model(idea)


@app.delete("/api/ideas/{idea_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_idea(idea_id: int, db: Session = Depends(get_db)):
    idea = db.query(Idea).filter(Idea.id == idea_id).first()
    if not idea:
        raise HTTPException(status_code=404, detail="Idea no encontrada")
    db.delete(idea)
    db.commit()
    return None


# Servir frontend estático
STATIC_DIR = BASE_DIR / "frontend"
STATIC_DIR.mkdir(exist_ok=True)
app.mount("/", StaticFiles(directory=str(STATIC_DIR), html=True), name="static")


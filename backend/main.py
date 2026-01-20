from datetime import datetime
import os

from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field
from sqlalchemy import Column, DateTime, Float, Integer, String, create_engine
from sqlalchemy.orm import Session, declarative_base, sessionmaker

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FRONTEND_DIR = os.path.join(BASE_DIR, "..", "frontend")
DB_PATH = os.path.join(BASE_DIR, "metrics.db")
DATABASE_URL = f"sqlite:///{DB_PATH}"

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class Metric(Base):
    __tablename__ = "metrics"

    id = Column(Integer, primary_key=True, index=True)
    url = Column(String(500), nullable=False, index=True)
    run_datetime = Column(DateTime, nullable=True, index=True)
    strategy = Column(String(20), nullable=False, default="mobile")

    score_performance = Column(Integer, nullable=True)
    score_accessibility = Column(Integer, nullable=True)
    score_best_practices = Column(Integer, nullable=True)
    score_seo = Column(Integer, nullable=True)

    fcp_ms = Column(Integer, nullable=True)
    lcp_ms = Column(Integer, nullable=True)
    inp_ms = Column(Integer, nullable=True)
    ttfb_ms = Column(Integer, nullable=True)
    cls = Column(Float, nullable=True)
    speed_index_ms = Column(Integer, nullable=True)
    tbt_ms = Column(Integer, nullable=True)

    total_requests = Column(Integer, nullable=True)
    total_transfer_kb = Column(Integer, nullable=True)

    notes = Column(String(2000), nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)


class MetricCreate(BaseModel):
    url: str
    run_datetime: datetime | None = None
    strategy: str = Field("mobile", pattern="^(mobile|desktop)$")

    score_performance: int | None = Field(None, ge=0, le=100)
    score_accessibility: int | None = Field(None, ge=0, le=100)
    score_best_practices: int | None = Field(None, ge=0, le=100)
    score_seo: int | None = Field(None, ge=0, le=100)

    fcp_ms: int | None = Field(None, ge=0)
    lcp_ms: int | None = Field(None, ge=0)
    inp_ms: int | None = Field(None, ge=0)
    ttfb_ms: int | None = Field(None, ge=0)
    cls: float | None = Field(None, ge=0)
    speed_index_ms: int | None = Field(None, ge=0)
    tbt_ms: int | None = Field(None, ge=0)

    total_requests: int | None = Field(None, ge=0)
    total_transfer_kb: int | None = Field(None, ge=0)

    notes: str | None = None


class MetricOut(MetricCreate):
    id: int
    created_at: datetime

    class Config:
        orm_mode = True


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    os.makedirs(BASE_DIR, exist_ok=True)
    Base.metadata.create_all(bind=engine)


app = FastAPI(title="PageSpeed Metrics Tracker")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def on_startup():
    init_db()


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/metrics", response_model=MetricOut)
def create_metric(payload: MetricCreate, db: Session = Depends(get_db)):
    metric = Metric(**payload.dict())
    db.add(metric)
    db.commit()
    db.refresh(metric)
    return metric


@app.get("/metrics", response_model=list[MetricOut])
def list_metrics(limit: int = 20, db: Session = Depends(get_db)):
    if limit <= 0:
        raise HTTPException(status_code=400, detail="limit must be positive")
    query = db.query(Metric).order_by(Metric.created_at.desc()).limit(limit)
    return list(query)


if os.path.isdir(FRONTEND_DIR):
    app.mount(
        "/", StaticFiles(directory=FRONTEND_DIR, html=True), name="frontend"
    )


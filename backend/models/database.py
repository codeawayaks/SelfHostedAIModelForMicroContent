from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
from backend.config import settings

# Note: Database initialization doesn't require Runpod config, so we can use settings directly

Base = declarative_base()


class Generation(Base):
    __tablename__ = "generations"
    
    id = Column(Integer, primary_key=True, index=True)
    input_type = Column(String, nullable=False)  # "topic" or "prompt"
    input_content = Column(Text, nullable=False)
    hook = Column(Text, nullable=True)
    caption = Column(Text, nullable=True)
    cta = Column(Text, nullable=True)
    final_output = Column(Text, nullable=False)
    cost = Column(Float, nullable=False)
    hook_cost = Column(Float, default=0.00011)
    caption_cost = Column(Float, default=0.00028)
    cta_cost = Column(Float, default=0.00006)
    merge_cost = Column(Float, default=0.00005)
    timestamp = Column(DateTime, default=datetime.utcnow)
    extra_metadata = Column(Text, nullable=True)  # JSON string for additional data


engine = create_engine(settings.database_url, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    """Dependency for getting database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """Initialize database tables"""
    Base.metadata.create_all(bind=engine)


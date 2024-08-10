from sqlalchemy import Column, String, Integer, Boolean, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session

DATABASE_URL = "sqlite:///test.db"

Base = declarative_base()

class Screenshot(Base):
    __tablename__ = 'screenshots'
    id = Column(String, primary_key=True, index=True)
    url = Column(String, index=True)
    type = Column(String)
    file_path = Column(String)
    part = Column(Integer)
    parent_id = Column(String, nullable=True)
    scrapable = Column(Boolean, default=False)

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def create_screenshot(db: Session, screenshot: Screenshot):
    try:
        db.add(screenshot)
        db.commit()
        db.refresh(screenshot)
        return screenshot
    except Exception as e:
        db.rollback()
        raise e

def get_screenshot(db: Session, screenshot_id: str):
    return db.query(Screenshot).filter(Screenshot.parent_id == screenshot_id).all()

def get_screenshot_by_name(db: Session, screenshot_name: str):
    return db.query(Screenshot).filter(Screenshot.id == screenshot_name).first()

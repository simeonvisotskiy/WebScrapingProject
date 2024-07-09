import os
import sys
import subprocess
import uuid
import time
from fastapi import FastAPI, Form, Depends, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy import Column, String, Integer, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session

# FastAPI app initialization
app = FastAPI()

# SQLAlchemy models and database setup
DATABASE_URL = "sqlite:///./test.db"  # Example using SQLite

Base = declarative_base()


class Screenshot(Base):
    __tablename__ = 'screenshots'
    id = Column(String, primary_key=True, index=True)
    url = Column(String, index=True)
    type = Column(String)
    file_path = Column(String)
    part = Column(Integer)


engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base.metadata.create_all(bind=engine)


# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# CRUD functions
def create_screenshot(db: Session, screenshot: Screenshot):
    db.add(screenshot)
    db.commit()
    db.refresh(screenshot)
    return screenshot


def get_screenshot(db: Session, screenshot_id: str):
    return db.query(Screenshot).filter(Screenshot.id == screenshot_id).first()


def get_screenshots_by_url(db: Session, url: str):
    return db.query(Screenshot).filter(Screenshot.url == url).all()


def get_screenshots_by_type(db: Session, type: str):
    return db.query(Screenshot).filter(Screenshot.type == type).all()


# Health check endpoint
@app.get("/isalive")
def is_alive():
    return {"status": "alive"}


# Screenshot capturing endpoint
@app.post("/screenshots")
def start_crawling(url: str = Form(...), num_links: int = Form(...), db: Session = Depends(get_db)):
    # Ensure the screenshots directory exists
    os.makedirs("screenshots", exist_ok=True)

    # Call a separate Python script to handle Playwright operations
    script_path = os.path.join(os.path.dirname(__file__), "playwright_script.py")
    result = subprocess.run([sys.executable, script_path, url, str(num_links)], capture_output=True, text=True)

    if result.returncode != 0:
        return {"error": result.stderr}

    # Process the output and save to database
    for line in result.stdout.split('\n'):
        if line.startswith("Screenshot:"):
            try:
                _, screenshot_id, url, type_, file_path, part = line.split('|')
                screenshot = Screenshot(
                    id=screenshot_id,
                    url=url,
                    type=type_,
                    file_path=file_path,
                    part=int(part)
                )
                create_screenshot(db, screenshot)
            except Exception as e:
                print(f"Failed to create screenshot entry: {e}")

    return {"message": "Screenshots taken and metadata saved"}


# Retrieve screenshots endpoints
@app.get("/screenshots/")
def read_screenshots(url: str = None, type: str = None, db: Session = Depends(get_db)):
    if url:
        return get_screenshots_by_url(db, url)
    if type:
        return get_screenshots_by_type(db, type)
    return db.query(Screenshot).all()


@app.get("/screenshots/{screenshot_id}")
def get_screenshot_by_id(screenshot_id: str, db: Session = Depends(get_db)):
    screenshot = get_screenshot(db, screenshot_id)
    if screenshot is None:
        raise HTTPException(status_code=404, detail="Screenshot not found")
    return screenshot


@app.get("/serve_screenshot/{screenshot_id}")
def serve_screenshot(screenshot_id: str, db: Session = Depends(get_db)):
    screenshot = get_screenshot(db, screenshot_id)
    if screenshot is None:
        raise HTTPException(status_code=404, detail="Screenshot not found")
    return FileResponse(screenshot.file_path)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8000)

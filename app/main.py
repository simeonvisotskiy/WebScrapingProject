import os
import sys
import subprocess
import uuid
from fastapi import FastAPI, Form, Depends, HTTPException
from sqlalchemy import Column, String, Integer, Boolean, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
import logging

logging.basicConfig(level=logging.INFO)

app = FastAPI()

DATABASE_URL = "sqlite:///test.db"
logging.info(f"Using database at: {DATABASE_URL}")

Base = declarative_base()

class Screenshot(Base):
    __tablename__ = 'screenshots'
    id = Column(String, primary_key=True, index=True)
    url = Column(String, index=True)
    type = Column(String)
    file_path = Column(String)  # Necessary if you need to store file paths
    part = Column(Integer)
    parent_id = Column(String, nullable=True)
    scrapable = Column(Boolean, default=False)

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base.metadata.create_all(bind=engine)
logging.info("Database tables created")  # Useful for confirming table creation

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def create_screenshot(db: Session, screenshot: Screenshot):
    try:
        logging.info(f"Creating screenshot entry: {screenshot}")
        db.add(screenshot)
        db.commit()
        db.refresh(screenshot)
        return screenshot
    except Exception as e:
        db.rollback()
        logging.error(f"Failed to create screenshot entry: {e}")
        raise e

def get_screenshot(db: Session, screenshot_id: str):
    logging.info(f"Fetching screenshot with ID: {screenshot_id}")
    return db.query(Screenshot).filter(Screenshot.parent_id == screenshot_id).all()

def get_screenshot_by_name(db: Session, screenshot_name: str):
    logging.info(f"Fetching screenshot with name: {screenshot_name}")
    return db.query(Screenshot).filter(Screenshot.id == screenshot_name).first()

@app.get("/isalive")
def is_alive():
    return {"status": "alive"}

@app.post("/screenshots")
def start_crawling(url: str = Form(...), num_links: int = Form(...), db: Session = Depends(get_db)):
    unique_id = str(uuid.uuid4())

    screenshots_dir = os.path.join(os.path.dirname(__file__), 'screenshots')
    os.makedirs(screenshots_dir, exist_ok=True)

    script_path = os.path.join(os.path.dirname(__file__), "playwright_script.py")

    result = subprocess.run([sys.executable, script_path, url, str(num_links), unique_id, screenshots_dir],
                            capture_output=True, text=True)

    if result.returncode != 0:
        logging.error(f"Error in subprocess: {result.stderr}")
        return {"error": result.stderr}

    scrapable = False
    screenshot_names = []
    for line in result.stdout.splitlines():
        if line.startswith("Screenshot:"):
            scrapable = True
            try:
                _, screenshot_id, url, type_, file_path, part = line.split('|')
                screenshot_name = f"{unique_id}_{screenshot_id}"
                screenshot = Screenshot(
                    id=screenshot_name,
                    url=url.rstrip('/'),
                    type=type_,
                    file_path=file_path,
                    part=int(part),
                    parent_id=unique_id,
                    scrapable=True
                )
                create_screenshot(db, screenshot)
                screenshot_names.append(screenshot_name)
            except Exception as e:
                logging.error(f"Failed to create screenshot entry: {e}")

    parent_screenshot = Screenshot(
        id=unique_id,
        url=url.rstrip('/'),
        type="parent",
        file_path="",
        part=0,
        parent_id=None,
        scrapable=scrapable
    )
    create_screenshot(db, parent_screenshot)

    return {"id": unique_id}

@app.get("/screenshots/{screenshot_id}")
def get_screenshot_by_id(screenshot_id: str, db: Session = Depends(get_db)):
    screenshots = get_screenshot(db, screenshot_id)
    if not screenshots:
        raise HTTPException(status_code=404, detail="Screenshot not found")
    return {"screenshots": [screenshot.id for screenshot in screenshots]}

@app.get("/screenshots/website/{screenshot_name}")
def get_screenshots_by_website(screenshot_name: str, db: Session = Depends(get_db)):
    screenshot = get_screenshot_by_name(db, screenshot_name)
    if not screenshot:
        raise HTTPException(status_code=404, detail="Screenshot ID not found")
    return {"website": screenshot.url}

@app.get("/screenshots/type/{screenshot_name}")
def get_screenshots_by_type_route(screenshot_name: str, db: Session = Depends(get_db)):
    screenshot = get_screenshot_by_name(db, screenshot_name)
    if not screenshot:
        raise HTTPException(status_code=404, detail="Screenshot ID not found")
    return {"scrapable": screenshot.scrapable}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
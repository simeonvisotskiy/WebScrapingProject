import os
import sys
import subprocess
import uuid
from fastapi import FastAPI, Form, Depends, HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy import Column, String, Integer, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session

app = FastAPI()

DATABASE_URL = "sqlite:///../test.db"

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
    return db.query(Screenshot).filter(Screenshot.id == screenshot_id).first()


def get_screenshots_by_url(db: Session, url: str):
    return db.query(Screenshot).filter(Screenshot.url == url).all()


def get_screenshots_by_type(db: Session, type: str):
    return db.query(Screenshot).filter(Screenshot.type == type).all()


@app.get("/isalive")
def is_alive():
    return {"status": "alive"}


@app.post("/screenshots")
def start_crawling(url: str = Form(...), num_links: int = Form(...), db: Session = Depends(get_db)):
    unique_id = str(uuid.uuid4())

    screenshots_dir = os.path.join(os.path.dirname(__file__), '../screenshots')
    os.makedirs(screenshots_dir, exist_ok=True)

    script_path = os.path.join(os.path.dirname(__file__), "playwright_script.py")
    result = subprocess.run([sys.executable, script_path, url, str(num_links), unique_id, screenshots_dir],
                            capture_output=True, text=True)

    if result.returncode != 0:
        return {"error": result.stderr}

    scrapable = False
    for line in result.stdout.split('\n'):
        if line.startswith("Screenshot:"):
            scrapable = True
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

    if not scrapable:
        error_message = {"error": "Website structure is inconsistent or not scrapable."}
        screenshot = Screenshot(
            id=unique_id,
            url=url,
            type="error",
            file_path="",
            part=0
        )
        create_screenshot(db, screenshot)
        return JSONResponse(status_code=400, content=error_message)

    return {"message": "Screenshots taken and metadata saved", "id": unique_id}


@app.get("/screenshots/{screenshot_id}")
def get_screenshot_by_id(screenshot_id: str, db: Session = Depends(get_db)):
    screenshot = get_screenshot(db, screenshot_id)
    if screenshot is None:
        raise HTTPException(status_code=404, detail="Screenshot not found")
    return screenshot


@app.get("/screenshots/website/{website}")
def get_screenshots_by_website(website: str, db: Session = Depends(get_db)):
    screenshots = get_screenshots_by_url(db, website)
    if not screenshots:
        raise HTTPException(status_code=404, detail="No screenshots found for this website")
    return screenshots


@app.get("/screenshots/type/{type}")
def get_screenshots_by_type_route(type: str, db: Session = Depends(get_db)):
    screenshots = get_screenshots_by_type(db, type)
    if not screenshots:
        raise HTTPException(status_code=404, detail="No screenshots found for this type")
    return screenshots


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8000)

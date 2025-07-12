from fastapi import FastAPI, UploadFile, File, Form, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import os, shutil, json, uuid

app = FastAPI()

os.makedirs("media/photos", exist_ok=True)
os.makedirs("media/audio", exist_ok=True)
os.makedirs("nft", exist_ok=True)

app.mount("/media", StaticFiles(directory="media"), name="media")
app.mount("/nft", StaticFiles(directory="nft"), name="nft")
templates = Jinja2Templates(directory="templates")

@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    nft_files = os.listdir("nft")
    memories = []
    for file in nft_files:
        with open(f"nft/{file}", "r", encoding="utf-8") as f:
            memories.append(json.load(f))
    return templates.TemplateResponse("gallery.html", {
        "request": request,
        "memories": memories
    })

@app.post("/upload/memory")
async def upload_memory(
    title: str = Form(...),
    description: str = Form(...),
    photo: UploadFile = File(None),
    audio: UploadFile = File(None)
):
    uid = str(uuid.uuid4())
    photo_path = ""
    audio_path = ""

    if photo:
        photo_path = f"media/photos/{uid}_{photo.filename}"
        with open(photo_path, "wb") as f:
            shutil.copyfileobj(photo.file, f)

    if audio:
        audio_path = f"media/audio/{uid}_{audio.filename}"
        with open(audio_path, "wb") as f:
            shutil.copyfileobj(audio.file, f)

    nft_meta = {
        "id": uid,
        "title": title,
        "description": description,
        "photo": "/" + photo_path if photo else "",
        "audio": "/" + audio_path if audio else ""
    }

    with open(f"nft/{uid}.json", "w", encoding="utf-8") as f:
        json.dump(nft_meta, f, ensure_ascii=False, indent=2)

    return {"status": "created", "id": uid}
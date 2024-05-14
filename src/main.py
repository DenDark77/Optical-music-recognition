import os

from pathlib import Path
from fastapi import FastAPI, Request, HTTPException, File, UploadFile, Form
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from shutil import copyfileobj

from recognize.music import notes_to_music_with_instrument, prediction


app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="templates")


UPLOAD_DIR = "uploads"
MUSIC_DIR = "music"
if not os.path.exists(UPLOAD_DIR):
    os.makedirs(UPLOAD_DIR)


@app.get("/")
async def index(request: Request):
    return templates.TemplateResponse(
        request=request, name="home.html"
    )


@app.get("/process_image", response_class=HTMLResponse)
async def get_process_image(request: Request):
    file_path = os.path.join(MUSIC_DIR, "music.mid")

    if os.path.exists(file_path):
        with open(file_path, "rb") as file:
            result = file.read()
        os.remove(file_path)

        return templates.TemplateResponse("result.html", {"request": request, "music_file": result})
    else:
        return templates.TemplateResponse("result.html", {"request": request})


@app.post("/process_image", response_class=HTMLResponse)
async def process_image(
        request: Request,
        instrument_name: str = Form(...),
        temp: int = Form(...),
        music_sheet: UploadFile = File(...),
        notes_data: str = None
):
    try:
        file_path = os.path.join(UPLOAD_DIR, music_sheet.filename)
        with open(file_path, "wb") as file:
            copyfileobj(music_sheet.file, file)
        array_data = prediction(file_path)
        if notes_data is not None:
            result = notes_to_music_with_instrument(notes_data, instrument_name, temp)
            print(result)
            result_file_path = os.path.join(MUSIC_DIR, "music.mid")
            result.write('midi', fp=result_file_path)

        photo_url = f"/uploads/{Path(file_path).name}"

        return templates.TemplateResponse("result.html", {
            "request": request,
            "array_data": array_data,
            "instrument_name": instrument_name,
            "temp": temp,
            "photo_url": photo_url,
        })
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/about", response_class=HTMLResponse)
async def about(request: Request):
    return templates.TemplateResponse(
        request=request, name="about.html"
    )



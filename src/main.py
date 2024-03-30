import os
from fastapi import FastAPI, Request, HTTPException, File, UploadFile, Form
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from io import BytesIO
from shutil import copyfileobj

from recognize.music import notes_to_music_with_instrument


app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="templates")


UPLOAD_DIR = "uploads"
if not os.path.exists(UPLOAD_DIR):
    os.makedirs(UPLOAD_DIR)


@app.get("/")
async def index(request: Request):
    return templates.TemplateResponse(
        request=request, name="base.html"
    )


@app.get("/process_image", response_class=HTMLResponse)
async def get_process_image(request: Request):
    return templates.TemplateResponse("result.html", {"request": request})


@app.post("/process_image")
async def process_image(
        request: Request,
        instrument_name: str = Form(...),
        temp: int = Form(...),
        music_sheet: UploadFile = File(...)
):
    try:
        file_path = os.path.join(UPLOAD_DIR, music_sheet.filename)
        with open(file_path, "wb") as file:
            copyfileobj(music_sheet.file, file)

        result = notes_to_music_with_instrument(file_path, instrument_name, temp)
        print(result)
        file_path = "music_with_violin.mid"
        result.write('midi', fp=file_path)
        return templates.TemplateResponse("result.html", {"request": request, "music_file": result, "instrument_name": instrument_name, "temp": temp})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

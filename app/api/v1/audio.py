import uuid
import torch
from fastapi import APIRouter, UploadFile, File, HTTPException, Form
from fastapi.responses import FileResponse, JSONResponse

from app.core.config import load_models_config
from app.services.separation import separate_audio
import os
from app.logger import logger
from app.utils.zip import zip_folder

router = APIRouter()

# Создаем папки, если их нет
UPLOAD_DIR = "uploads"
OUTPUT_DIR = "outputs"

os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)


@router.get("/models", response_class=JSONResponse)
async def available_models():
    config = load_models_config()
    result = []
    for (model_name, model) in [*config["models"].items()]:
        result.append({"name":model_name, "sources":model["sources"], "variants":[*model["variants"].keys()]})
    return result



@router.post("/separate", response_class=JSONResponse)
async def separate_audio_endpoint(model: str = Form(...) , variant: str = Form(...) , file: UploadFile = File(...)):
    input_path = os.path.join(UPLOAD_DIR, file.filename)
    logger.info(f"model: {model}, variant: {variant}, input_path: {input_path}")
    try:
        with open(input_path, "wb") as buffer:
            buffer.write(await file.read())
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка сохранения файла: {e}")

    try:
        with torch.no_grad():
            uniq = uuid.uuid4()
            output = OUTPUT_DIR + "/" + uniq.hex
            zip_path = os.path.join(output,  "result.zip")
            os.makedirs(output, exist_ok=True)
            result = separate_audio(input_path, output, model, variant)
            logger.info(f"output: {output}, zip_path: {zip_path}")
            return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка разделения аудио: {e}")
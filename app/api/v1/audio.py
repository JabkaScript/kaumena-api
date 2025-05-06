
from fastapi import BackgroundTasks, File, Form, HTTPException, UploadFile, APIRouter
from fastapi.responses import JSONResponse
import os
import uuid
import logging
import torch
from typing import Dict


from app.core.config import load_models_config
from app.services.separation import separate_audio

router = APIRouter()

UPLOAD_DIR = "uploads"
OUTPUT_DIR = "outputs"
logger = logging.getLogger("uvicorn")

# Хранилище состояния задач
tasks: Dict[str, Dict] = {}
chunk_size = 1024*1024*1024


async def background_separate(task_id: str, input_path: str, model: str, variant: str):
    try:
        with torch.no_grad():
            uniq = uuid.uuid4()
            output = os.path.join(OUTPUT_DIR, uniq.hex)
            os.makedirs(output, exist_ok=True)
            result = separate_audio(input_path, output, model, variant)
            tasks[task_id]["status"] = "completed"
            tasks[task_id]["result"] = result
    except Exception as e:
        tasks[task_id]["status"] = "failed"
        tasks[task_id]["error"] = str(e)

@router.post("/separate", response_class=JSONResponse)
async def separate_audio_endpoint(
    background_tasks: BackgroundTasks,
    model: str = Form(...),
    variant: str = Form(...),
    file: UploadFile = File()
):
    task_id = str(uuid.uuid4())
    input_path = os.path.join(UPLOAD_DIR, file.filename)
    logger.info(f"model: {model}, variant: {variant}, input_path: {input_path}")
    try:
        with open(input_path, "wb") as buffer:
            while contents := file.file.read(chunk_size):
                buffer.write(contents)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка сохранения файла: {e}")
    finally:
        file.file.close()
        logger.info(f"file loaded")
        # Сохраняем статус задачи
        tasks[task_id] = {
            "status": "processing",
            "model": model,
            "variant": variant,
            "file": file.filename
        }

        # Добавляем задачу в фон
        background_tasks.add_task(background_separate, task_id, input_path, model, variant)

        # Возвращаем клиенту идентификатор задачи
        return JSONResponse(content={"task_id": task_id, "status": "accepted"}, status_code=202)

@router.get("/task/{task_id}")
async def check_task_status(task_id: str):
    task = tasks.get(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Задача не найдена")
    return task

@router.get("/models", response_class=JSONResponse)
async def available_models():
    config = load_models_config()
    result = []
    for (model_name, model) in [*config["models"].items()]:
        result.append({"name":model_name, "sources":model["sources"], "variants":[*model["variants"].keys()]})
    return result
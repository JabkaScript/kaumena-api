import torch
import torchaudio
from kaumena.models import HTDemucsModel, OpenUnmixModel
import librosa

from app.core.config import load_models_config
from app.logger import logger

SOURCES = ["drums", "bass", "other", "vocals"]


def get_sep_model(model: str = "htdemucs", variant: str = "standard"):
    config = load_models_config()
    device = "cuda" if torch.cuda.is_available() else "cpu"
    if model == "htdemucs":
        sep_model = HTDemucsModel(sources=SOURCES, model_path=config["models"][model]["variants"][variant], device=device, model_included_in_path=config["models"][model]["model_included_in_path"])
        return sep_model
    if model == "convtasnet":
        sep_model = OpenUnmixModel(sources=SOURCES, model_type='umxl', device=device)
        return sep_model
    if model == "mdxnet":
        sep_model = OpenUnmixModel(sources=SOURCES, model_type='umxhq', device=device)
        return sep_model
    if model == "openunmix":
        sep_model = OpenUnmixModel(sources=SOURCES, model_type=variant, device=device)
        return sep_model
    return None


def separate_audio(input_path: str, output_dir: str, model: str = "htdemucs", variant: str = "standard") :
    sep_model = get_sep_model(model, variant)
    waveform, sr = librosa.load(input_path, sr=44100, mono=False)
    logger.info(f"Форма сигнала (waveform.shape): {waveform.shape}, sample rate: {sr}, model: {model}, variant: {variant}")
    result_paths = sep_model.separate(waveform)
    sources = SOURCES
    result = {}
    for source in sources:
        track = result_paths[source]
        result[source] = f"{output_dir}/output_{source}.mp3"
        torchaudio.save(f"{output_dir}/output_{source}.mp3", torch.tensor(track).cpu() , 44100)
    return result
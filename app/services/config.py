import yaml
from pathlib import Path


def load_config(config_path: str) -> dict:
    """
    Загружает и парсит YAML-конфигурационный файл.

    :param config_path: Путь к .yaml файлу.
    :return: Словарь с данными из конфига.
    :raises: FileNotFoundError, YAMLError, RuntimeError
    """
    config_path = Path(config_path)

    if not config_path.exists():
        raise FileNotFoundError(f"Конфигурационный файл не найден: {config_path}")

    try:
        with open(config_path, "r", encoding="utf-8") as file:
            config = yaml.safe_load(file)
        return config
    except yaml.YAMLError as e:
        raise ValueError(f"Ошибка разбора YAML в файле {config_path}: {e}")
    except Exception as e:
        raise RuntimeError(f"Не удалось загрузить конфиг: {e}")
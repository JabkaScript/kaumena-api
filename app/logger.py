import logging
import sys

# Создаем логгер
logger = logging.getLogger("kaumena_api")
logger.setLevel(logging.DEBUG)

# Форматтер
formatter = logging.Formatter(
    fmt="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

# Обработчик для вывода в консоль
console_handler = logging.StreamHandler(sys.stdout)
console_handler.setLevel(logging.DEBUG)
console_handler.setFormatter(formatter)

# Добавляем обработчики к логгеру
logger.addHandler(console_handler)

# Экспортируем логгер
__all__ = ["logger"]
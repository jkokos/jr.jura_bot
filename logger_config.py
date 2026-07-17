import logging
from pathlib import Path


def setup_logging() -> None:
    logs_directory = Path("logs")
    logs_directory.mkdir(exist_ok=True)

    logging.basicConfig(
        level=logging.INFO,
        format=(
            "%(asctime)s | "
            "%(levelname)s | "
            "%(name)s | "
            "%(message)s"
        ),
        datefmt="%d.%m.%Y %H:%M:%S",
        handlers=[
            logging.FileHandler(
                logs_directory / "bot.log",
                encoding="utf-8"
            ),
            logging.StreamHandler()
        ]
    )

    # Уменьшаем количество технических сообщений
    logging.getLogger("aiogram.event").setLevel(logging.WARNING)
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("openai").setLevel(logging.WARNING)
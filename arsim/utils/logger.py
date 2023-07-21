from typing import Optional

import os
import loguru
import sys

if os.path.exists("./.log") is False:
    os.makedirs("./.log")


class Logger:
    __instance: Optional["Logger"] = None
    loguru.logger.remove()
    loguru.logger.add(
        "./.log/arsim.log",
        level="INFO",
        # format="{time} {level} {message}",
        rotation="5 MB",
    )
    # loguru.logger.add(
    #     sys.stdout,
    #     # format="{time} {level} {message}",
    # )

    def __new__(cls, *args, **kwargs):
        if cls.__instance is None:
            cls.__instance = super(Logger, cls).__new__(cls, *args, **kwargs)
        return cls.__instance

    def info(self, msg):
        loguru.logger.info(msg)

    def debug(self, msg):
        loguru.logger.debug(msg)

    def warning(self, msg):
        loguru.logger.warning(msg)

    def error(self, msg):
        loguru.logger.error(msg)

    def arrive(self, time: float, aircraft, position):
        h = int(time / 3600)
        m = int((time - h * 3600) / 60)
        s = int(time - h * 3600 - m * 60)
        loguru.logger.info(f"[{h}:{m}:{s}] {aircraft.name} 到达 {position.name}")

Logger()
logger = loguru.logger
import logging
import signal
import sys
import threading
import time
from datetime import timedelta
from pathlib import Path

import rpyc
import structlog
from pydantic import RedisDsn, ValidationError
from pydantic_settings import BaseSettings, SettingsConfigDict
from rpyc.utils.helpers import classpartial

from conveyor import GoldConveyorService, storage


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="conveyor_")

    debug: bool = False
    data_ttl: timedelta
    data_dir: Path
    listen_port: int
    redis_url: RedisDsn


def main():
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=logging.INFO,
    )

    structlog.configure(
        processors=[
            structlog.stdlib.add_logger_name,
            structlog.stdlib.add_log_level,
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.EventRenamer("message"),
            structlog.processors.JSONRenderer(),
        ],
        wrapper_class=structlog.stdlib.BoundLogger,
        logger_factory=structlog.stdlib.LoggerFactory(),
    )
    logger = structlog.stdlib.get_logger("main")

    try:
        settings = Settings.model_validate({})
    except ValidationError as err:
        for error in err.errors():
            logger.critical(
                f'validating field {".".join(map(str, error["loc"]))}: {error["msg"]}'
            )
        exit(1)

    try:
        repository = storage.RedisRepository(
            str(settings.redis_url), round(settings.data_ttl.total_seconds())
        )
    except Exception as err:
        logger.critical("failed to initialize redis-based repository", error=str(err))
        exit(1)

    try:
        files = storage.FileStorage(settings.data_dir)
    except Exception as err:
        logger.critical("failed to initialize file storage", error=str(err))
        exit(1)

    logger.warn("starting conveyor service", port=settings.listen_port)

    rpyc_logger = structlog.stdlib.get_logger("rpyc")
    rpyc_logger.setLevel(logging.WARN)

    server = rpyc.ThreadedServer(
        classpartial(GoldConveyorService, repository, files),
        port=settings.listen_port,
        logger=rpyc_logger,
        protocol_config=dict(
            allow_safe_attrs=True,
            allow_exposed_attrs=False,
            include_local_traceback=settings.debug,
            include_local_version=settings.debug,
            allow_pickle=False,
        ),
    )

    alive = True

    def shutdown(*_):
        nonlocal alive
        alive = False

    for sig in (signal.SIGTERM, signal.SIGINT):
        signal.signal(sig, shutdown)

    def shutdown_watcher():
        while alive:
            time.sleep(1)

        logger.warn("shutting down conveyor service")

        server.close()
        repository.close()

    shutdown_thread = threading.Thread(target=shutdown_watcher)
    shutdown_thread.start()

    server.start()

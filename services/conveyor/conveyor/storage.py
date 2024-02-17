from dataclasses import dataclass
from pathlib import Path
from typing import Optional, cast
from uuid import UUID

import redis


@dataclass
class DataSet:
    name: str
    description: str
    file_id: UUID


@dataclass
class Model:
    name: str
    file_id: UUID


class RedisRepository:
    def __init__(self, redis_url: str, ttl_seconds: int):
        self.ttl = ttl_seconds
        self.redis = cast(
            redis.Redis,
            redis.Redis.from_url(redis_url, protocol=3, decode_responses=True),
        )
        self.redis.ping()

    def close(self):
        self.redis.close()

    def save_account_creds(self, account_id: UUID, access_key: bytes) -> bool:
        """
        Returns true if access_key wasn't previously bound to any account_id.
        """

        result = self.redis.set(
            RedisRepository.__credentials_key(access_key),
            str(account_id),
            ex=self.ttl,
            nx=True,
        )

        return result == True

    def authenticate_by_creds(self, access_key: bytes) -> Optional[UUID]:
        """
        Returns the parsed account ID associated with this access_key, or None.
        """

        account_id = cast(
            Optional[str], self.redis.get(RedisRepository.__credentials_key(access_key))
        )
        if account_id is None:
            return None

        return UUID(hex=account_id)

    def save_dataset(self, account_id: UUID, dataset: DataSet):
        """
        Saves the dataset entry for the specified account.
        """

        key = RedisRepository.__datasets_key(account_id)

        pl = self.redis.pipeline(transaction=True)
        pl.hset(
            key,
            dataset.name,
            RedisRepository.__encode_dataset(dataset),
        )
        pl.expire(key, self.ttl)
        pl.execute()

    def list_datasets(self, account_id: UUID) -> list[DataSet]:
        """
        List datasets saved for the specified account.
        """

        result = cast(
            dict[str, str],
            self.redis.hgetall(RedisRepository.__datasets_key(account_id)),
        )

        return [
            RedisRepository.__decode_dataset(name, value)
            for name, value in result.items()
        ]

    def get_dataset(self, account_id: UUID, name: str) -> Optional[DataSet]:
        """
        Returns the dataset entry saved for the specified account with such name, or None.
        """

        result = cast(
            Optional[str],
            self.redis.hget(RedisRepository.__datasets_key(account_id), name),
        )
        if result is None:
            return None

        return RedisRepository.__decode_dataset(name, result)

    def save_model(self, account_id: UUID, model: Model):
        """
        Saves the model entry for the specified account.
        """

        key = RedisRepository.__models_key(account_id)

        pl = self.redis.pipeline(transaction=True)
        pl.hset(key, model.name, str(model.file_id))
        pl.expire(key, self.ttl)
        pl.execute()

    def list_models(self, account_id: UUID) -> list[Model]:
        """
        List models saved for the specified account.
        """

        result = cast(
            dict[str, str], self.redis.hgetall(RedisRepository.__models_key(account_id))
        )

        return [Model(name=name, file_id=UUID(value)) for name, value in result.items()]

    def get_model(self, account_id: UUID, name: str) -> Optional[Model]:
        """
        Returns the model entry saved for the specified account with such name, or None.
        """

        result = cast(
            Optional[str],
            self.redis.hget(RedisRepository.__models_key(account_id), name),
        )
        if result is None:
            return None

        return Model(name=name, file_id=UUID(result))

    @staticmethod
    def __credentials_key(key: bytes) -> str:
        return f"credentials:{key.hex()}"

    @staticmethod
    def __datasets_key(account_id: UUID) -> str:
        return f"datasets:{account_id}"

    @staticmethod
    def __models_key(account_id: UUID) -> str:
        return f"models:{account_id}"

    @staticmethod
    def __encode_dataset(dataset: DataSet) -> str:
        return f"{dataset.file_id}\n{dataset.description}"

    @staticmethod
    def __decode_dataset(name: str, value: str) -> DataSet:
        file_id_str, description = value.split("\n", maxsplit=1)
        file_id = UUID(hex=file_id_str)

        return DataSet(name=name, file_id=file_id, description=description)


class FileStorage:
    def __init__(self, dir: Path):
        self.dir = dir
        self.dir.mkdir(parents=True, exist_ok=True)

    def open_read(self, file_id: UUID):
        return open(self.__build_path(file_id), "rb")

    def open_write(self, file_id: UUID):
        return open(self.__build_path(file_id), "wb")

    def __build_path(self, file_id: UUID) -> Path:
        return self.dir.joinpath(str(file_id))

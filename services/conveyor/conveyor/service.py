import secrets
from base64 import b85decode, b85encode
from dataclasses import dataclass
from typing import Optional, cast
from uuid import UUID, uuid4

import numpy as np
import pandas as pd
import pyarrow
import rpyc
import structlog
from pyarrow import feather

from . import config, remote, storage
from .data import DataConveyor, DataFrame
from .model import Model, ModelConveyor

UNEXPECTED_ERROR = Exception("unexpected error has occurred, please retry later")
UNAUTHENTICATED_ERROR = Exception("authentication required")
INVALID_ACCESS_KEY_ERROR = ValueError("invalid access key provided")


@remote.safe({"name", "description"})
@dataclass
class DataSet:
    name: str
    description: str

    @classmethod
    def from_repository(cls, dataset: storage.DataSet) -> "DataSet":
        return cls(name=dataset.name, description=dataset.description)


@remote.safe(
    {
        "account_id",
        "data_conveyor",
        "model_conveyor",
        "create_account",
        "authenticate",
        "save_dataset",
        "list_datasets",
        "load_dataset",
        "save_model",
        "list_models",
        "load_model",
    }
)
class GoldConveyorService(rpyc.Service):
    def __init__(self, repository: storage.RedisRepository, files: storage.FileStorage):
        self.repository = repository
        self.files = files
        self.logger = structlog.stdlib.get_logger("gold-conveyor")
        self.rng = np.random.RandomState(secrets.randbits(30))

        # Attributes exposed by the service
        self.account_id: Optional[UUID] = None  # set when client has authenticated
        self.data_conveyor = DataConveyor(self.rng)
        self.model_conveyor = ModelConveyor(self.rng)

    def on_connect(self, conn: rpyc.Connection):
        endpoints = cast(
            tuple[tuple[str, str], tuple[str, str]], conn._config["endpoints"]
        )

        self.logger = self.logger.bind(
            local=f"{endpoints[0][0]}:{endpoints[0][1]}",
            remote=f"{endpoints[1][0]}:{endpoints[1][1]}",
            connid=conn._config["connid"],
        )

        self.logger.info("client connected")

    def on_disconnect(self, conn):
        self.logger.info("client disconnected")

    def create_account(self) -> str:
        """
        Create new account and return an access key which can be used for authentication.

        This connection will be immediatelly authenticated as the created account.
        """

        access_key = secrets.token_bytes(config.ACCESS_KEY_BYTES)
        account_id = uuid4()

        try:
            result = self.repository.save_account_creds(account_id, access_key)
        except Exception as err:
            self.logger.error(
                "unexpectedly failed to save account credentials to repository",
                error=str(err),
                stack_info=True,
            )
            raise UNEXPECTED_ERROR

        if not result:
            raise Exception("credential generation has failed, please retry")

        self.account_id = account_id
        self.__logger_with_account_id()
        self.logger.info("created new account")

        return GoldConveyorService.__encode_access_key(access_key)

    def authenticate(self, access_key: str):
        """
        Authenticate using the provided access key.
        """

        access_key = str(access_key)

        try:
            access_key_bytes = GoldConveyorService.__decode_access_key(access_key)
        except ValueError:
            raise INVALID_ACCESS_KEY_ERROR

        try:
            result = self.repository.authenticate_by_creds(access_key_bytes)
        except Exception as err:
            self.logger.error(
                "unexpectedly failed to authenticate client",
                error=str(err),
                stack_info=True,
            )
            raise UNEXPECTED_ERROR

        if result is None:
            raise INVALID_ACCESS_KEY_ERROR

        self.account_id = result
        self.__logger_with_account_id()
        self.logger.info("client authenticated")

    def save_dataset(self, df: pd.DataFrame, name: str, description: str):
        """
        Save dataframe as dataset with specified name.
        This call requires authentication.
        """

        if self.account_id is None:
            raise UNAUTHENTICATED_ERROR
        elif len(name.encode()) > config.MAX_DATA_LEN:
            raise ValueError(
                f"dataset name should not be longer than {config.MAX_DATA_LEN} bytes"
            )
        elif len(description.encode()) > config.MAX_DATA_LEN:
            raise ValueError(
                f"dataset description should not be longer than {config.MAX_DATA_LEN} bytes"
            )

        name = str(name)
        description = str(description)
        file_id = uuid4()

        try:
            with self.files.open_write(file_id) as f:
                feather.write_feather(pyarrow.Table.from_pandas(df), f)
        except Exception as err:
            self.logger.error(
                "unexpectedly failed to save dataframe to file",
                file_id=str(file_id),
                error=str(err),
                stack_info=True,
            )
            raise UNEXPECTED_ERROR

        try:
            self.repository.save_dataset(
                self.account_id,
                storage.DataSet(name=name, description=description, file_id=file_id),
            )
        except Exception as err:
            self.logger.error(
                "unexpectedly failed to save dataset info to repository",
                file_id=str(file_id),
                name=name,
                error=str(err),
                stack_info=True,
            )
            raise UNEXPECTED_ERROR

        self.logger.info("saved new dataset", file_id=str(file_id), name=name)

    def list_datasets(self) -> list[DataSet]:
        """
        Return names and descriptions of saved datasets.
        This call requires authentication.
        """

        if self.account_id is None:
            raise UNAUTHENTICATED_ERROR

        try:
            datasets = self.repository.list_datasets(self.account_id)
        except Exception as err:
            self.logger.error(
                "unexpectedly failed to list datasets in repository",
                error=str(err),
                stack_info=True,
            )
            raise UNEXPECTED_ERROR

        return list(map(DataSet.from_repository, datasets))

    def load_dataset(self, name: str) -> DataFrame:
        """
        Load dataframe from dataset with the specified name.
        This call requires authentication.
        """

        if self.account_id is None:
            raise UNAUTHENTICATED_ERROR

        name = str(name)

        try:
            dataset = self.repository.get_dataset(self.account_id, name)
        except Exception as err:
            self.logger.error(
                "unexpectedly failed to get dataset from repository",
                error=str(err),
                stack_info=True,
            )
            raise UNEXPECTED_ERROR

        if dataset is None:
            raise KeyError("no dataset with such name exists")

        try:
            with self.files.open_read(dataset.file_id) as f:
                df = pd.read_feather(f)
        except Exception as err:
            self.logger.error(
                "unexpectedly failed to read dataframe from file",
                file_id=dataset.file_id,
                name=dataset.name,
                error=str(err),
                stack_info=True,
            )
            raise UNEXPECTED_ERROR

        return DataFrame(df)

    def save_model(self, model: Model, name: str, description: str):
        """
        Save model with specified name.
        This call requires authentication.
        """

        if self.account_id is None:
            raise UNAUTHENTICATED_ERROR
        elif len(name.encode()) > config.MAX_DATA_LEN:
            raise ValueError(
                f"model name should not be longer than {config.MAX_DATA_LEN} bytes"
            )
        elif len(description.encode()) > config.MAX_DATA_LEN:
            raise ValueError(
                f"model description should not be longer than {config.MAX_DATA_LEN} bytes"
            )

        name = str(name)
        description = str(description)
        file_id = uuid4()

        model.name = name
        model.description = description

        try:
            with self.files.open_write(file_id) as f:
                model.save(f)
        except Exception as err:
            self.logger.error(
                "unexpectedly failed to save model to file",
                file_id=str(file_id),
                error=str(err),
                stack_info=True,
            )
            raise UNEXPECTED_ERROR

        try:
            self.repository.save_model(
                self.account_id, storage.Model(name=name, file_id=file_id)
            )
        except Exception as err:
            self.logger.error(
                "unexpectedly failed to save model info to repository",
                file_id=str(file_id),
                name=name,
                error=str(err),
                stack_info=True,
            )
            raise UNEXPECTED_ERROR

        self.logger.info("saved new model", file_id=str(file_id), name=name)

    def list_models(self) -> list[str]:
        """
        Return names of saved models.
        This call requires authentication.
        """

        if self.account_id is None:
            raise UNAUTHENTICATED_ERROR

        try:
            models = self.repository.list_models(self.account_id)
        except Exception as err:
            self.logger.error(
                "unexpectedly failed to list models in repository",
                error=str(err),
                stack_info=True,
            )
            raise UNEXPECTED_ERROR

        return [m.name for m in models]

    def load_model(self, name: str) -> Model:
        """
        Load model with the specified name.
        This call requires authentication.
        """

        if self.account_id is None:
            raise UNAUTHENTICATED_ERROR

        name = str(name)

        try:
            model_info = self.repository.get_model(self.account_id, name)
        except Exception as err:
            self.logger.error(
                "unexpectedly failed to get model from repository",
                error=str(err),
                stack_info=True,
            )
            raise UNEXPECTED_ERROR

        if model_info is None:
            raise KeyError("no model with such name exists")

        try:
            with self.files.open_read(model_info.file_id) as f:
                model = Model.load(f)
        except Exception as err:
            self.logger.error(
                "unexpectedly failed to read dataframe from file",
                file_id=model_info.file_id,
                name=model_info.name,
                error=str(err),
                stack_info=True,
            )
            raise UNEXPECTED_ERROR

        return model

    def __logger_with_account_id(self):
        self.logger = self.logger.bind(account_id=str(self.account_id))

    @staticmethod
    def __encode_access_key(access_key: bytes) -> str:
        return b85encode(access_key).decode()

    @staticmethod
    def __decode_access_key(access_key: str) -> bytes:
        return b85decode(access_key)

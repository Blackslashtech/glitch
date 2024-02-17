"""
conveyorlib contains rpyc service type stubs for interacting with the service
"""

from dataclasses import dataclass
from typing import Optional
from uuid import UUID

import numpy as np
import numpy.typing as npt
import pandas as pd


@dataclass
class AlloyComposition:
    ALLOWED = set(["gold_fr", "silver_fr", "copper_fr", "platinum_fr"])

    gold_fr: float
    silver_fr: float
    copper_fr: float
    platinum_fr: float

    def _rpyc_getattr(self, name):
        if name in AlloyComposition.ALLOWED:
            return getattr(self, name)
        raise AttributeError("access denied")


class DataConveyor:
    def random_alloy_samples(
        self, weight_ozt: float, max_deviation: float, samples: int
    ) -> pd.DataFrame: ...

    def template_alloy_samples(
        self,
        template: AlloyComposition,
        weight_ozt: float,
        max_deviation: float,
        samples: int,
    ) -> pd.DataFrame: ...

    def concat_samples(self, *dfs: pd.DataFrame) -> pd.DataFrame: ...

    def normalize_sample_weights(self, df: pd.DataFrame) -> pd.DataFrame: ...

    def split_samples(
        self, *dfs: pd.DataFrame, proportion: float
    ) -> list[pd.DataFrame]: ...


MatrixLike = np.ndarray | pd.DataFrame
ArrayLike = npt.ArrayLike


class Model:
    name: str
    description: str

    def predict(self, X: MatrixLike) -> np.ndarray: ...

    def score(self, X: MatrixLike, y: MatrixLike | ArrayLike) -> float: ...


class ModelConveyor:
    def fit_linear_regression(self, x: npt.ArrayLike, y: npt.ArrayLike) -> Model: ...

    def fit_ridge(self, x: npt.ArrayLike, y: npt.ArrayLike) -> Model: ...

    def mean_absolute_error(
        self, y_true: npt.ArrayLike, y_pred: npt.ArrayLike
    ) -> float: ...

    def mean_squared_error(
        self, y_true: npt.ArrayLike, y_pred: npt.ArrayLike
    ) -> float: ...


class DataSetInfo:
    name: str
    description: str


class GoldConveyorService:
    account_id: Optional[UUID]
    data_conveyor: DataConveyor
    model_conveyor: ModelConveyor

    def create_account(self) -> str: ...

    def authenticate(self, access_key: str): ...

    def save_dataset(self, df: pd.DataFrame, name: str, description: str): ...

    def list_datasets(self) -> list[DataSetInfo]: ...

    def load_dataset(self, name: str) -> pd.DataFrame: ...

    def save_model(self, model: Model, name: str, description: str): ...

    def list_models(self) -> list[str]: ...

    def load_model(self, name: str) -> Model: ...

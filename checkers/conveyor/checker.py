#!/usr/bin/env python3

import json
import random
import sys
import traceback
from collections import UserList
from enum import Enum
from functools import partial
from typing import cast

import pandas as pd
import rpyc
from checklib import BaseChecker, Status, cquit, rnd_string

from conveyorlib import (
    AlloyComposition,
    DataConveyor,
    GoldConveyorService,
    Model,
    ModelConveyor,
)

SERVICE_PORT = 12378
MAX_SAMPLES = 100
MIN_SAMPLES = MAX_SAMPLES // 2
FEATURES = [
    "gold_ozt",
    "silver_ozt",
    "copper_ozt",
    "platinum_ozt",
    "troy_ounces",
    "karat",
    "fineness",
]
ALLOYS = [
    AlloyComposition(gold_fr=0.75, silver_fr=0.125, copper_fr=0.125, platinum_fr=0),
    AlloyComposition(gold_fr=0.75, silver_fr=0, copper_fr=0.25, platinum_fr=0),
    AlloyComposition(gold_fr=0.75, silver_fr=0.025, copper_fr=0.225, platinum_fr=0),
    AlloyComposition(gold_fr=0.75, silver_fr=0.05, copper_fr=0.2, platinum_fr=0),
    AlloyComposition(gold_fr=0.75, silver_fr=0, copper_fr=0, platinum_fr=0.25),
]
PRECISION = 1e-3
MAX_DATA_LEN = 128


# rnd_weight returns random number of ounces for DataConveyor
def rnd_weight() -> float:
    return random.random() * 10


# rnd_deviation returns random deviation for DataConveyor
def rnd_deviation() -> float:
    return random.random() * 0.1


# rnd_nsamples returns random number of samples for DataConveyor
def rnd_nsamples() -> int:
    return random.randint(MIN_SAMPLES, MAX_SAMPLES)


# rnd_features returns a random list of features and a target for model training
def rnd_features() -> tuple[list[str], str]:
    features = random.choices(FEATURES, k=random.randint(2, len(FEATURES) - 1))
    left = list(set(FEATURES).difference(features))
    target = random.choice(left)
    return features, target


# rnd_name generates random name of model or dataset
def rnd_name(info: str) -> str:
    length = random.randint(MAX_DATA_LEN // 2, MAX_DATA_LEN - len(info) - 1)
    return info + "_" + rnd_string(length)


# rnd_description generates random description of model or dataset
def rnd_description() -> str:
    return rnd_string(random.randint(MAX_DATA_LEN // 2, MAX_DATA_LEN))


class FlagPlace(Enum):
    DATASET = 1
    MODEL = 2


class Checker(BaseChecker):
    vulns: int = 2
    timeout: int = 20
    uses_attack_data: bool = True

    conn: rpyc.Connection
    service: GoldConveyorService
    data_conveyor: DataConveyor
    model_conveyor: ModelConveyor

    def __init__(self, *args, **kwargs):
        super(Checker, self).__init__(*args, **kwargs)

    def action(self, action, *args, **kwargs):
        try:
            super(Checker, self).action(action, *args, **kwargs)
        except ConnectionError as err:
            self.cquit(Status.DOWN, "Connection error", f"Connection error: {err}")
        except TimeoutError as err:
            self.cquit(Status.DOWN, "Timeout error", f"Timeout error: {err}")
        except Exception as err:
            if "_get_exception_class" in type(err).__qualname__:
                err_desc = str(err).split("\n", 1)[0]  # error without the remote part
                self.cquit(
                    Status.MUMBLE,
                    f"Unexpected remote error: {err_desc}",
                    f"Unexpected remote error: {traceback.format_exception(err)}",
                )
            else:
                raise

    def check(self):
        self._connect()

        # Generate DataFrame, like for put
        (want_weight, want_deviation, want_nsamples), df = self._generate_samples()
        self.assert_eq(
            len(df),
            want_nsamples,
            "Incorrect length of generated DataFrame",
            Status.MUMBLE,
        )
        self.assert_eq(
            df.shape,
            (want_nsamples, len(FEATURES)),
            "Incorrect shape of generated DataFrame",
            Status.MUMBLE,
        )
        self.assert_neq(
            str(df.head(1)),
            "",
            "Empty head() of generated DataFrame",
            Status.MUMBLE,
        )
        self.assert_gt(
            want_deviation,
            abs(
                df.iloc[random.randint(0, want_nsamples - 1)]["troy_ounces"]
                - want_weight
            )
            / want_weight,
            "Generated DataFrame weight deviates too much",
            Status.MUMBLE,
        )

        # Additionally test DataFrame weight normalization
        if random.randint(0, 1) == 0:
            df = self.data_conveyor.normalize_sample_weights(df)
            self.assert_gt(
                PRECISION,
                abs(df.iloc[random.randint(0, want_nsamples - 1)]["troy_ounces"] - 1.0),
                "Normalized DataFrame weight deviates too much",
                Status.MUMBLE,
            )

        # Pick DataFrame features/target and split them into train/test datasets
        features, target = rnd_features()
        x, y = df[UserList(features)], df[UserList([target])]
        splits = self.data_conveyor.split_samples(x, y, proportion=0.8)
        self.assert_eq(
            len(splits), 4, "Incorrect number of DataFrames after split", Status.MUMBLE
        )
        x_train, x_test, y_train, y_test = splits
        self.assert_eq(
            len(x_train),
            len(y_train),
            "Train X and Y length mismatch after split",
            Status.MUMBLE,
        )
        self.assert_eq(
            len(x_test),
            len(y_test),
            "Test X and Y length mismatch asfter split",
            Status.MUMBLE,
        )

        # Train model and test it
        model = self._train_model(x_train, y_train)
        test_mode = random.randint(0, 2)
        if test_mode == 0:
            score = model.score(x_test, y_test)
        elif test_mode == 1:
            predict = model.predict(x_test)
            score = self.model_conveyor.mean_absolute_error(y_test, predict)
        else:
            predict = model.predict(x_test)
            score = self.model_conveyor.mean_squared_error(y_test, predict)

        self._disconnect()
        self.cquit(Status.OK)

    def put(self, _flag_id: str, flag: str, vuln: str):
        flag_place = self._parse_vuln(vuln)
        self._connect()

        access_key = self.service.create_account()
        account_id = str(self.service.account_id)

        # Always generate dataset, because it is needed for both flag places
        (_, _, want_nsamples), df = self._generate_samples()
        self.assert_eq(
            len(df),
            want_nsamples,
            "Incorrect length of generated DataFrame",
            Status.MUMBLE,
        )

        dataset_params = []
        model_params = []

        if flag_place == FlagPlace.DATASET:
            # Save dataset with random info, one containing the flag in its description
            extra_datasets = random.randint(1, 2)
            dataset_params = [
                (rnd_name("dataset"), rnd_description()) for _ in range(extra_datasets)
            ]
            dataset_params.append((rnd_name("dataset"), flag))
            random.shuffle(dataset_params)

            for name, description in dataset_params:
                self.service.save_dataset(df, name, description)
        else:
            features, target = rnd_features()
            x, y = df[UserList(features)], df[UserList([target])]
            model = self._train_model(x, y)

            # Save model with random info, one containing the flag in its description
            extra_models = random.randint(1, 2)
            model_params = [
                (rnd_name("model"), rnd_description()) for _ in range(extra_models)
            ]
            model_params.append((rnd_name("model"), flag))
            random.shuffle(model_params)

            for name, description in model_params:
                self.service.save_model(model, name, description)

        self._disconnect()

        private = dict(
            k=access_key,
            i=account_id,
            p=dataset_params,
            n=want_nsamples,
            m=model_params,
        )
        private = json.dumps(private, separators=(",", ":"))

        self.cquit(Status.OK, f"account_id: {account_id}", private)

    def get(self, flag_id: str, flag: str, vuln: str):
        flag_place = self._parse_vuln(vuln)
        private = json.loads(flag_id)
        access_key = private["k"]
        account_id = private["i"]
        dataset_params = private["p"]
        model_params = private["m"]
        nsamples = private["n"]

        self._connect()

        # Always check authentication
        try:
            self.service.authenticate(access_key)
        except ValueError as err:
            self.cquit(
                Status.CORRUPT,
                "Failed to authenticate",
                f"Failed to authenticate as {account_id} using key {access_key}: {err}",
            )
        self.assert_eq(
            str(self.service.account_id),
            account_id,
            "Account ID mismatch",
            Status.CORRUPT,
        )

        if flag_place == FlagPlace.DATASET:
            want_datasets = dict(dataset_params)
            dataset_info = self.service.list_datasets()
            for info in dataset_info:
                name, description = info.name, info.description
                self.assert_in(
                    name,
                    want_datasets,
                    "list_datasets returned unknown dataset",
                    Status.CORRUPT,
                )
                self.assert_eq(
                    description,
                    want_datasets[name],
                    "list_datasets returned incorrect dataset description",
                    Status.CORRUPT,
                )
                want_datasets.pop(name)

            self.assert_eq(
                0,
                len(want_datasets),
                "datasets missing from list_datasets result",
                Status.CORRUPT,
            )

            flag_dataset_name = next(filter(lambda p: p[1] == flag, dataset_params))[0]
            df = self.service.load_dataset(flag_dataset_name)
            self.assert_eq(
                nsamples,
                len(df),
                "Incorrect length of loaded DataFrame",
                Status.CORRUPT,
            )
        else:
            want_names = set(map(lambda p: p[0], model_params))
            model_names = self.service.list_models()
            for name in model_names:
                self.assert_in(
                    name,
                    want_names,
                    "list_models returned unknown model",
                    Status.CORRUPT,
                )
                want_names.remove(name)

            self.assert_eq(
                0,
                len(want_names),
                "models missing from list_models result",
                Status.CORRUPT,
            )

            flag_model_name = next(filter(lambda p: p[1] == flag, model_params))[0]
            model = self.service.load_model(flag_model_name)
            self.assert_eq(
                model.name,
                flag_model_name,
                "Incorrect name of loaded model",
                Status.CORRUPT,
            )
            self.assert_eq(
                model.description,
                flag,
                "Incorrect description of loaded model",
                Status.CORRUPT,
            )

        self._disconnect()
        self.cquit(Status.OK)

    def _connect(self):
        self.conn = cast(
            rpyc.Connection,
            rpyc.connect(
                host=self.host,
                port=SERVICE_PORT,
                config=dict(
                    include_local_traceback=False,
                    include_local_version=False,
                ),
            ),
        )

        self.service = cast(GoldConveyorService, self.conn.root)
        self.data_conveyor = self.service.data_conveyor
        self.model_conveyor = self.service.model_conveyor

    def _disconnect(self):
        self.conn.close()

    def _parse_vuln(self, vuln: str) -> FlagPlace:  # type: ignore
        if vuln == "1":
            return FlagPlace.DATASET
        elif vuln == "2":
            return FlagPlace.MODEL
        else:
            c.cquit(Status.ERROR, "Checker error", f"Got unexpected vuln value {vuln}")

    def _generate_samples(
        self,
    ) -> tuple[tuple[float, float, int], pd.DataFrame]:
        want_weight = rnd_weight()
        want_deviation = rnd_deviation()
        want_nsamples = rnd_nsamples()
        params = (want_weight, want_deviation, want_nsamples)

        generators = [
            self.data_conveyor.random_alloy_samples,
            partial(self.data_conveyor.template_alloy_samples, random.choice(ALLOYS)),
        ]

        generators.append(
            lambda w, d, n: self.data_conveyor.concat_samples(
                generators[0](w, d, n // 2), generators[1](w, d, n - n // 2)
            )
        )

        return params, random.choice(generators)(
            want_weight, want_deviation, want_nsamples
        )

    def _train_model(self, x: pd.DataFrame, y: pd.DataFrame) -> Model:
        if random.randint(0, 1) == 0:
            return self.model_conveyor.fit_linear_regression(x, y)
        else:
            return self.model_conveyor.fit_ridge(x, y)


if __name__ == "__main__":

    c = Checker(sys.argv[2])

    try:
        c.action(sys.argv[1], *sys.argv[3:])
    except c.get_check_finished_exception():
        cquit(Status(c.status), c.public, c.private)

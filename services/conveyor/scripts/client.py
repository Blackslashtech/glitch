import argparse
from collections import UserList as ulist
from typing import cast

import rpyc

from conveyor import AlloyComposition, GoldConveyorService


def main():
    argument_parser = argparse.ArgumentParser(
        prog="conveyor-client",
        description="Example client for the RPYC-powered gold ML dataset/model conveyors.",
    )
    argument_parser.add_argument(
        "host", help="Conveyor service connection target host.", type=str
    )
    argument_parser.add_argument(
        "port", help="Conveyor service connection target port.", type=int
    )

    # Connect to remote, allowing public attribute access in order to properly pass arguments.
    args = argument_parser.parse_args()
    conn: rpyc.Connection = rpyc.connect(
        host=args.host,
        port=args.port,
        config=dict(
            allow_public_attrs=True,
            include_local_traceback=False,  # don't include traceback to save bandwidth
            include_local_version=False,
        ),
    )
    service: GoldConveyorService = cast(GoldConveyorService, conn.root)

    # Select samples of different origins and combine them.
    custom_samples = service.data_conveyor.template_alloy_samples(
        AlloyComposition(gold_fr=0.83, silver_fr=0.05, copper_fr=0.02, platinum_fr=0.1),
        weight_ozt=5,
        max_deviation=0.01,
        samples=50,
    )
    random_samples = service.data_conveyor.random_alloy_samples(
        weight_ozt=2, max_deviation=0.005, samples=50
    )
    samples = service.data_conveyor.concat_samples(custom_samples, random_samples)

    print(f"Samples:\n{samples.head()}\n")

    # Normalize samples before working with them.
    samples = service.data_conveyor.normalize_sample_weights(samples)

    print(f"Normalized samples:\n{samples.head()}\n")

    # Split them in preparation for training and testing.
    x, y = (
        samples[ulist(["gold_ozt", "silver_ozt", "copper_ozt", "platinum_ozt"])],
        samples[ulist(["karat"])],
    )

    x_train, x_test, y_train, y_test = service.data_conveyor.split_samples(
        x, y, proportion=0.8
    )

    print(
        f"Train/Test frames shapes:\n - x_train {x_train.shape}\n - y_train {y_train.shape}\n - x_test {x_test.shape}\n - y_test {y_test.shape}\n"
    )

    # Train model and score it on the test data.
    model = service.model_conveyor.fit_linear_regression(x_train, y_train)
    print(f"Train score: {model.score(x_train, y_train)}")
    print(f"Test score: {model.score(x_test, y_test)}")

    prediction = model.predict(x_test)
    print(f"Test MAE: {service.model_conveyor.mean_absolute_error(y_test, prediction)}")
    print(f"Test MSA: {service.model_conveyor.mean_squared_error(y_test, prediction)}")

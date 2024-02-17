from typing import Annotated, Callable

import numpy as np
import pandas as pd
import pandera as pa
import pandera.typing as pt
import pydantic
from sklearn.model_selection import train_test_split

from . import config, remote


class AlloyComposition(pydantic.BaseModel):
    gold_fr: Annotated[float, pydantic.Field(ge=0, le=1)]
    silver_fr: Annotated[float, pydantic.Field(ge=0, le=1)]
    copper_fr: Annotated[float, pydantic.Field(ge=0, le=1)]
    platinum_fr: Annotated[float, pydantic.Field(ge=0, le=1)]

    @pydantic.model_validator(mode="after")
    def check_fraction(self):
        fr = self.gold_fr + self.silver_fr + self.copper_fr + self.platinum_fr
        if abs(fr - 1.0) > config.PRECISION:
            raise ValueError("alloy composition fractions should add up to 1")
        return self

    @classmethod
    def localized(cls, remote: "AlloyComposition") -> "AlloyComposition":
        """
        Recreate AlloyComposition dataclass instance from non-trusted instance,
        revalidating it in the process.
        """

        return cls(
            gold_fr=remote.gold_fr,
            silver_fr=remote.silver_fr,
            copper_fr=remote.copper_fr,
            platinum_fr=remote.platinum_fr,
        )


class PredefinedAlloys:
    YELLOW_GOLD = AlloyComposition(
        gold_fr=0.75, silver_fr=0.125, copper_fr=0.125, platinum_fr=0
    )

    RED_GOLD = AlloyComposition(
        gold_fr=0.75, silver_fr=0, copper_fr=0.25, platinum_fr=0
    )

    ROSE_GOLD = AlloyComposition(
        gold_fr=0.75, silver_fr=0.025, copper_fr=0.225, platinum_fr=0
    )

    PINK_GOLD = AlloyComposition(
        gold_fr=0.75, silver_fr=0.05, copper_fr=0.2, platinum_fr=0
    )

    WHITE_GOLD = AlloyComposition(
        gold_fr=0.75, silver_fr=0, copper_fr=0, platinum_fr=0.25
    )


@remote.safe({"iloc", "head", "shape"})
class DataFrame(pd.DataFrame):
    """
    Specialized dataframe subclassing the usual pandas dataframe.
    """

    class Schema(pa.DataFrameModel):
        gold_ozt: pt.Series[float] = pa.Field(ge=0)
        silver_ozt: pt.Series[float] = pa.Field(ge=0)
        copper_ozt: pt.Series[float] = pa.Field(ge=0)
        platinum_ozt: pt.Series[float] = pa.Field(ge=0)
        troy_ounces: pt.Series[float] = pa.Field(ge=0)
        karat: pt.Series[float] = pa.Field(ge=0, le=24)
        fineness: pt.Series[float] = pa.Field(ge=0, le=1000)

    def __init__(self, *args, **kwargs):
        # Check to avoid creating NaN columns when casting existing pandas DataFrame to this one.
        if len(args) == 0:
            kwargs["columns"] = [
                "gold_ozt",
                "silver_ozt",
                "copper_ozt",
                "platinum_ozt",
                "troy_ounces",
                "karat",
                "fineness",
            ]

        super().__init__(*args, **kwargs)

    def validate(self):
        DataFrame.Schema.validate(self)


@remote.safe(
    {
        "template_alloy_samples",
        "random_alloy_samples",
        "normalize_sample_weights",
        "concat_samples",
        "split_samples",
    }
)
class DataConveyor:
    """
    Conveyor for working with samples of gold,
    preparing them for later use with models.
    """

    RANDOM_ALLOYS = np.array(
        [
            PredefinedAlloys.YELLOW_GOLD,
            PredefinedAlloys.RED_GOLD,
            PredefinedAlloys.ROSE_GOLD,
            PredefinedAlloys.PINK_GOLD,
            PredefinedAlloys.WHITE_GOLD,
        ]
    )

    def __init__(self, rng: np.random.RandomState):
        self.rng = rng

    def template_alloy_samples(
        self,
        template: AlloyComposition,
        weight_ozt: float,
        max_deviation: float,
        samples: int,
    ) -> DataFrame:
        """
        Selects a number of gold samples fitting the specified alloy template,
        with alloy composition and weight deviating no more than is requested.

        A pandas DataFrame is returned, containing the selected samples.
        """

        validated_template = AlloyComposition.localized(template)

        # TODO optimize generation using template alloy by replacing operations
        # on each sample with operations on an array of samples.
        # Unfortunately, this means that the sample generation process would be different for random_alloy_samples.
        return self.__generate_samples(
            weight_ozt,
            max_deviation,
            samples,
            lambda: self.__randomize_alloy(validated_template, max_deviation),
        )

    def random_alloy_samples(
        self, weight_ozt: float, max_deviation: float, samples: int
    ) -> DataFrame:
        """
        Selects a number of random gold samples with weight deviating no more than is requested.

        A pandas DataFrame is returned, containing the selected samples.
        """

        return self.__generate_samples(
            weight_ozt,
            max_deviation,
            samples,
            lambda: self.__randomize_alloy(
                self.rng.choice(DataConveyor.RANDOM_ALLOYS),
                max_deviation,
            ),
        )

    def normalize_sample_weights(self, df: pd.DataFrame) -> DataFrame:
        """
        Scale sample alloy composition to 1 troy ounce.
        This method works even when not all of the alloy components are present in the dataframe columns.
        """

        if "troy_ounces" not in df.columns:
            raise ValueError("troy_ounces column must be present for normalization")

        weights = df["troy_ounces"]
        components = ["gold_ozt", "silver_ozt", "copper_ozt", "platinum_ozt"]

        for component in components:
            if component in df.columns:
                df[component] /= weights

        df["troy_ounces"] = 1.0

        return DataFrame(df)

    def concat_samples(self, *dfs: pd.DataFrame) -> DataFrame:
        """
        Concatentates multiple sample DataFrames vertically.

        The total number of samples in the resulting DataFrame should not be more than is allowed.
        """

        if sum(map(len, dfs)) > config.MAX_SAMPLES:
            raise ValueError(
                f"total number of samples after concatenating dataframes should not be more than {config.MAX_SAMPLES}"
            )

        return DataFrame(
            pd.concat(dfs, ignore_index=True)
            .sample(frac=1, random_state=self.rng)
            .reset_index(drop=True)
        )

    def split_samples(
        self, *dfs: pd.DataFrame, proportion: float
    ) -> list[pd.DataFrame]:
        """
        Splits multiple sample DataFrames horizontally according to the specified proportion.

        The first part of each split contains the specified proportion, the other part contains 1-proportion.
        """

        if not (proportion >= 0 and proportion <= 1):
            raise ValueError("proportion should be in the range [0.0; 1.0]")

        return [
            DataFrame(df)
            for df in train_test_split(
                *dfs,
                train_size=proportion,
                random_state=self.rng,
            )
        ]

    def __generate_samples(
        self,
        weight_ozt: float,
        max_deviation: float,
        samples: int,
        generator: Callable[[], np.ndarray],
    ) -> DataFrame:
        if weight_ozt < 0:
            raise ValueError("sample weight should be non-negative")
        elif max_deviation < 0 or max_deviation > 1:
            raise ValueError("max deviation should be a fraction")
        elif samples < 0 or samples > config.MAX_SAMPLES:
            raise ValueError(
                f"a non-negative number of samples no more than {config.MAX_SAMPLES} should be specified"
            )

        # Array of generated weights deviating no more than max_deviation
        # from the dezired weight in troy ounces.
        weights = weight_ozt * (
            1 - (2 * max_deviation * self.rng.random(samples)) + max_deviation
        )

        df = DataFrame()
        for i in range(samples):
            sample_alloy_fr = generator()
            sample_karat = round(sample_alloy_fr[0] * 24, config.KARAT_DIGITS)
            sample_fineness = round(sample_alloy_fr[0] * 1000, config.FINENESS_DIGITS)
            sample_weight = weights[i]
            sample_alloy_ozt = sample_alloy_fr * sample_weight

            df.loc[i] = [  # type: ignore # setitem typing is broken for loc
                sample_alloy_ozt[0],
                sample_alloy_ozt[1],
                sample_alloy_ozt[2],
                sample_alloy_ozt[3],
                sample_weight,
                sample_karat,
                sample_fineness,
            ]

        # Perform basic sanity check after dataframe construction.
        df.validate()

        return df

    def __randomize_alloy(
        self, template: AlloyComposition, max_deviation: float
    ) -> np.ndarray:
        fractions = np.array(
            [
                template.gold_fr,
                template.silver_fr,
                template.copper_fr,
                template.platinum_fr,
            ],
            dtype=np.float64,
        )

        # Since this private method accepts only validated compositions,
        # originally, the fractions sum to 1.
        # They are reduced by some amount so that each fraction differs no more than by max_deviation.
        fractions *= 1 - max_deviation * self.rng.random(len(fractions))

        # The resulting shortage must be then redistributed between the present alloy parts.
        shortage = 1 - np.sum(fractions)
        shortage_distribution = self.rng.random(len(fractions))
        shortage_distribution *= fractions > config.PRECISION
        shortage_distribution /= np.sum(shortage_distribution)
        fractions += shortage * shortage_distribution

        return fractions

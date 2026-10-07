from typing import Protocol

import pandas as pd


class DataSource(Protocol):
    @property
    def name(self) -> str: ...

    def load(self) -> pd.DataFrame: ...
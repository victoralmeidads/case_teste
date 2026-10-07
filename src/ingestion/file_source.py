from io import BytesIO

import pandas as pd


class UploadedFileSource:
    def __init__(self, filename: str, content: bytes):
        self.filename = filename
        self.content = content

    @property
    def name(self) -> str:
        return f"Arquivo: {self.filename}"

    def load(self) -> pd.DataFrame:
        extension = self.filename.rsplit(".", 1)[-1].lower()
        stream = BytesIO(self.content)
        if extension == "csv":
            return pd.read_csv(stream)
        if extension in {"xlsx", "xls"}:
            return pd.read_excel(stream)
        raise ValueError("Formato nao suportado. Envie um arquivo CSV ou Excel.")
import json
from pathlib import Path


class JsonRepository:

    def save(self, filepath: Path, data) -> None:

        filepath.parent.mkdir(
            parents=True,
            exist_ok=True
        )

        with open(
            filepath,
            "w",
            encoding="utf-8"
        ) as file:

            json.dump(
                data,
                file,
                ensure_ascii=False,
                indent=4
            )
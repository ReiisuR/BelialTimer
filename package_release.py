import argparse
import hashlib
import os
import tempfile
import time
import zipfile
from pathlib import Path


def create_archive(source_directory, archive_path):

    source_directory = Path(source_directory).resolve()
    archive_path = Path(archive_path).resolve()
    archive_path.parent.mkdir(parents=True, exist_ok=True)

    if not (source_directory / "BelialTimer.exe").is_file():
        raise FileNotFoundError(
            "BelialTimer.exe não foi encontrado em {}".format(
                source_directory
            )
        )

    temporary_file = None
    try:
        with tempfile.NamedTemporaryFile(
            dir=archive_path.parent,
            prefix=".BelialTimer-",
            suffix=".zip.tmp",
            delete=False
        ) as file:
            temporary_file = Path(file.name)

        with zipfile.ZipFile(
            temporary_file,
            "w",
            compression=zipfile.ZIP_DEFLATED,
            compresslevel=9
        ) as archive:
            for path in sorted(source_directory.rglob("*")):
                if path.is_file():
                    archive.write(
                        path,
                        Path(source_directory.name) / path.relative_to(
                            source_directory
                        )
                    )

        with zipfile.ZipFile(temporary_file, "r") as archive:
            invalid_entry = archive.testzip()
            if invalid_entry is not None:
                raise OSError(
                    "Arquivo inválido dentro do ZIP: {}".format(invalid_entry)
                )

        last_error = None
        for attempt in range(5):
            try:
                os.replace(temporary_file, archive_path)
                last_error = None
                break
            except PermissionError as error:
                last_error = error
                if attempt < 4:
                    time.sleep(1)

        if last_error is not None:
            raise last_error

        digest = hashlib.sha256(archive_path.read_bytes()).hexdigest()
        print("ZIP: {}".format(archive_path))
        print("Tamanho: {:.1f} MB".format(archive_path.stat().st_size / 1048576))
        print("SHA-256: {}".format(digest))
    finally:
        if temporary_file is not None and temporary_file.exists():
            temporary_file.unlink()


def main():

    parser = argparse.ArgumentParser()
    parser.add_argument("source_directory")
    parser.add_argument("archive_path")
    arguments = parser.parse_args()
    create_archive(arguments.source_directory, arguments.archive_path)


if __name__ == "__main__":
    main()

import os
import shutil
from dataclasses import dataclass
from pathlib import Path
import json
from json import JSONDecodeError

from dotenv import load_dotenv
import kagglehub

METADATA_PATH = Path(__file__).parent / "statics" / "metadata.json"


@dataclass(frozen=True)
class KaggleDatasetSpec:
    handle: str
    # version: int | None = None


class KaggleDatasetDownloader():

    def __init__(self, spec: KaggleDatasetSpec, dest_dir: str):
        self.spec = spec
        self.dest_dir = dest_dir

    def download(self):
        load_dotenv()
        try:
            print("Starting downloading files from kaggle to hard disk...")
            path = kagglehub.competition_download(self.spec.handle)
            print("Download completed.")

            print("Checking if destination directory exists...")
            if not os.path.isdir(self.dest_dir):
                print("The destination directory does not exist. Creating the directory...")
                os.mkdir(self.dest_dir)
                print(f"Directory has been created. Location: {self.dest_dir}")

            print("Copying files from cache to project...")
            shutil.copytree(path, self.dest_dir, dirs_exist_ok= True)
            print("Completed copying files. Raw data ready for processing.")

            self._validate()

            return self.dest_dir
        except Exception as e:
            raise Exception(f"Got error while downloading kaggle dataset {e}")

    def _validate(self):
        print("Validating the data that has been downloaded...")
        try:
            print("Loading metadata...")
            metadata = None
            with open(METADATA_PATH, "r") as metadata_file:
                metadata = json.load(metadata_file)

            print("Metadata loaded")
        except FileNotFoundError as fne:
            raise FileNotFoundError(f"Metadata was not found. {fne}")
        except JSONDecodeError as json_error:
            raise ValueError(f"Could not load the metadat json file. Make sure the JSON is properly structured out. {json_error}")

        print("Extracting the list of files...")
        downloaded_file = os.listdir(self.dest_dir)

        print("Checking the stats...")
        for expected_file in metadata["llm-response-classification-files"]:
            print("Validating file names...")
            if expected_file['file_name'] not in downloaded_file:
                raise FileNotFoundError(f"Could not find: {expected_file['file_name']}")

        print("Validation complete. Data is ready to go.")

    def _write_manifest(self):  # pragma: no cover -- TODO: unimplemented, see below
        # TODO: write a manifest recording what was downloaded, so future-you doesn't
        # have to guess. Decide on:
        #   - fields: self.spec.handle, download timestamp (datetime.now().isoformat()),
        #     list of validated files
        #   - location: inside self.dest_dir (e.g. data/raw/manifest.json), so it
        #     travels with the data it describes
        #   - when to call it from download(): only after _validate() succeeds, so a
        #     manifest never claims data is good when it isn't
        pass

if __name__ == "__main__":
    load_dotenv()

    dest_dir = os.getenv("RAW_DATASET_PATH")
    if not dest_dir:
        raise EnvironmentError("RAW_DATASET_PATH is not set. Add it to your .env file.")

    spec = KaggleDatasetSpec(handle="llm-classification-finetuning")
    downloader = KaggleDatasetDownloader(spec, dest_dir)
    downloader.download()

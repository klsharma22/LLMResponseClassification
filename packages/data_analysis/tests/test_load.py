import json
from dataclasses import FrozenInstanceError

import pytest

import data_analysis.load as load_module
from data_analysis.load import KaggleDatasetDownloader, KaggleDatasetSpec


@pytest.fixture
def metadata_file(tmp_path, monkeypatch):
    path = tmp_path / "metadata.json"
    path.write_text(json.dumps({
        "llm-response-classification-files": [
            {"file_name": "train.csv"},
            {"file_name": "test.csv"},
        ]
    }))
    monkeypatch.setattr(load_module, "METADATA_PATH", path)
    return path


def test_spec_is_immutable():
    spec = KaggleDatasetSpec(handle="someuser/some-competition")
    with pytest.raises(FrozenInstanceError):
        spec.handle = "changed"


def test_validate_passes_when_all_expected_files_present(tmp_path, metadata_file):
    (tmp_path / "train.csv").touch()
    (tmp_path / "test.csv").touch()
    downloader = KaggleDatasetDownloader(KaggleDatasetSpec(handle="x"), str(tmp_path))

    downloader._validate()


def test_validate_ignores_extra_files(tmp_path, metadata_file):
    (tmp_path / "train.csv").touch()
    (tmp_path / "test.csv").touch()
    (tmp_path / ".gitkeep").touch()
    downloader = KaggleDatasetDownloader(KaggleDatasetSpec(handle="x"), str(tmp_path))

    downloader._validate()


def test_validate_raises_when_a_file_is_missing(tmp_path, metadata_file):
    (tmp_path / "train.csv").touch()
    downloader = KaggleDatasetDownloader(KaggleDatasetSpec(handle="x"), str(tmp_path))

    with pytest.raises(FileNotFoundError):
        downloader._validate()


def test_validate_raises_value_error_on_malformed_metadata(tmp_path, monkeypatch):
    bad_path = tmp_path / "metadata.json"
    bad_path.write_text("{not valid json")
    monkeypatch.setattr(load_module, "METADATA_PATH", bad_path)
    downloader = KaggleDatasetDownloader(KaggleDatasetSpec(handle="x"), str(tmp_path))

    with pytest.raises(ValueError):
        downloader._validate()


def test_validate_raises_file_not_found_when_metadata_missing(tmp_path, monkeypatch):
    monkeypatch.setattr(load_module, "METADATA_PATH", tmp_path / "does_not_exist.json")
    downloader = KaggleDatasetDownloader(KaggleDatasetSpec(handle="x"), str(tmp_path))

    with pytest.raises(FileNotFoundError):
        downloader._validate()


def test_download_success(tmp_path, metadata_file, monkeypatch):
    cache_dir = tmp_path / "cache"
    cache_dir.mkdir()
    (cache_dir / "train.csv").touch()
    (cache_dir / "test.csv").touch()
    dest_dir = tmp_path / "dest"

    monkeypatch.setattr(load_module.kagglehub, "competition_download", lambda handle: str(cache_dir))
    monkeypatch.setattr(load_module, "load_dotenv", lambda: None)

    downloader = KaggleDatasetDownloader(KaggleDatasetSpec(handle="x"), str(dest_dir))
    result = downloader.download()

    assert result == str(dest_dir)
    assert (dest_dir / "train.csv").exists()
    assert (dest_dir / "test.csv").exists()


def test_download_wraps_kagglehub_failure(tmp_path, monkeypatch):
    def boom(handle):
        raise RuntimeError("kaggle is down")

    monkeypatch.setattr(load_module.kagglehub, "competition_download", boom)
    monkeypatch.setattr(load_module, "load_dotenv", lambda: None)

    downloader = KaggleDatasetDownloader(KaggleDatasetSpec(handle="x"), str(tmp_path / "dest"))

    with pytest.raises(Exception, match="Got error while downloading kaggle dataset"):
        downloader.download()

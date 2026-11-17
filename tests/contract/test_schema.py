"""The config schema rejects a broken install and warns about dead keys."""

from __future__ import annotations

import sys
from pathlib import Path

PACK = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PACK / "tools" / "shared"))

import packschema  # noqa: E402


def _valid() -> dict:
    return {
        "default_project": "demo",
        "projects": {"demo": {"project_root": "../proj", "source_roots": ["app"]}},
    }


def test_a_minimal_config_is_valid():
    errors, warnings = packschema.validate(_valid(), packschema.load(PACK))

    assert errors == []
    assert warnings == []


def test_a_missing_source_root_is_an_error():
    config = _valid()
    del config["projects"]["demo"]["source_roots"]

    errors, _ = packschema.validate(config, packschema.load(PACK))

    assert any("source_roots" in problem for problem in errors)


def test_a_relative_project_root_is_still_a_string():
    errors, _ = packschema.validate(_valid(), packschema.load(PACK))

    assert not any("project_root" in problem for problem in errors)


def test_an_empty_projects_map_is_an_error():
    errors, _ = packschema.validate({"projects": {}}, packschema.load(PACK))

    assert errors


def test_deploy_roots_and_doc_files_are_known_lists_of_paths():
    # Rejects a schema that does not know the two write roots: the guard reads them,
    # so an install that sets them must not be warned about a dead key.
    config = _valid()
    config["projects"]["demo"]["deploy_roots"] = ["deploy"]
    config["projects"]["demo"]["doc_files"] = ["README.md"]

    errors, warnings = packschema.validate(config, packschema.load(PACK))

    assert errors == []
    assert warnings == []

    config["projects"]["demo"]["deploy_roots"] = "deploy"
    errors, _warnings = packschema.validate(config, packschema.load(PACK))
    assert errors


def test_an_unknown_key_warns_but_does_not_fail():
    config = _valid()
    config["projects"]["demo"]["typo_key"] = 1

    errors, warnings = packschema.validate(config, packschema.load(PACK))

    assert errors == []
    assert any("typo_key" in warning for warning in warnings)

import pytest

from zomi_syl.registry.models import list_models
from zomi_syl.registry.models import load_model
from zomi_syl.registry.models import model_exists


def test_list_models_returns_at_least_rule():
    """
    The rule backend must always be present.
    """
    models = list_models()
    assert "rule" in models


def test_model_exists_matches_list_models():
    """
    model_exists(name) must agree with list_models().
    """
    models = list_models()
    for name in models:
        assert model_exists(name) is True

    # A clearly invalid backend
    assert model_exists("nonexistent_backend_xyz") is False


def test_load_model_optional_crf():
    """
    CRF may or may not be installed.
    If installed, load_model('crf') must succeed.
    If not installed, it must raise.
    """
    if "crf" in list_models():
        model = load_model("crf")
        assert "backend_instance" in model
    else:
        with pytest.raises(Exception):
            load_model("crf")

    # A clearly invalid backend
    with pytest.raises(Exception):
        load_model("nonexistent_backend_xyz")
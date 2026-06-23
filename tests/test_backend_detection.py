import pytest

from zomi_syl.registry.models import list_models
# from zomi_syl.registry.models import load_model
from zomi_syl.models.loader import load_model
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
    # All listed models must exist
    models = list_models()
    for name in models:
        assert model_exists(name) is True

    # A clearly invalid backend must not exist
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

def test_explicit_backend_error_message():
    from zomi_syl.core.engine import predict

    if "crf" not in list_models():
        with pytest.raises(RuntimeError) as exc:
            predict("kiginna", model="crf")

        msg = str(exc.value)
        assert "not installed" in msg
        assert "Available backends" in msg
        assert "omit --backend" in msg

    if "transformer" not in list_models():
        with pytest.raises(RuntimeError) as exc:
            predict("kiginna", model="transformer")

        msg = str(exc.value)
        assert "not installed" in msg
        assert "Available backends" in msg
        assert "omit --backend" in msg

def test_rule_backend_is_always_present():
    """
    The rule backend must always be installed.
    """
    models = list_models()
    assert "rule" in models
    
def test_crf_backend_optional_but_consistent():
    """
    CRF may or may not be installed.
    If installed, load_model('crf') must succeed.
    If not installed, load_model('crf') must raise.
    """
    if "crf" in list_models():
        model = load_model("crf")
        assert "backend_instance" in model
    else:
        with pytest.raises(Exception):
            load_model("crf")
            
def test_metadata_included_when_requested():
    from zomi_syl.api import syllabify

    result = syllabify("itna", return_metadata=True)
    assert "backend" in result.raw

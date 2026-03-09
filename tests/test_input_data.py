import pytest

from src.input_dataclass import InputData


def test_input_data_accepts_valid_values() -> None:
    item = InputData(
        var_id=1,
        a1=2,
        a2=3,
        a3=4,
        k=5,
        t=100.0,
        lambda0=0.001,
        lambda1=0.001,
        lambda2=0.001,
        lambda3=0.001,
        beta=1.2,
        plots=["Q_3W"],
    )
    assert item.k == 5


def test_input_data_rejects_invalid_k() -> None:
    with pytest.raises(ValueError, match="k must be in range"):
        InputData(
            var_id=1,
            a1=2,
            a2=2,
            a3=2,
            k=999,
            t=100.0,
            lambda0=0.001,
            lambda1=0.001,
            lambda2=0.001,
            lambda3=0.001,
            beta=1.2,
            plots=["Q_3W"],
        )

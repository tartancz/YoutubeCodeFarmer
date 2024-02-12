from time import time
import pytest
from .mocks.youtube_mock import ProgramEndedException


def test_overall(farmer):
    start = time()
    with pytest.raises(ProgramEndedException):
        farmer._farm()
    duration = time() - start
    print(f"Mine duration was {duration} seconds")
    assert farmer.discount_model._Discount is not None
    assert farmer.discount_model._Discount.activated_by_me == True

import pytest
from .mocks.youtube_mock import ProgramEndedException
from time import time

def test_overall(farmer):
    start = time()
    try:
        farmer._farm()
    except ProgramEndedException:
        pass
    duration = time() - start
    print(f"Mine duration was {duration} seconds")
    assert farmer.discount_model._Discount is not None
    assert farmer.discount_model._Discount.activated_by_me == True


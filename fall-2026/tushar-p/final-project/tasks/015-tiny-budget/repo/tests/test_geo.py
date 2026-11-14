import math

import pytest

from geo import circle_area, cm_to_m


def test_circle_area():
    assert circle_area(3) == pytest.approx(math.pi * 9)


def test_cm_to_m():
    assert cm_to_m(250) == 2.5

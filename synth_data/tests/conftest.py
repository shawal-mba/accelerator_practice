"""Test configuration — bootstrap the DataGenerator for matching tests."""

from __future__ import annotations

from src.adapters.generator.faker import FakerAdapter
from src.domain.matching import set_generator

set_generator(FakerAdapter(locale="zu_ZA"))

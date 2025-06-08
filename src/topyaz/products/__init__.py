#!/usr/bin/env python3
# this_file: src/topyaz/products/__init__.py
"""
Products module for topyaz.

This module contains implementations for all supported Topaz products,
providing a unified interface for image and video processing.
"""

from topyaz.products.base import MacOSTopazProduct, TopazProduct, create_product
from topyaz.products.gigapixel import GigapixelAI
from topyaz.products.photo_ai import PhotoAI
from topyaz.products.video_ai import VideoAI

__all__ = [
    # Product implementations
    "GigapixelAI",
    "MacOSTopazProduct",
    "PhotoAI",
    # Base classes
    "TopazProduct",
    "VideoAI",
    "create_product",
]

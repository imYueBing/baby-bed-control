#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Feature Modules Package Initialization File

Provides exports for all modules
"""

# Export Arduino controller related modules
from .arduino import ArduinoController, BaseArduinoController, BedController, HeartRateController

# Export camera manager module
try:
    from .camera import CameraManager
except ImportError:
    # If camera module is unavailable (e.g., running on non-Raspberry Pi), provide availability flag
    CameraManager = None
    HAS_CAMERA = False
else:
    HAS_CAMERA = True

__all__ = [
    'ArduinoController',
    'BaseArduinoController',
    'BedController',
    'HeartRateController',
    'CameraManager',
    'HAS_CAMERA'
] 
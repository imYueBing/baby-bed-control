#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
API Endpoint Package Initialization File
Exports all API endpoint blueprints
"""

# Export endpoint blueprints
from .bed import bed_api, init_bed_api
from .heart_rate import heart_rate_api, init_heart_rate_api
from .video import video_api, init_video_api
from .system import system_api, init_system_api

__all__ = [
    'bed_api', 'init_bed_api',
    'heart_rate_api', 'init_heart_rate_api',
    'video_api', 'init_video_api',
    'system_api', 'init_system_api'
] 
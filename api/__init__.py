#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
API Service Module Initialization File

Provides all API interfaces and WebSocket event handling
"""

from flask import Flask
from flask_socketio import SocketIO

# Export API server class
from .server import APIServer

# Export API blueprint initialization functions
from .endpoints.bed import bed_api, init_bed_api
from .endpoints.heart_rate import heart_rate_api, init_heart_rate_api
from .endpoints.video import video_api, init_video_api
from .endpoints.system import system_api, init_system_api

# Export WebSocket event registration functions
from .websocket.bed import register_bed_socketio_events
from .websocket.heart_rate import register_heart_rate_socketio_events
from .websocket.video import register_video_socketio_events

__all__ = [
    'APIServer',
    'bed_api', 'init_bed_api',
    'heart_rate_api', 'init_heart_rate_api', 
    'video_api', 'init_video_api',
    'system_api', 'init_system_api',
    'register_bed_socketio_events',
    'register_heart_rate_socketio_events',
    'register_video_socketio_events'
] 
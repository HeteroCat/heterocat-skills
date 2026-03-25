#!/usr/bin/env python3
"""
Doubao Seedance Video Generation - Configuration
"""
import os
from pathlib import Path

# API Configuration
API_BASE_URL = "https://ark.cn-beijing.volces.com/api/v3"
API_KEY = os.environ.get("ARK_API_KEY")

# Default Model Configuration
DEFAULT_MODEL = "doubao-seedance-1-5-pro-251215"
LITE_I2V_MODEL = "doubao-seedance-1-0-lite-i2v-250428"

# Default Output Configuration
# Use a repo-portable default output folder under this skill directory.
SKILL_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_OUTPUT_DIR = str(SKILL_ROOT / "outputs")
DEFAULT_DURATION = 5
DEFAULT_RATIO = "adaptive"
DEFAULT_RESOLUTION = "720p"
DEFAULT_GENERATE_AUDIO = True

# Polling Configuration
POLL_INTERVAL = 10
MAX_POLL_TIME = 600  # 10 minutes

# Valid Options
VALID_RATIOS = ["16:9", "9:16", "1:1", "4:3", "3:4", "21:9", "adaptive"]
VALID_RESOLUTIONS = ["480p", "720p", "1080p"]
VALID_DURATIONS = range(4, 13)  # 4-12 seconds
VALID_IMAGE_EXTENSIONS = [".jpg", ".jpeg", ".png", ".webp"]

# Model Options
MODEL_OPTIONS = {
    "doubao-seedance-1-5-pro-251215": "默认，最高品质，支持音画同步",
    "doubao-seedance-1-0-lite-i2v-250428": "轻量级图生视频，支持多图",
}

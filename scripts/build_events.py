from __future__ import annotations

import csv
import hashlib
import json
import re
from collections import defaultdict
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

# This comment intentionally triggers the PR validation workflow.
ROOT = Path(__file__).resolve().parents[1]
CSV_PATH = ROOT / "data" / "Canitrail_Masterkalender_2026_2027.csv"
JSON_PATH = ROOT / "data/events.json"
CALENDAR_ROOT = ROOT / "calendar"

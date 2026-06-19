"""
logger.py — Structured JSON error logging
Each pipeline run gets its own timestamped log file.
"""

import json
import uuid
from datetime import datetime
from pathlib import Path


class PipelineLogger:
    def __init__(self, target: str):
        self.run_id   = str(uuid.uuid4())[:8]
        self.target   = target
        self.started  = datetime.now().isoformat()
        self.errors   = []
        Path("logs").mkdir(exist_ok=True)

    def log_error(self, error: dict) -> None:
        error["run_id"] = self.run_id
        error["ts"]     = datetime.now().isoformat()
        self.errors.append(error)
        print(f"      ✗ Row {error['row']} | {error['field']} | "
              f"{error['issue']} | value={error['value']!r}")

    def save(self) -> str:
        payload = {
            "run_id":    self.run_id,
            "target":    self.target,
            "started":   self.started,
            "completed": datetime.now().isoformat(),
            "error_count": len(self.errors),
            "errors":    self.errors,
        }
        path = f"logs/{self.target}_{self.run_id}.json"
        with open(path, "w") as f:
            json.dump(payload, f, indent=2)
        return path

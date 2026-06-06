import os
import json
from datetime import datetime

class HistoryLogger:

    def __init__(self, filename="victron_history.jsonl", num_samples=100):
        self.filename = filename
        self.num_samples = num_samples
        self._ensure_valid_file()

    def _ensure_valid_file(self):
        """
        Validates the file. If it doesn't exist, is unreadable, 
        or contains corrupted JSON lines, it resets/creates a fresh file.
        """
        if not os.path.exists(self.filename):
            self._reset_file()
            return

        try:
            with open(self.filename, 'r', encoding='utf-8') as f:
                for line in f:
                    if line.strip():  # Skip empty lines
                        json.loads(line)  # Try to parse
        except (json.JSONDecodeError, IOError, OSError):
            # If anything goes wrong (damaged file, locked file, etc.), reset it
            print(f"Warning: {self.filename} was corrupted or unreadable. Resetting file.")
            self._reset_file()

    def _reset_file(self):
        """Creates a fresh, empty log file."""
        with open(self.filename, 'w', encoding='utf-8') as f:
            pass

    def update(self, vrm_status):
        """
        Appends a new status entry. Ensures the data has a timestamp,
        validates the file health, and keeps only the last N samples.
        """
        # 1. Run health checks on the file before modifying
        self._ensure_valid_file()

        # 2. Add or update timestamp if it's missing/null
        if not vrm_status.get("timestamp"):
            vrm_status["timestamp"] = datetime.now().isoformat()

        # 3. Read existing history lines
        lines = []
        if os.path.exists(self.filename):
            with open(self.filename, 'r', encoding='utf-8') as f:
                lines = [line.strip() for line in f if line.strip()]

        # 4. Append the new data structure
        lines.append(json.dumps(vrm_status))

        # 5. Maintain rolling window (remove oldest lines if exceeding num_samples)
        if len(lines) > self.num_samples:
            lines = lines[-self.num_samples:]

        # 6. Write everything back safely
        with open(self.filename, 'w', encoding='utf-8') as f:
            for line in lines:
                f.write(line + '\n')
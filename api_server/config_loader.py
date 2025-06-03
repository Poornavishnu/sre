"""Configuration loader for the API server."""

import os
import yaml

DEFAULT_CONFIG = {
    "influxdb": {
        "url": "http://localhost:8086",
        "database": "metrics"
    }
}


class ConfigLoader:
    """Loads configuration from a YAML file, falling back to defaults if needed."""

    def __init__(self, config_path="config.yaml"):
        self.config_path = config_path
        self.config = self.load_config()

    def load_config(self):
        """Load and parse YAML config file. Return merged config with defaults."""
        if not os.path.exists(self.config_path):
            print(f"Config file not found: {self.config_path}, using defaults.")
            return DEFAULT_CONFIG
        try:
            with open(self.config_path, "r", encoding="utf-8") as f:
                config = yaml.safe_load(f) or {}
                merged = DEFAULT_CONFIG.copy()
                if "influxdb" in config:
                    merged["influxdb"].update(config["influxdb"])
                return merged
        except (OSError, yaml.YAMLError) as e:
            print(f"Failed to load config: {e}, using defaults.")
            return DEFAULT_CONFIG

    def get_config(self):
        """Return the loaded configuration."""
        return self.config
    
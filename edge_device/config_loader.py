import yaml
import os

def load_config(path="config/config.yaml"):
    config = {}

    if os.path.exists(path):
        try:
            with open(path, "r") as f:
                config = yaml.safe_load(f) or {}
        except yaml.YAMLError as e:
            print(f"[ERROR] Failed to parse config: {e}")
            config = {}
    else:
        print(f"[WARN] Config file not found: {path}. Using env vars and defaults.")

    # Basic fields
    config.setdefault("cloud_endpoint", os.getenv("CLOUD_ENDPOINT"))
    config.setdefault("metrics_interval", int(os.getenv("METRICS_INTERVAL", 10)))
    config.setdefault("thresholds", {})
    config.setdefault("device_type", os.getenv("DEVICE_TYPE", "unknown"))
    config.setdefault("tags", {
        "location": os.getenv("LOCATION", "unknown"),
        "zone": os.getenv("ZONE", "default")
    })

    # Metrics
    metrics_env = os.getenv("METRICS")
    if "metrics_to_collect" not in config:
        if metrics_env:
            config["metrics_to_collect"] = [m.strip() for m in metrics_env.split(",")]
        else:
            config["metrics_to_collect"] = ["cpu", "memory", "disk"]

    return config
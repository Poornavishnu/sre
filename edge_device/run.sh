#!/bin/bash

# Activate the virtual environment and start the monitor script
source edge_agent_env/bin/activate
python monitor.py
```

Make sure to run:
```bash
chmod +x run.sh
```

Then launch the agent with:
```bash
./run.sh
```

This script is useful on edge devices to automatically start the monitoring agent after unpacking the bundle.

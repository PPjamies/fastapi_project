import json
import sys
from pathlib import Path

# have script find main.py in the project root
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

# import fastapi app
from app.main import app

# output filename
output = sys.argv[1] if len(sys.argv) > 1 else "openapi.json"

# ask fastapi for the spec and save it
spec = app.openapi()
with open(output, "w") as f:
    json.dump(spec, f, indent=2, sort_keys=True)

print(f"Wrote {output}")

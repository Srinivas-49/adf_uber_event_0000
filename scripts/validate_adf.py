"""Static ADF artifact validation; no Azure credentials required."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1] / "adf_uber_event_0000"

def validate():
    artifacts = sorted(ROOT.rglob("*.json"))
    assert artifacts, "No ADF artifacts found"
    for path in artifacts:
        document = json.loads(path.read_text(encoding="utf-8"))
        assert isinstance(document, dict), f"{path}: expected JSON object"
        if path.parent.name == "pipeline":
            assert "activities" in document.get("properties", {}), f"{path}: missing activities"
        if path.parent.name == "linkedService":
            assert "type" in document.get("properties", {}), f"{path}: missing linked service type"
    pipeline = json.loads((ROOT / "pipeline/HTTP_to_ADLS.json").read_text())
    activities = pipeline["properties"]["activities"]
    assert {"Lookup1", "foreachjson"}.issubset({a["name"] for a in activities})
    print(f"Validated {len(artifacts)} ADF JSON artifacts")

if __name__ == "__main__":
    validate()

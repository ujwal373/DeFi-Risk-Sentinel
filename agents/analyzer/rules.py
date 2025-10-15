import os, yaml
from typing import Any, Dict, List

def load_rules(path: str | None = None) -> Dict[str, Any]:
    path = path or os.getenv("RULES_PATH", "knowledge/rules.yaml")
    with open(path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
    return data

def evaluate(event: Dict[str, Any], ruleset: Dict[str, Any]) -> tuple[List[str], List[str], int]:
    flags, why = [], []
    score = 0
    globs = {"__builtins__": {}}
    locs = {
        "apr": event["apr"],
        "contract_age_days": event["contract_age_days"],
        "protocol": event["protocol"],
    }
    for r in ruleset.get("rules", []):
        try:
            if bool(eval(r["when"], globs, locs)):
                flags.append(r["id"])
                why.append(r.get("why", r["id"]))
                score += int(r.get("weight", 0))
        except Exception:
            # ignore a broken rule; keep MVP resilient
            continue
    cap = int(ruleset.get("scoring", {}).get("cap", 100))
    score = max(0, min(cap, score))
    return flags, why, score

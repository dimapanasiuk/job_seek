"""One-shot import of data/jobs.json into PostgreSQL."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

from app.db.session import SessionLocal
from app.repositories import jobs as jobs_repo

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_PATH = ROOT / "data" / "jobs.json"
BATCH_SIZE = 500


def _load_jobs(path: Path) -> list[dict[str, Any]]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    jobs_map = payload.get("jobs")
    if not isinstance(jobs_map, dict):
        msg = f"Expected 'jobs' object in {path}"
        raise TypeError(msg)
    return [job for job in jobs_map.values() if isinstance(job, dict)]


def main() -> int:
    path = Path(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_PATH
    if not path.is_file():
        print(f"File not found: {path}", file=sys.stderr)
        return 1

    jobs = _load_jobs(path)
    print(f"Loaded {len(jobs)} jobs from {path}")

    session = SessionLocal()
    try:
        stored = 0
        for start in range(0, len(jobs), BATCH_SIZE):
            batch = jobs[start : start + BATCH_SIZE]
            result = jobs_repo.upsert_jobs(session, batch)
            stored = int(result["stored"])
            print(
                f"Upserted batch {start // BATCH_SIZE + 1} "
                f"({len(batch)} rows); total stored={stored}"
            )
        print(f"Done. jobs in DB: {stored}")
    finally:
        session.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

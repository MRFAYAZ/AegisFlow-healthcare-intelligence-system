"""Pure contract rules for replay-safe partner inventory snapshots."""

from datetime import datetime, timedelta
from hashlib import sha256
import json
from typing import Mapping, Any


def canonical_snapshot_hash(payload: Mapping[str, Any]) -> str:
    """Return a stable SHA-256 digest independent of JSON key ordering."""
    canonical = json.dumps(payload, sort_keys=True, separators=(",", ":"))
    return sha256(canonical.encode("utf-8")).hexdigest()


def validate_replay_payload(stored_hash: str, incoming_hash: str) -> None:
    """Accept an identical replay; reject reuse of an event ID with changed content."""
    if stored_hash != incoming_hash:
        raise ValueError(
            "external_event_id was already used with a different payload; use a new event ID for changed content."
        )


def validate_snapshot_timestamp(
    source_timestamp: datetime,
    last_accepted_timestamp: datetime | None,
    now: datetime,
    max_future_skew: timedelta = timedelta(minutes=5),
) -> None:
    """Reject stale timestamps and source clocks too far in the future."""
    if source_timestamp.tzinfo is None or source_timestamp.utcoffset() is None:
        raise ValueError("source_timestamp must include a timezone offset.")

    if last_accepted_timestamp is not None and source_timestamp <= last_accepted_timestamp:
        raise ValueError(
            "Snapshot is stale: source_timestamp must be newer than the last accepted snapshot."
        )

    if source_timestamp > now.replace(microsecond=0) + max_future_skew:
        raise ValueError("source_timestamp is more than five minutes in the future.")

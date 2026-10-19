'''volunteers/mongo.py
----------------------
PyMongo integration for auxiliary real-time data that does not need the Django ORM.
Three collections are defined:
  * operations_logs    - audit trail for coordinator actions
  * volunteer_feedback  -free-form feedback from volunteers
  * emergency_dispatches - urgent resource dispatch records
The module provides:
  * a singleton ``MongoClient`` with a short timeout (fails fast if MongoDB is offline)
  * graceful **in-memory fallback** so the app continues to work without a running Mongo instance
  * helper functions for each collection (create, read, update, delete) with **basic validation**
  * ``is_mongo_online()``- used by the context processor to surface connection status in the UI

NOTE: All functions return plain Python ``dict`` objects - they never expose ``ObjectId``
instances to the rest of the Django code. When the fallback store is used an ``uuid4``
string mimics an ObjectId.
''' 

import logging
import uuid
from datetime import datetime
from typing import List, Optional, Dict, Any

from django.conf import settings

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Singleton MongoDB client – created on first use with a 1.5‑second timeout.
# ---------------------------------------------------------------------------
_client = None
_db = None
_mongo_online: Optional[bool] = None  # Cached connection flag (None = not yet checked)


def _get_client():
    """Return a ``MongoClient`` instance or ``None`` if connection fails.
    The client is cached in the module‑level ``_client`` variable.
    """
    global _client
    if _client is not None:
        return _client
    try:
        from pymongo import MongoClient
        uri = getattr(settings, "MONGO_URI", "mongodb://localhost:27017/")
        _client = MongoClient(uri, serverSelectionTimeoutMS=1500)
        return _client
    except Exception as exc:  # pragma: no cover – very unlikely in normal dev env
        logger.warning("Unable to create MongoClient: %s", exc)
        return None


def get_db():
    """Return the ``Database`` object or ``None`` if MongoDB is unreachable.
    The first successful call caches the connection status in ``_mongo_online``.
    """
    global _db, _mongo_online
    if _mongo_online is True:
        return _db
    if _mongo_online is False:
        return None

    client = _get_client()
    if client is None:
        _mongo_online = False
        return None
    try:
        # ``ping`` forces a round‑trip; if it raises we treat Mongo as offline.
        client.admin.command("ping")
        db_name = getattr(settings, "MONGO_DB_NAME", "ngo_portal")
        _db = client[db_name]
        _mongo_online = True
        logger.info("Connected to MongoDB database %s", db_name)
        return _db
    except Exception as exc:
        _mongo_online = False
        logger.warning("MongoDB ping failed – falling back to in‑memory store: %s", exc)
        return None


def is_mongo_online() -> bool:
    """Convenient flag used by templates/context processors.
    Calls ``get_db()`` to ensure the connection attempt has been made.
    """
    get_db()
    return bool(_mongo_online)

# ---------------------------------------------------------------------------
# In‑memory fallback structures – used only when MongoDB is not reachable.
# ---------------------------------------------------------------------------
_fallback: Dict[str, List[Dict[str, Any]]] = {
    "operations_logs": [],
    "volunteer_feedback": [],
    "emergency_dispatches": [],
}

# ---------------------------------------------------------------------------
# Validation helpers
# ---------------------------------------------------------------------------
def _validate_required_str(value: Any, field_name: str) -> Optional[str]:
    if not isinstance(value, str) or not value.strip():
        return f"{field_name} must be a non‑empty string"
    return None

def _validate_operation_log(data: Dict[str, Any]) -> List[str]:
    errors = []
    for field in ("event_type", "description"):
        err = _validate_required_str(data.get(field), field)
        if err:
            errors.append(err)
    if "performed_by" in data and not isinstance(data["performed_by"], str):
        errors.append("performed_by must be a string")
    if "metadata" in data and not isinstance(data["metadata"], dict):
        errors.append("metadata must be a JSON object (dict)")
    return errors

def _validate_feedback(data: Dict[str, Any]) -> List[str]:
    errors = []
    for field in ("volunteer", "campaign", "feedback"):
        err = _validate_required_str(data.get(field), field)
        if err:
            errors.append(err)
    rating = data.get("rating")
    if rating is not None and not (isinstance(rating, int) and 0 <= rating <= 5):
        errors.append("rating must be an integer between 0 and 5")
    return errors

def _validate_dispatch(data: Dict[str, Any]) -> List[str]:
    errors = []
    for field in ("dispatcher", "location", "resource_type"):
        err = _validate_required_str(data.get(field), field)
        if err:
            errors.append(err)
    count = data.get("count")
    if not isinstance(count, int) or count <= 0:
        errors.append("count must be a positive integer")
    return errors

# ---------------------------------------------------------------------------
# Generic CRUD helpers – used internally by the concrete collections.
# ---------------------------------------------------------------------------
def _insert_one(collection: str, doc: Dict[str, Any]) -> str:
    db = get_db()
    if db is not None:
        result = db[collection].insert_one(doc)
        return str(result.inserted_id)
    # fallback – generate a UUID that mimics an ObjectId
    doc_id = str(uuid.uuid4())
    doc_copy = {**doc, "_id": doc_id}
    _fallback[collection].insert(0, doc_copy)
    return doc_id

def _find_one(collection: str, _id: str) -> Optional[Dict[str, Any]]:
    db = get_db()
    if db is not None:
        from bson import ObjectId
        try:
            oid = ObjectId(_id)
        except Exception:
            return None
        doc = db[collection].find_one({"_id": oid}, {"_id": 0})
        return doc
    for entry in _fallback[collection]:
        if entry.get("_id") == _id:
            return {k: v for k, v in entry.items() if k != "_id"}
    return None

def _update_one(collection: str, _id: str, updates: Dict[str, Any]) -> bool:
    db = get_db()
    if db is not None:
        from bson import ObjectId
        try:
            oid = ObjectId(_id)
        except Exception:
            return False
        result = db[collection].update_one({"_id": oid}, {"$set": updates})
        return result.modified_count > 0
    for i, entry in enumerate(_fallback[collection]):
        if entry.get("_id") == _id:
            _fallback[collection][i] = {**entry, **updates}
            return True
    return False

def _delete_one(collection: str, _id: str) -> bool:
    db = get_db()
    if db is not None:
        from bson import ObjectId
        try:
            oid = ObjectId(_id)
        except Exception:
            return False
        result = db[collection].delete_one({"_id": oid})
        return result.deleted_count > 0
    before = len(_fallback[collection])
    _fallback[collection] = [e for e in _fallback[collection] if e.get("_id") != _id]
    return len(_fallback[collection]) < before

# ---------------------------------------------------------------------------
# Operations Log CRUD (with validation)
# ---------------------------------------------------------------------------
def create_operation_log(event_type: str, description: str, performed_by: str = "system", metadata: Optional[Dict] = None) -> str:
    payload = {
        "event_type": event_type,
        "description": description,
        "performed_by": performed_by,
        "metadata": metadata or {},
        "timestamp": datetime.utcnow(),
    }
    errs = _validate_operation_log(payload)
    if errs:
        raise ValueError("Invalid operation-log data: " + "; ".join(errs))
    return _insert_one("operations_logs", payload)

def get_operation_log(log_id: str) -> Optional[Dict[str, Any]]:
    return _find_one("operations_logs", log_id)

def update_operation_log(log_id: str, updates: Dict[str, Any]) -> bool:
    # Only allow known fields to be updated
    allowed = {"event_type", "description", "performed_by", "metadata"}
    unknown = set(updates) - allowed
    if unknown:
        raise ValueError(f"Invalid fields for update: {unknown}")
    # Merge with existing data for full validation
    existing = get_operation_log(log_id)
    if not existing:
        return False
    combined = {**existing, **updates}
    errs = _validate_operation_log(combined)
    if errs:
        raise ValueError("Invalid update payload: " + "; ".join(errs))
    return _update_one("operations_logs", log_id, updates)

def delete_operation_log(log_id: str) -> bool:
    return _delete_one("operations_logs", log_id)

def list_operation_logs(limit: int = 20) -> List[Dict[str, Any]]:
    db = get_db()
    if db is not None:
        cursor = db["operations_logs"].find({}, {"_id": 0}).sort("timestamp", -1).limit(limit)
        return list(cursor)
    return _fallback["operations_logs"][:limit]

# ---------------------------------------------------------------------------
# Volunteer Feedback CRUD (with validation)
# ---------------------------------------------------------------------------
def create_feedback(volunteer: str, campaign: str, feedback: str, rating: int = 0) -> str:
    payload = {
        "volunteer": volunteer,
        "campaign": campaign,
        "feedback": feedback,
        "rating": rating,
        "submitted_at": datetime.utcnow(),
    }
    errs = _validate_feedback(payload)
    if errs:
        raise ValueError("Invalid feedback data: " + "; ".join(errs))
    return _insert_one("volunteer_feedback", payload)

def list_feedback(campaign: Optional[str] = None, limit: int = 50) -> List[Dict[str, Any]]:
    db = get_db()
    query = {"campaign": campaign} if campaign else {}
    if db is not None:
        cursor = db["volunteer_feedback"].find(query, {"_id": 0}).sort("submitted_at", -1).limit(limit)
        return list(cursor)
    data = _fallback["volunteer_feedback"]
    if campaign:
        data = [f for f in data if f.get("campaign") == campaign]
    return data[:limit]

# ---------------------------------------------------------------------------
# Emergency Dispatch CRUD (with validation)
# ---------------------------------------------------------------------------
def create_dispatch(dispatcher: str, location: str, resource_type: str, count: int, notes: str = "", campaign: str = "") -> str:
    payload = {
        "dispatcher": dispatcher,
        "campaign": campaign,
        "location": location,
        "resource_type": resource_type,
        "count": count,
        "notes": notes,
        "status": "DISPATCHED",
        "dispatched_at": datetime.utcnow(),
    }
    errs = _validate_dispatch(payload)
    if errs:
        raise ValueError("Invalid dispatch data: " + "; ".join(errs))
    return _insert_one("emergency_dispatches", payload)

def list_dispatches(limit: int = 30) -> List[Dict[str, Any]]:
    db = get_db()
    if db is not None:
        cursor = db["emergency_dispatches"].find({}, {"_id": 0}).sort("dispatched_at", -1).limit(limit)
        return list(cursor)
    return _fallback["emergency_dispatches"][:limit]

# ---------------------------------------------------------------------------
# Summary statistics – displayed on the Operations Dashboard.
# ---------------------------------------------------------------------------
def get_mongo_summary_stats() -> Dict[str, Any]:
    stats = {
        "ops_log_count": 0,
        "feedback_count": 0,
        "dispatch_count": 0,
        "mongo_online": is_mongo_online(),
    }
    db = get_db()
    if db is not None:
        try:
            stats["ops_log_count"] = db["operations_logs"].count_documents({})
            stats["feedback_count"] = db["volunteer_feedback"].count_documents({})
            stats["dispatch_count"] = db["emergency_dispatches"].count_documents({})
        except Exception:
            pass
    else:
        stats["ops_log_count"] = len(_fallback["operations_logs"])
        stats["feedback_count"] = len(_fallback["volunteer_feedback"])
        stats["dispatch_count"] = len(_fallback["emergency_dispatches"])
    return stats


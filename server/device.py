import time
import uuid
from typing import Any, Dict, List, Optional

from db_init import db_connect, Device, Report
from utils import generate_access_code, generate_token
from datetime import datetime


def _ensure_uuid(val: Any) -> uuid.UUID:
    if isinstance(val, uuid.UUID):
        return val
    return uuid.UUID(str(val))


def _device_to_dict(device: Device) -> Dict[str, Any]:
    return {
        "id": str(device.id),
        "name": device.name,
        "last_online": device.last_online.isoformat() if device.last_online else None,
        "last_session_time": device.last_session_time,
    }


def _report_to_dict(report: Report) -> Dict[str, Any]:
    return {
        "id": str(report.id),
        "device_id": str(report.device.id) if report.device else None,
        "timestamp": report.timestamp.isoformat() if report.timestamp else None,
        "reason": report.reason,
        "message": report.message,
        "screen_shot_id": report.screen_shot_id,
        "data": report.data,
    }


class Devices:
    def __init__(self, db=None):
        # db param for backwards compatibility; we prefer to use peewee models
        self._db = db_connect() if db is None else db
        self.devices: Dict[str, Dict[str, Any]] = {}  # token -> session info
        self.online: Dict[str, str] = {}  # device_id(str) -> token

    def create_device(self, name: str) -> Dict[str, str]:
        access_code = generate_access_code()
        d = Device.create(name=name, access_code=access_code)
        return {"id": str(d.id), "access_code": access_code}

    def remove_device(self, device_id: str) -> bool:
        try:
            did = _ensure_uuid(device_id)
            deleted = Device.delete().where(Device.id == did).execute()
            # If online, forget session
            token = self.online.get(str(did))
            if token:
                self.forget(token)
            return deleted > 0
        except Exception:
            return False

    def edit_device(self, device_id: str, name: Optional[str] = None) -> bool:
        try:
            did = _ensure_uuid(device_id)
            d = Device.get_or_none(Device.id == did)
            if not d:
                return False
            if name is not None:
                d.name = name
            d.save()
            # update cached session device if present
            token = self.online.get(str(did))
            if token and token in self.devices:
                self.devices[token]["device_id"] = str(d.id)
            return True
        except Exception:
            return False

    def get_device(self, device_id: str) -> Optional[Dict[str, Any]]:
        try:
            did = _ensure_uuid(device_id)
            d = Device.get_or_none(Device.id == did)
            if not d:
                return None
            reports = (
                Report.select()
                .where(Report.device == d)
                .order_by(Report.timestamp.desc())
            )
            return {"device": _device_to_dict(d), "reports": [_report_to_dict(r) for r in reports]}
        except Exception:
            return None

    def get_all_devices(self) -> List[Dict[str, Any]]:
        devices = Device.select().order_by(Device.last_online.desc())
        out: List[Dict[str, Any]] = []
        for d in devices:
            dd = _device_to_dict(d)
            dd["is_online"] = str(d.id) in self.online
            out.append(dd)
        return out

    def authenticate(self, ws, access_code: str) -> Optional[str]:
        d = Device.get_or_none(Device.access_code == access_code)
        if not d:
            return None
        token = generate_token()
        # store minimal session info
        self.devices[token] = {"session": ws, "timestamp": time.time(), "device_id": str(d.id)}
        self.online[str(d.id)] = token
        return token

    def forget(self, token: str) -> bool:
        if token in self.devices:
            device_id = self.devices[token].get("device_id")
            if device_id and device_id in self.online:
                del self.online[device_id]
            del self.devices[token]
            try:
                # try to recover session timestamp if still available; otherwise use now
                sess = self.devices.get(token)
                ts = sess.get("timestamp") if sess and "timestamp" in sess else time.time()
                session_len = int(time.time() - ts) if sess and "timestamp" in sess else 0

                if device_id:
                    try:
                        did = _ensure_uuid(device_id)
                        d = Device.get_or_none(Device.id == did)
                        if d:
                            d.last_online = datetime.fromtimestamp(ts)
                            d.last_session_time = session_len
                            d.save()
                    except Exception:
                        pass
            except Exception:
                pass
        return True


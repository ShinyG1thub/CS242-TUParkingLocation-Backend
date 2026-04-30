"""Business logic using SQLAlchemy models.

This layer handles database interactions and cleanly returns 
standardized dictionaries to the API controller, now structured
within a ParkingManager class as defined by the UML.
"""
from typing import List, Optional, TypedDict
import json

from ..extensions import db
from ..models.parking import ParkingArea, ParkingSlot


class ParkingAreaDict:
    """Class representing parking area data for API transfer."""
    def __init__(self, **kwargs):
        self._id = kwargs.get('id')
        self._name = kwargs.get('name')
        self._address = kwargs.get('address')
        self._latitude = kwargs.get('latitude')
        self._longitude = kwargs.get('longitude')
        self._allowed_types = kwargs.get('allowed_types', [])
        self._total_slots = kwargs.get('total_slots', 0)
        self._available_slots = kwargs.get('available_slots', 0)
        self._unavailable_slots = kwargs.get('unavailable_slots', 0)

    @property
    def id(self): return self._id

    def to_dict(self):
        """Complex logic: Convert object state to a standardized dictionary."""
        return {
            "id": self._id,
            "name": self._name,
            "address": self._address,
            "latitude": self._latitude,
            "longitude": self._longitude,
            "allowed_types": self._allowed_types,
            "total_slots": self._total_slots,
            "available_slots": self._available_slots,
            "unavailable_slots": self._unavailable_slots,
        }


class ParkingSlotDict:
    """Class representing parking slot data for API transfer."""
    def __init__(self, **kwargs):
        self._id = kwargs.get('id')
        self._area_id = kwargs.get('area_id')
        self._name = kwargs.get('name')
        self._status = kwargs.get('status')

    def to_dict(self):
        """Complex logic: Format slot data with status-specific decorations."""
        return {
            "id": self._id,
            "area_id": self._area_id,
            "name": self._name,
            "status": self._status.lower() if self._status else "unknown"
        }


class ParkingManager:
    """Manages all interactions with Parking database models."""

    def __init__(self, db_name: str = "sqlite:///tu_parking.db"):
        self._db_name = db_name

    @property
    def db_name(self):
        return self._db_name
    
    @db_name.setter
    def db_name(self, value):
        self._db_name = value

    # Complex logic method for the manager
    def generate_occupancy_report(self) -> dict:
        """Aggregates occupancy data across all areas into a complex report."""
        areas = ParkingArea.query.all()
        total_slots = sum(a.total_slots for a in areas)
        total_available = sum(a.available_slots_db for a in areas)
        
        return {
            "summary": {
                "total_areas": len(areas),
                "global_total_slots": total_slots,
                "global_available": total_available,
                "occupancy_rate": (total_slots - total_available) / total_slots if total_slots > 0 else 0
            },
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

    def get_all_parking_areas(self) -> List[dict]:
        """Retrieve all parking areas with calculated slot bounds."""
        areas: List[ParkingArea] = ParkingArea.query.all()
        results = []
        for area in areas:
            data = ParkingAreaDict(
                id=area.id,
                name=area.name,
                address=area.address,
                latitude=area.latitude,
                longitude=area.longitude,
                allowed_types=area.get_allowed_types_list(),
                total_slots=area.total_slots,
                available_slots=area.available_slots_db,
                unavailable_slots=area.unavailable_slots,
            )
            results.append(data.to_dict())
        return results

    def get_parking_area_by_id(self, area_id: int) -> Optional[dict]:
        """Retrieve a single parking area by its ID."""
        area: Optional[ParkingArea] = ParkingArea.query.get(area_id)
        if not area:
            return None
        data = ParkingAreaDict(
            id=area.id,
            name=area.name,
            address=area.address,
            latitude=area.latitude,
            longitude=area.longitude,
            allowed_types=area.get_allowed_types_list(),
            total_slots=area.total_slots,
            available_slots=area.available_slots_db,
            unavailable_slots=area.unavailable_slots,
        )
        return data.to_dict()

    def get_parking_slots(self, area_id: int) -> List[dict]:
        """Retrieve all slots belonging to a specific parking area."""
        slots: List[ParkingSlot] = ParkingSlot.query.filter_by(area_id=area_id).order_by(ParkingSlot._name).all()
        results = []
        for s in slots:
            data = ParkingSlotDict(
                id=s.id,
                area_id=s.area_id,
                name=s.name,
                status=s.status
            )
            results.append(data.to_dict())
        return results

    # UML Required Methods
    def add_parking_area(self, name: str, total_slots: int, address: str = None, lat: float = None, lon: float = None) -> ParkingArea:
        area = ParkingArea(name=name, address=address, latitude=lat, longitude=lon, total_slots=total_slots, available_slots_db=total_slots)
        db.session.add(area)
        db.session.commit()
        return area

    def add_parking_slot(self, area_id: int, name: str, status: str = 'available') -> ParkingSlot:
        slot = ParkingSlot(area_id=area_id, name=name, status=status)
        db.session.add(slot)
        db.session.commit()
        return slot

    def update_slot(self, slot_id: int, new_status: str) -> bool:
        slot = ParkingSlot.query.get(slot_id)
        if slot:
            slot.update_status(new_status)
            db.session.commit()
            return True
        return False

    def delete_slot(self, slot_id: int) -> bool:
        slot = ParkingSlot.query.get(slot_id)
        if slot:
            db.session.delete(slot)
            db.session.commit()
            return True
        return False

    def get_all_slots_json(self) -> str:
        """Returns JSON representation of all slots."""
        slots: List[ParkingSlot] = ParkingSlot.query.all()
        slots_list = [{"id": s.id, "area_id": s.area_id, "name": s.name, "status": s.status} for s in slots]
        return json.dumps(slots_list)

# Instantiate the singleton manager for routes to use
parking_manager = ParkingManager()
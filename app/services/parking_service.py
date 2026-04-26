"""Business logic using SQLAlchemy models.

This layer handles database interactions and cleanly returns 
standardized dictionaries to the API controller, now structured
within a ParkingManager class as defined by the UML.
"""
from typing import List, Optional, TypedDict
import json

from ..extensions import db
from ..models.parking import ParkingArea, ParkingSlot


class ParkingAreaDict(TypedDict):
    id: int
    name: str
    address: Optional[str]
    latitude: Optional[float]
    longitude: Optional[float]
    total_slots: int
    available_slots: int
    unavailable_slots: int


class ParkingSlotDict(TypedDict):
    id: int
    area_id: int
    name: str
    status: str


class ParkingManager:
    """Manages all interactions with Parking database models."""

    def __init__(self, db_name: str = "sqlite:///tu_parking.db"):
        self.db_name = db_name

    def get_all_parking_areas(self) -> List[ParkingAreaDict]:
        """Retrieve all parking areas with calculated slot bounds."""
        areas: List[ParkingArea] = ParkingArea.query.all()
        return [
            {
                "id": area.id,
                "name": area.name,
                "address": area.address,
                "latitude": area.latitude,
                "longitude": area.longitude,
                "total_slots": area.total_slots,
                "available_slots": area.available_slots_db,
                "unavailable_slots": area.unavailable_slots,
            }
            for area in areas
        ]

    def get_parking_area_by_id(self, area_id: int) -> Optional[ParkingAreaDict]:
        """Retrieve a single parking area by its ID."""
        area: Optional[ParkingArea] = ParkingArea.query.get(area_id)
        if not area:
            return None
        return {
            "id": area.id,
            "name": area.name,
            "address": area.address,
            "latitude": area.latitude,
            "longitude": area.longitude,
            "total_slots": area.total_slots,
            "available_slots": area.available_slots_db,
            "unavailable_slots": area.unavailable_slots,
        }

    def get_parking_slots(self, area_id: int) -> List[ParkingSlotDict]:
        """Retrieve all slots belonging to a specific parking area."""
        slots: List[ParkingSlot] = ParkingSlot.query.filter_by(area_id=area_id).order_by(ParkingSlot.name).all()
        return [
            {
                "id": s.id,
                "area_id": s.area_id,
                "name": s.name,
                "status": s.status,
            }
            for s in slots
        ]

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
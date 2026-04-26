"""SQLAlchemy models for parking areas and slots."""

from datetime import datetime, timezone
from ..extensions import db


class ParkingArea(db.Model):
    __tablename__ = 'parking_areas'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    address = db.Column(db.String(255), nullable=True)
    latitude = db.Column(db.Float, nullable=True)
    longitude = db.Column(db.Float, nullable=True)
    allowed_types = db.Column(db.String(50), nullable=False, default="staff,general")  # comma-separated: staff,general,disabled
    total_slots = db.Column(db.Integer, nullable=False)
    available_slots_db = db.Column('available_slots', db.Integer, nullable=False) # Keep mapped for legacy code but use method for UML

    # Relationship to slots (one-to-many)
    slots = db.relationship('ParkingSlot', backref='area', lazy=True)

    @property
    def unavailable_slots(self):
        return self.total_slots - self.available_slots_db

    def get_allowed_types_list(self) -> list:
        """แปลง 'staff,general' -> ['staff', 'general']"""
        return [t.strip() for t in self.allowed_types.split(",") if t.strip()]

    def is_full(self, occupied_count: int) -> bool:
        """UML Method: Check if the parking area is full given an occupied count."""
        return occupied_count >= self.total_slots

    def available_slots(self, occupied_count: int) -> int:
        """UML Method: Calculate available slots based on an occupied count."""
        return max(0, self.total_slots - occupied_count)


class ParkingSlot(db.Model):
    __tablename__ = 'parking_slots'

    id = db.Column(db.Integer, primary_key=True)
    area_id = db.Column(db.Integer, db.ForeignKey('parking_areas.id'), nullable=False)
    name = db.Column(db.String(20), nullable=False)
    status = db.Column(db.String(20), nullable=False, default='available')  # 'available' or 'occupied'
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    def is_available(self) -> bool:
        """UML Method: Check if this slot is available."""
        return self.status == 'available'

    def update_status(self, new_status: str):
        """UML Method: Safely update the slot status."""
        valid_statuses = ['available', 'occupied', 'maintenance']
        if new_status in valid_statuses:
            self.status = new_status
        else:
            raise ValueError(f"Invalid status: {new_status}")
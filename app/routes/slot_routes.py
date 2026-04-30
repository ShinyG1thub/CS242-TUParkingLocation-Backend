from typing import Tuple

from flask import Blueprint, Response, jsonify, request

from ..extensions import db
from ..models.parking import ParkingArea, ParkingSlot
from ..services.parking_service import parking_manager

slot_bp = Blueprint("slot", __name__)

def _get_area_or_404(
    area_id: int,
) -> Tuple[ParkingArea | None, Tuple[Response, int] | None]:
    area = ParkingArea.query.get(area_id)
    if not area:
        return None, (jsonify({"error": "Parking area not found"}), 404)
    return area, None


def _refresh_area_available_slots(area: ParkingArea) -> None:
    area.available_slots_db = ParkingSlot.query.filter_by(
        area_id=area.id,
        _status="available",
    ).count()

@slot_bp.route("/api/parking/areas/<int:area_id>/slots", methods=["GET"])
def api_parking_slots(area_id: int) -> Tuple[Response, int] | Response:
    """Return all slots for a parking area."""
    _, error_response = _get_area_or_404(area_id)
    if error_response:
        return error_response
    return jsonify(parking_manager.get_parking_slots(area_id))

@slot_bp.route("/api/parking/areas/<int:area_id>/update", methods=["POST"])
def update_parking_available(area_id: int) -> Tuple[Response, int] | Response:
    """Update available slots for a parking area."""
    try:
        data = request.get_json(silent=True) or {}
        available_slots = data.get("available_slots")

        area, error_response = _get_area_or_404(area_id)
        if error_response:
            return error_response

        if not isinstance(available_slots, int):
            return jsonify({"error": "available_slots must be an integer"}), 400
        if available_slots < 0 or available_slots > area.total_slots:
            return (
                jsonify(
                    {
                        "error": f"available_slots must be between 0 and {area.total_slots}"
                    }
                ),
                400,
            )

        ordered_slots = (
            ParkingSlot.query.filter_by(area_id=area_id).order_by(ParkingSlot._name).all()
        )
        for index, slot in enumerate(ordered_slots, start=1):
            slot.status = "available" if index <= available_slots else "occupied"

        _refresh_area_available_slots(area)
        db.session.commit()

        return (
            jsonify(
                {
                    "message": f"Updated {area.name}: {available_slots} slots available",
                    "area": parking_manager.get_parking_area_by_id(area_id),
                    "slots": parking_manager.get_parking_slots(area_id),
                }
            ),
            200,
        )
    except Exception as exc:
        db.session.rollback()
        return jsonify({"error": str(exc)}), 400
    
@slot_bp.route("/api/parking/areas/<int:area_id>/slots/<int:slot_id>", methods=["POST"])
def update_slot_status(area_id: int, slot_id: int) -> Tuple[Response, int] | Response:
    """Update the status of a specific parking slot."""
    try:
        data = request.get_json(silent=True) or {}
        new_status = data.get("status")
        valid_statuses = {"available", "occupied", "maintenance"}

        if new_status not in valid_statuses:
            return (
                jsonify(
                    {
                        "error": "Invalid status. Must be: available, occupied, or maintenance"
                    }
                ),
                400,
            )

        area, error_response = _get_area_or_404(area_id)
        if error_response:
            return error_response

        slot = ParkingSlot.query.get(slot_id)
        if not slot or slot.area_id != area_id:
            return jsonify({"error": "Slot not found"}), 404

        old_status = slot.status
        slot.update_status(new_status)
        _refresh_area_available_slots(area)
        db.session.commit()

        return (
            jsonify(
                {
                    "message": f"Slot {slot.name}: {old_status} -> {new_status}",
                    "slot": {
                        "id": slot.id,
                        "name": slot.name,
                        "status": slot.status,
                    },
                    "area": parking_manager.get_parking_area_by_id(area_id),
                    "slots": parking_manager.get_parking_slots(area_id),
                }
            ),
            200,
        )
    except Exception as exc:
        db.session.rollback()
        return jsonify({"error": str(exc)}), 400
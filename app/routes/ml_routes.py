from typing import Tuple
from flask import Blueprint, Response, jsonify, request

from ..extensions import db
from ..models.parking import ParkingArea
from ..services.parking_service import parking_manager

ml_bp = Blueprint("ml", __name__)


def _get_area_or_404(area_id: int):
    area = ParkingArea.query.get(area_id)
    if not area:
        return None, (jsonify({"error": "Parking area not found"}), 404)
    return area, None


def _parse_bool(value: str | None) -> bool:
    if value is None:
        return False
    return value.strip().lower() in {"1", "true", "yes", "on"}


@ml_bp.route("/api/parking/areas/<int:area_id>/ml-image-detect", methods=["POST"])
def ml_detect_area_from_image(area_id: int):
    try:
        area, error_response = _get_area_or_404(area_id)
        if error_response:
            return error_response

        uploaded_file = request.files.get("image")

        if not uploaded_file or not uploaded_file.filename:
            return jsonify({"error": "image file is required"}), 400

        image_bytes = uploaded_file.read()

        if not image_bytes:
            return jsonify({"error": "uploaded image is empty"}), 400

        from ML.services.parking_image_detector import parking_image_detector

        result = parking_image_detector.analyze(image_bytes)

        apply_to_area = _parse_bool(request.form.get("apply_to_area"))

        sync_summary = {
            "applied": False,
            "synced_slots": 0
        }

        # 🔥 ย้าย logic ไป service
        if apply_to_area:
            analyzed_slots = result["slot_results"]

            sync_summary = parking_manager.sync_slots_from_ml(
                area_id,
                analyzed_slots
            )

        return jsonify({
            "area": parking_manager.get_parking_area_by_id(area_id),
            "db_slots": parking_manager.get_parking_slots(area_id),
            "ml_result": result,
            "sync": sync_summary
        }), 200

    except Exception as exc:
        db.session.rollback()
        return jsonify({"error": str(exc)}), 400
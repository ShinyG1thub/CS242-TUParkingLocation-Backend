from typing import Tuple
from flask import Blueprint, Response, jsonify, request

from ..extensions import db
from ..models.parking import ParkingArea
from ..services.parking_service import parking_manager
from ..models.parking import ParkingArea, ParkingSlot

ml_bp = Blueprint("ml", __name__)

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
        status="available",
    ).count()
    
def _parse_bool(value: str | None) -> bool:
    if value is None:
        return False
    return value.strip().lower() in {"1", "true", "yes", "on"}

@ml_bp.route("/api/parking/areas/<int:area_id>/ml-predict", methods=["POST"])
def ml_predict_area(area_id: int) -> Tuple[Response, int] | Response:
    """Return a simple ML-style status prediction for a parking area."""
    try:
        from ..services.ml_manager import MLManager
        from ML.utils.data_preparer import DataPreparer

        area, error_response = _get_area_or_404(area_id)
        if error_response:
            return error_response

        ml_manager = MLManager()

        active_model = ml_manager.get_active_model()
        if not active_model:
            model = ml_manager.add_ml_model(
                name="default_model_v1",
                model_type="Status-Based",
                version="1.0.0",
                file_path="ML/models/default.pkl",
                description="Default status-based model",
            )
            ml_manager.set_active_model(model.id)
            active_model = ml_manager.get_active_model()

        features = DataPreparer().get_parking_area_features(area_id)
        occupancy_rate = features.get("occupancy_rate", 0.0)

        if occupancy_rate > 0.9:
            prediction = "very_full"
            confidence = 0.95
        elif occupancy_rate > 0.75:
            prediction = "likely_full"
            confidence = 0.85
        elif occupancy_rate > 0.5:
            prediction = "moderate"
            confidence = 0.80
        elif occupancy_rate > 0.2:
            prediction = "available"
            confidence = 0.85
        else:
            prediction = "very_available"
            confidence = 0.90

        ml_manager.add_prediction(
            model_id=active_model["id"],
            parking_area_id=area_id,
            prediction_value=prediction,
            confidence_score=confidence,
            predicted_available_slots=features.get("available_slots"),
            input_features=features,
        )

        return (
            jsonify(
                {
                    "area_id": area_id,
                    "area_name": area.name,
                    "prediction": prediction,
                    "confidence": confidence,
                    "occupancy_rate": f"{occupancy_rate:.1%}",
                    "available_slots": features.get("available_slots"),
                    "total_slots": features.get("total_slots"),
                    "model": active_model["name"],
                }
            ),
            200,
        )
    except Exception as exc:
        db.session.rollback()
        return jsonify({"error": str(exc)}), 400


@ml_bp.route("/api/parking/areas/<int:area_id>/ml-image-detect", methods=["POST"])
def ml_detect_area_from_image(area_id: int) -> Tuple[Response, int] | Response:
    """Analyze an uploaded image and optionally sync the result to DB."""
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
            "synced_slots": 0,
        }

        if apply_to_area:
            ordered_slots = (
                ParkingSlot.query.filter_by(area_id=area_id).order_by(ParkingSlot.name).all()
            )
            analyzed_slots = result["slot_results"]

            for index, db_slot in enumerate(ordered_slots):
                if index < len(analyzed_slots):
                    db_slot.status = analyzed_slots[index]["status"]
                else:
                    db_slot.status = "maintenance"

            _refresh_area_available_slots(area)
            db.session.commit()

            sync_summary = {
                "applied": True,
                "synced_slots": min(len(ordered_slots), len(analyzed_slots)),
                "remaining_slots_marked_maintenance": max(0, len(ordered_slots) - len(analyzed_slots)),
            }

        return (
            jsonify(
                {
                    "area": parking_manager.get_parking_area_by_id(area_id),
                    "db_slots": parking_manager.get_parking_slots(area_id),
                    "ml_result": result,
                    "sync": sync_summary,
                }
            ),
            200,
        )
    except Exception as exc:
        db.session.rollback()
        return jsonify({"error": str(exc)}), 400
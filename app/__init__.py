"""TUparkingLocation - Flask Application Factory"""

from flask import Flask
from flask_cors import CORS
from .extensions import db
from .routes.parking_routes import parking_bp
from .routes.slot_routes import slot_bp
from .routes.ml_routes import ml_bp
from .models.parking import ParkingArea, ParkingSlot
from .models.ml_models import MLModel, Prediction, TrainingHistory


def create_app():
    app = Flask(__name__)
    CORS(app)  # Enable CORS for Vite frontend
    
    # SQLite Database Configuration
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///tu_parking.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # Initialize SQLAlchemy
    db.init_app(app)

    # Create tables and seed data
    with app.app_context():
        db.create_all()
        seed_mock_data()
        ensure_demo_defaults()

    # Register routes
    app.register_blueprint(parking_bp)
    app.register_blueprint(slot_bp)
    app.register_blueprint(ml_bp)
    
    return app


def seed_mock_data():
    """Seed mock Thammasat University parking data"""
    if ParkingArea.query.count() > 0:
        return

    print("🌱 Seeding mock parking data for TUparkingLocation...")

    areas_data = [
        {"name": "GYM 7",       "lat": 14.0754, "lon": 100.6041, "total_slots": 60,  "available_slots": 2, "address": "Tambon Khlong Nueng, Amphoe Khlong Luang, Pathum Thani 12120"},
        {"name": "Parking 1",   "lat": 14.0700, "lon": 100.6000, "total_slots": 120, "available_slots": 8, "address": "99 Moo 18 Paholyothin Road, Khlong Nueng"},
        {"name": "Parking 2",   "lat": 14.0680, "lon": 100.6050, "total_slots": 80,  "available_slots": 35, "address": "TU Main Library Zone, Pathum Thani 12120"},
        {"name": "Parking 3",   "lat": 14.0720, "lon": 100.6090, "total_slots": 45,  "available_slots": 12, "address": "Faculty of Engineering, Thammasat University"},
        {"name": "Parking 4",   "lat": 14.0650, "lon": 100.6100, "total_slots": 90,  "available_slots": 67, "address": "SC Building Zone, Rangsit Campus"},
    ]

    for data in areas_data:
        area = ParkingArea(
            name=data["name"],
            address=data["address"],
            latitude=data["lat"],
            longitude=data["lon"],
            total_slots=data["total_slots"],
            available_slots_db=data["available_slots"]
        )
        db.session.add(area)
        db.session.flush()                     # Get ID for slots

        # Create slots
        for i in range(1, data["total_slots"] + 1):
            status = "available" if i <= data["available_slots"] else "occupied"
            slot = ParkingSlot(
                area_id=area.id,
                name=f"Slot-{i:02d}",
                status=status
            )
            db.session.add(slot)

    db.session.commit()
    print("✅ Mock data seeded successfully! Database is ready.")


def ensure_demo_defaults():
    """Keep demo data aligned with the current testing scenario."""
    gym7 = ParkingArea.query.filter(ParkingArea.name.in_(["GYM 7", "GYM-7"])).first()
    if not gym7:
        return

    target_available_slots = 2
    gym7.available_slots_db = target_available_slots

    ordered_slots = (
        ParkingSlot.query.filter_by(area_id=gym7.id)
        .order_by(ParkingSlot.name)
        .all()
    )
    for index, slot in enumerate(ordered_slots, start=1):
        slot.status = "available" if index <= target_available_slots else "occupied"

    db.session.commit()
"""SQLAlchemy models for ML operations and predictions."""

from datetime import datetime, timezone
from app.extensions import db


class MLModel(db.Model):
    """Stores metadata about trained ML models."""
    __tablename__ = 'ml_models'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    model_type = db.Column(db.String(50), nullable=False)  # e.g., 'RandomForest', 'Neural Network'
    version = db.Column(db.String(20), nullable=False)  # e.g., '1.0.0'
    file_path = db.Column(db.String(255), nullable=False)  # Path to saved model artifact
    accuracy = db.Column(db.Float, nullable=True)  # Model performance metric
    precision = db.Column(db.Float, nullable=True)  # Precision score
    recall = db.Column(db.Float, nullable=True)  # Recall score
    f1_score = db.Column(db.Float, nullable=True)  # F1 score
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), 
                          onupdate=lambda: datetime.now(timezone.utc))
    is_active = db.Column(db.Boolean, default=False)  # Current production model
    description = db.Column(db.Text, nullable=True)

    # Relationships
    predictions = db.relationship('Prediction', backref='model', lazy=True)
    training_history = db.relationship('TrainingHistory', backref='model', lazy=True)

    def __repr__(self):
        return f'<MLModel {self.name} v{self.version}>'


class Prediction(db.Model):
    """Stores prediction results linked to parking areas."""
    __tablename__ = 'predictions'

    id = db.Column(db.Integer, primary_key=True)
    model_id = db.Column(db.Integer, db.ForeignKey('ml_models.id'), nullable=False)
    parking_area_id = db.Column(db.Integer, db.ForeignKey('parking_areas.id'), nullable=False)
    
    # Prediction output
    prediction_value = db.Column(db.String(50), nullable=False)  # e.g., 'likely_full', 'available', 'moderate'
    confidence_score = db.Column(db.Float, nullable=False)  # 0.0 to 1.0
    predicted_available_slots = db.Column(db.Integer, nullable=True)
    
    # Input features used for prediction (stored as JSON string for flexibility)
    input_features = db.Column(db.Text, nullable=True)  # JSON string of features
    
    # Metadata
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    is_accurate = db.Column(db.Boolean, nullable=True)  # Validated against actual data later

    # Relationship to parking area
    parking_area = db.relationship('ParkingArea', backref='predictions')

    def __repr__(self):
        return f'<Prediction {self.parking_area_id}: {self.prediction_value} ({self.confidence_score}%)>'


class TrainingHistory(db.Model):
    """Records training sessions and performance metrics."""
    __tablename__ = 'training_history'

    id = db.Column(db.Integer, primary_key=True)
    model_id = db.Column(db.Integer, db.ForeignKey('ml_models.id'), nullable=False)
    
    # Training metadata
    training_start_time = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    training_end_time = db.Column(db.DateTime, nullable=True)
    training_duration_seconds = db.Column(db.Float, nullable=True)
    
    # Dataset info
    training_samples_count = db.Column(db.Integer, nullable=True)
    validation_split_ratio = db.Column(db.Float, default=0.2)
    
    # Performance metrics
    training_loss = db.Column(db.Float, nullable=True)
    validation_loss = db.Column(db.Float, nullable=True)
    training_accuracy = db.Column(db.Float, nullable=True)
    validation_accuracy = db.Column(db.Float, nullable=True)
    
    # Training status
    status = db.Column(db.String(20), default='in_progress')  # 'in_progress', 'completed', 'failed'
    error_message = db.Column(db.Text, nullable=True)  # If training failed
    
    notes = db.Column(db.Text, nullable=True)  # Additional notes or hyperparameters used

    def __repr__(self):
        return f'<TrainingHistory Model-{self.model_id}: {self.status}>'
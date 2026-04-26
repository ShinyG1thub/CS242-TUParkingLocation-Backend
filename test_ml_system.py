#!/usr/bin/env python3
"""
ML System Test Script for TU Parking System
à¸—à¸”à¸ªà¸­à¸šà¸à¸²à¸£à¸—à¸³à¸‡à¸²à¸™à¸‚à¸­à¸‡ ML integration à¸à¸±à¸š Database
"""

import sys
import json
from typing import Dict, Any

class MLSystemTester:
    """à¸—à¸”à¸ªà¸­à¸šà¸£à¸°à¸šà¸š ML"""
    
    def __init__(self):
        self.results = {
            'passed': [],
            'failed': [],
            'warnings': []
        }
    
    def test_ml_models_import(self) -> bool:
        """à¸—à¸”à¸ªà¸­à¸šà¸à¸²à¸£ import ML models"""
        print("\n" + "="*50)
        print("ðŸ“¦ TEST 1: Import ML Models")
        print("="*50)
        
        try:
            from app.models.ml_models import MLModel, Prediction, TrainingHistory
            print("âœ… Successfully imported MLModel")
            print("âœ… Successfully imported Prediction")
            print("âœ… Successfully imported TrainingHistory")
            self.results['passed'].append("ML models import")
            return True
        except ImportError as e:
            print(f"âŒ Failed to import ML models: {str(e)}")
            self.results['failed'].append(f"ML models import: {str(e)}")
            return False
    
    def test_ml_manager_import(self) -> bool:
        """à¸—à¸”à¸ªà¸­à¸šà¸à¸²à¸£ import MLManager"""
        print("\n" + "="*50)
        print("ðŸ“¦ TEST 2: Import MLManager Service")
        print("="*50)
        
        try:
            from app.services.ml_manager import MLManager
            print("âœ… Successfully imported MLManager")
            self.results['passed'].append("MLManager import")
            return True
        except ImportError as e:
            print(f"âŒ Failed to import MLManager: {str(e)}")
            self.results['failed'].append(f"MLManager import: {str(e)}")
            return False
    
    def test_data_preparer_import(self) -> bool:
        """à¸—à¸”à¸ªà¸­à¸šà¸à¸²à¸£ import DataPreparer"""
        print("\n" + "="*50)
        print("ðŸ“¦ TEST 3: Import DataPreparer Utility")
        print("="*50)
        
        try:
            from ML.utils.data_preparer import DataPreparer
            print("âœ… Successfully imported DataPreparer")
            self.results['passed'].append("DataPreparer import")
            return True
        except ImportError as e:
            print(f"âŒ Failed to import DataPreparer: {str(e)}")
            self.results['failed'].append(f"DataPreparer import: {str(e)}")
            return False
    
    def test_prediction_service_import(self) -> bool:
        """à¸—à¸”à¸ªà¸­à¸šà¸à¸²à¸£ import ParkingPredictionService"""
        print("\n" + "="*50)
        print("ðŸ“¦ TEST 4: Import ParkingPredictionService")
        print("="*50)
        
        try:
            from ML.services import ParkingPredictionService
            print("âœ… Successfully imported ParkingPredictionService")
            self.results['passed'].append("ParkingPredictionService import")
            return True
        except ImportError as e:
            print(f"âŒ Failed to import ParkingPredictionService: {str(e)}")
            self.results['failed'].append(f"ParkingPredictionService import: {str(e)}")
            return False
    
    def test_database_operations(self) -> bool:
        """à¸—à¸”à¸ªà¸­à¸š MLManager database operations"""
        print("\n" + "="*50)
        print("ðŸ’¾ TEST 5: MLManager Database Operations")
        print("="*50)
        
        try:
            from app import create_app
            from app.services.ml_manager import MLManager
            
            app = create_app()
            
            with app.app_context():
                ml_manager = MLManager()
                
                # Test 5a: Add model
                print("\n5a. Adding model to database...")
                model = ml_manager.add_ml_model(
                    name='TestModel_Integration',
                    model_type='RandomForest',
                    version='1.0.0',
                    file_path='ML/models/test_integration.pkl',
                    description='Integration test model',
                    accuracy=0.92,
                    precision=0.89,
                    recall=0.94,
                    f1_score=0.915
                )
                print(f"âœ… Model added: ID={model.id}, Name={model.name}")
                
                # Test 5b: Retrieve model
                print("\n5b. Retrieving model from database...")
                retrieved = ml_manager.get_ml_model_by_id(model.id)
                assert retrieved is not None, "Failed to retrieve model"
                assert retrieved['name'] == 'TestModel_Integration'
                print(f"âœ… Model retrieved: {retrieved['name']}")
                print(f"   - Accuracy: {retrieved['accuracy']}")
                print(f"   - F1 Score: {retrieved['f1_score']}")
                
                # Test 5c: Set active model
                print("\n5c. Setting model as active...")
                success = ml_manager.set_active_model(model.id)
                assert success, "Failed to set active model"
                active = ml_manager.get_active_model()
                assert active is not None
                print(f"âœ… Model set as active: {active['name']}")
                
                # Test 5d: Get all models
                print("\n5d. Retrieving all models...")
                all_models = ml_manager.get_all_ml_models()
                print(f"âœ… Retrieved {len(all_models)} model(s)")
                
                self.results['passed'].append("Database operations")
                return True
                
        except Exception as e:
            print(f"âŒ Test failed: {str(e)}")
            self.results['failed'].append(f"Database operations: {str(e)}")
            import traceback
            traceback.print_exc()
            return False
    
    def test_data_preparation(self) -> bool:
        """à¸—à¸”à¸ªà¸­à¸š DataPreparer"""
        print("\n" + "="*50)
        print("ðŸ”§ TEST 6: DataPreparer Functionality")
        print("="*50)
        
        try:
            from app import create_app
            from ML.utils.data_preparer import DataPreparer
            
            app = create_app()
            
            with app.app_context():
                preparer = DataPreparer()
                
                # Test 6a: Get features for one area
                print("\n6a. Extracting features for parking area...")
                features = preparer.get_parking_area_features(1)
                assert features, "Failed to get features"
                assert 'area_id' in features
                assert 'occupancy_rate' in features
                print(f"âœ… Features extracted for area: {features['name']}")
                print(f"   - Total slots: {features['total_slots']}")
                print(f"   - Available: {features['available_slots']}")
                print(f"   - Occupancy rate: {features['occupancy_rate']:.2%}")
                
                # Test 6b: Get all features
                print("\n6b. Extracting features for all areas...")
                all_features = preparer.get_all_areas_features()
                assert len(all_features) > 0
                print(f"âœ… Features extracted for {len(all_features)} areas")
                
                # Test 6c: Feature names
                print("\n6c. Getting feature names...")
                feature_names = preparer.get_feature_names()
                print(f"âœ… Feature names: {feature_names}")
                
                # Test 6d: Normalization
                print("\n6d. Normalizing features...")
                normalized = preparer.normalize_features(all_features)
                assert len(normalized) == len(all_features)
                print(f"âœ… Features normalized: {len(normalized)} samples")
                print(f"   Sample (Area 1 occupancy): {normalized[0]['occupancy_rate']:.4f}")
                
                self.results['passed'].append("Data preparation")
                return True
                
        except Exception as e:
            print(f"âŒ Test failed: {str(e)}")
            self.results['failed'].append(f"Data preparation: {str(e)}")
            import traceback
            traceback.print_exc()
            return False
    
    def test_predictions(self) -> bool:
        """à¸—à¸”à¸ªà¸­à¸š Prediction storage"""
        print("\n" + "="*50)
        print("ðŸŽ¯ TEST 7: Prediction Storage")
        print("="*50)
        
        try:
            from app import create_app
            from app.services.ml_manager import MLManager
            from ML.utils.data_preparer import DataPreparer
            
            app = create_app()
            
            with app.app_context():
                ml_manager = MLManager()
                preparer = DataPreparer()
                
                # Setup: Get active model or create one
                active_model = ml_manager.get_active_model()
                if not active_model:
                    model = ml_manager.add_ml_model(
                        name=f'TestModel_Pred_{id(object())}',
                        model_type='RandomForest',
                        version='1.0.0',
                        file_path='ML/models/test_pred.pkl'
                    )
                    ml_manager.set_active_model(model.id)
                    active_model = ml_manager.get_active_model()
                
                # Test 7a: Add prediction
                print("\n7a. Adding prediction to database...")
                features = preparer.get_parking_area_features(1)
                prediction = ml_manager.add_prediction(
                    model_id=active_model['id'],
                    parking_area_id=1,
                    prediction_value='moderate',
                    confidence_score=0.85,
                    predicted_available_slots=25,
                    input_features=features
                )
                print(f"âœ… Prediction added: ID={prediction.id}")
                print(f"   - Prediction: {prediction.prediction_value}")
                print(f"   - Confidence: {prediction.confidence_score}")
                
                # Test 7b: Get predictions by area
                print("\n7b. Retrieving predictions by area...")
                predictions = ml_manager.get_predictions_by_area(1, limit=5)
                print(f"âœ… Retrieved {len(predictions)} prediction(s) for area 1")
                
                # Test 7c: Mark prediction accuracy
                print("\n7c. Marking prediction accuracy...")
                success = ml_manager.mark_prediction_accuracy(prediction.id, is_accurate=True)
                assert success
                print(f"âœ… Prediction marked as accurate")
                
                self.results['passed'].append("Predictions")
                return True
                
        except Exception as e:
            print(f"âŒ Test failed: {str(e)}")
            self.results['failed'].append(f"Predictions: {str(e)}")
            import traceback
            traceback.print_exc()
            return False
    
    def test_training_history(self) -> bool:
        """à¸—à¸”à¸ªà¸­à¸š Training History"""
        print("\n" + "="*50)
        print("ðŸ“š TEST 8: Training History Management")
        print("="*50)
        
        try:
            from app import create_app
            from app.services.ml_manager import MLManager
            
            app = create_app()
            
            with app.app_context():
                ml_manager = MLManager()
                
                # Setup: Get or create model
                active_model = ml_manager.get_active_model()
                if not active_model:
                    model = ml_manager.add_ml_model(
                        name=f'TestModel_Train_{id(object())}',
                        model_type='RandomForest',
                        version='1.0.0',
                        file_path='ML/models/test_train.pkl'
                    )
                    ml_manager.set_active_model(model.id)
                    active_model = ml_manager.get_active_model()
                
                # Test 8a: Start training
                print("\n8a. Starting training session...")
                session = ml_manager.start_training_session(
                    model_id=active_model['id'],
                    notes='Integration test training'
                )
                print(f"âœ… Training session started: ID={session.id}")
                print(f"   Status: {session.status}")
                
                # Test 8b: End training
                print("\n8b. Ending training session...")
                success = ml_manager.end_training_session(
                    session_id=session.id,
                    training_samples_count=1000,
                    training_accuracy=0.95,
                    validation_accuracy=0.92,
                    training_loss=0.15,
                    validation_loss=0.18,
                    status='completed'
                )
                assert success
                print(f"âœ… Training session completed")
                print(f"   - Training accuracy: 0.95")
                print(f"   - Validation accuracy: 0.92")
                print(f"   - Samples: 1000")
                
                # Test 8c: Get training history
                print("\n8c. Retrieving training history...")
                history = ml_manager.get_training_history(active_model['id'])
                print(f"âœ… Retrieved {len(history)} training session(s)")
                
                self.results['passed'].append("Training history")
                return True
                
        except Exception as e:
            print(f"âŒ Test failed: {str(e)}")
            self.results['failed'].append(f"Training history: {str(e)}")
            import traceback
            traceback.print_exc()
            return False
    
    def test_prediction_service(self) -> bool:
        """à¸—à¸”à¸ªà¸­à¸š ParkingPredictionService"""
        print("\n" + "="*50)
        print("ðŸš€ TEST 9: ParkingPredictionService")
        print("="*50)
        
        try:
            from app import create_app
            from ML.services import ParkingPredictionService
            
            app = create_app()
            
            with app.app_context():
                service = ParkingPredictionService()
                
                # Ensure active model exists
                active_model = service.ml_manager.get_active_model()
                if not active_model:
                    model = service.ml_manager.add_ml_model(
                        name=f'TestModel_Service_{id(object())}',
                        model_type='RandomForest',
                        version='1.0.0',
                        file_path='ML/models/test_service.pkl'
                    )
                    service.ml_manager.set_active_model(model.id)
                
                # Test 9a: Make single prediction
                print("\n9a. Making prediction for single area...")
                result = service.make_prediction(parking_area_id=1)
                assert result['success'], result.get('error', 'Unknown error')
                print(f"âœ… Prediction made for area {result['parking_area_id']}")
                print(f"   - Result: {result['prediction']}")
                print(f"   - Confidence: {result['confidence']}")
                print(f"   - Model: {result['model_name']}")
                
                # Test 9b: Make predictions for all areas
                print("\n9b. Making predictions for all areas...")
                result = service.predict_all_areas()
                assert result['success'], result.get('error', 'Unknown error')
                print(f"âœ… Predictions made for {result['total_predictions']} areas")
                
                # Test 9c: Get prediction history
                print("\n9c. Getting prediction history...")
                history = service.get_prediction_history(1, limit=5)
                print(f"âœ… Retrieved {len(history)} recent prediction(s)")
                
                # Test 9d: Get active model info
                print("\n9d. Getting active model info...")
                info = service.get_active_model_info()
                if info['model']:
                    print(f"âœ… Active model: {info['model']['name']}")
                    print(f"   - Version: {info['model']['version']}")
                    print(f"   - Type: {info['model']['model_type']}")
                
                self.results['passed'].append("Prediction service")
                return True
                
        except Exception as e:
            print(f"âŒ Test failed: {str(e)}")
            self.results['failed'].append(f"Prediction service: {str(e)}")
            import traceback
            traceback.print_exc()
            return False
    
    def print_summary(self) -> None:
        """à¸žà¸´à¸¡à¸žà¹Œà¸ªà¸£à¸¸à¸›à¸œà¸¥à¸—à¸”à¸ªà¸­à¸š"""
        print("\n" + "="*50)
        print("ðŸ“Š ML SYSTEM TEST SUMMARY")
        print("="*50)
        
        if self.results['passed']:
            print(f"\nâœ… PASSED ({len(self.results['passed'])}):")
            for test in self.results['passed']:
                print(f"   â€¢ {test}")
        
        if self.results['failed']:
            print(f"\nâŒ FAILED ({len(self.results['failed'])}):")
            for test in self.results['failed']:
                print(f"   â€¢ {test}")
        
        if self.results['warnings']:
            print(f"\nâš ï¸  WARNINGS ({len(self.results['warnings'])}):")
            for warning in self.results['warnings']:
                print(f"   â€¢ {warning}")
        
        print("\n" + "="*50)
        
        total = len(self.results['passed']) + len(self.results['failed'])
        passed_pct = (len(self.results['passed']) / total * 100) if total > 0 else 0
        
        print(f"Passed: {len(self.results['passed'])}/{total} ({passed_pct:.0f}%)")
        
        if not self.results['failed']:
            print("âœ… ALL ML SYSTEM TESTS PASSED!")
        else:
            print(f"âŒ {len(self.results['failed'])} TEST(S) FAILED")
        
        print("="*50 + "\n")
    
    def run_all_tests(self) -> bool:
        """à¸£à¸±à¸™ test à¸—à¸±à¹‰à¸‡à¸«à¸¡à¸”"""
        print("\n")
        print("â•”" + "="*48 + "â•—")
        print("â•‘" + " "*12 + "TU PARKING - ML SYSTEM TEST SUITE" + " "*3 + "â•‘")
        print("â•‘" + " "*20 + "ðŸ¤– ML Integration" + " "*12 + "â•‘")
        print("â•š" + "="*48 + "â•")
        
        # Import tests
        self.test_ml_models_import()
        self.test_ml_manager_import()
        self.test_data_preparer_import()
        self.test_prediction_service_import()
        
        # If imports failed, stop here
        if len(self.results['failed']) > 0:
            print("\n" + "="*50)
            print("âŒ CANNOT PROCEED - Import tests failed")
            print("="*50)
            self.print_summary()
            return False
        
        # Functional tests
        self.test_database_operations()
        self.test_data_preparation()
        self.test_predictions()
        self.test_training_history()
        self.test_prediction_service()
        
        # Print summary
        self.print_summary()
        
        return len(self.results['failed']) == 0


if __name__ == '__main__':
    tester = MLSystemTester()
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)

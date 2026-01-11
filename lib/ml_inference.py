#File: lib/ml_inference.py
import pickle
import numpy as np
import pandas as pd

data = "data"
model_dir= "models"


class WastePredictor:
    def __init__(self):
        # Load all models
        with open(model_dir+'/encoders.pkl', 'rb') as f:
            self.encoders = pickle.load(f)
        
        with open(model_dir+'/waste_type_classifiers.pkl', 'rb') as f:
            self.waste_classifiers = pickle.load(f)
        
        with open(model_dir+'/quantity_models.pkl', 'rb') as f:
            self.quantity_models = pickle.load(f)
        
        with open(model_dir+'/quality_models.pkl', 'rb') as f:
            self.quality_models = pickle.load(f)
        
        with open(model_dir+'/contamination_models.pkl', 'rb') as f:
            self.contamination_models = pickle.load(f)
    
    def predict(self, facility_input):
        """
        Predict waste profile from facility operational data
        
        Args:
            facility_input: dict with keys:
                - industry: str
                - product: str
                - process: str
                - machinery: str
                - scale: str
                - units_per_month: int
        
        Returns:
            dict with waste profile prediction
        """
        
        # Encode features
        features = self._encode_features(facility_input)
        
        # Predict waste types
        waste_predictions = []
        for waste_type, classifier in self.waste_classifiers.items():
            prob = classifier.predict_proba(features)[0][1]  # Probability of class 1
            
            if prob > 0.3:  # Threshold for including waste type
                waste_predictions.append({
                    'type': waste_type,
                    'probability': float(prob)
                })
        
        # Sort by probability
        waste_predictions.sort(key=lambda x: x['probability'], reverse=True)
        
        # Predict quantities, quality, contamination for each waste type
        waste_streams = []
        for pred in waste_predictions:
            waste_type = pred['type']
            
            # Quantity
            if waste_type in self.quantity_models:
                qty_model = self.quantity_models[waste_type]
                avg_qty = qty_model.predict(features)[0]
                
                # Add uncertainty range (±20%)
                qty_min = avg_qty * 0.8
                qty_max = avg_qty * 1.2
            else:
                # Fallback
                qty_min, qty_max = 1.0, 5.0
            
            # Quality
            if waste_type in self.quality_models:
                qual_info = self.quality_models[waste_type]
                quality_encoded = qual_info['model'].predict(features)[0]
                quality = qual_info['encoder'].inverse_transform([quality_encoded])[0]
            else:
                quality = 'Grade B'
            
            # Contamination
            if waste_type in self.contamination_models:
                contamination = self.contamination_models[waste_type].predict(features)[0]
            else:
                contamination = 10.0
            
            # Hazard classification (rule-based)
            hazard = self._classify_hazard(waste_type, contamination)
            
            waste_streams.append({
                'type': waste_type,
                'category': self._get_category(waste_type),
                'quantity_min_tons': round(qty_min, 2),
                'quantity_max_tons': round(qty_max, 2),
                'quality_grade': quality,
                'contamination_pct': round(contamination, 1),
                'hazard_class': hazard,
                'confidence': round(pred['probability'], 2)
            })
        
        # Overall confidence (average of top 3 predictions)
        top_confidences = [w['confidence'] for w in waste_streams[:3]]
        overall_confidence = np.mean(top_confidences) if top_confidences else 0.5
        
        return {
            'waste_streams': waste_streams,
            'overall_confidence': round(overall_confidence, 2),
            'num_waste_types': len(waste_streams)
        }
    
    def _encode_features(self, facility_input):
        """Convert input dict to encoded feature vector"""
        
        # Encode categorical
        industry_enc = self.encoders['industry'].transform([facility_input['industry']])[0]
        product_enc = self.encoders['product'].transform([facility_input['product']])[0]
        process_enc = self.encoders['process'].transform([facility_input['process']])[0]
        machinery_enc = self.encoders['machinery'].transform([facility_input['machinery']])[0]
        scale_enc = self.encoders['scale'].transform([facility_input['scale']])[0]
        
        # Scale units
        units_scaled = self.encoders['scaler'].transform([[facility_input['units_per_month']]])[0][0]
        
        # Interaction features
        industry_process = industry_enc * 100 + process_enc
        process_machinery = process_enc * 100 + machinery_enc
        
        # Create feature array
        features = np.array([[
            industry_enc, product_enc, process_enc, machinery_enc, scale_enc,
            units_scaled, industry_process, process_machinery
        ]])
        
        return features
    
    def _get_category(self, waste_type):
        """Get waste category from waste type"""
        categories = {
            'metal': ['steel', 'aluminum', 'shavings', 'slag', 'dross'],
            'chemical': ['coolant', 'lubricant', 'solvent', 'chemical', 'paint'],
            'plastic': ['plastic', 'packaging'],
            'electronic': ['pcb', 'electronic', 'component'],
            'organic': ['organic', 'food'],
            'textile': ['fabric', 'thread'],
            'liquid': ['wastewater', 'water']
        }
        
        for category, keywords in categories.items():
            if any(kw in waste_type.lower() for kw in keywords):
                return category
        
        return 'mixed'
    
    def _classify_hazard(self, waste_type, contamination):
        """Classify hazard level"""
        hazardous_keywords = ['chemical', 'solvent', 'paint', 'dye', 'coolant', 'lubricant']
        
        if any(kw in waste_type.lower() for kw in hazardous_keywords):
            if contamination > 15:
                return 'Hazardous - Class 3'
            return 'Hazardous - Class 2'
        
        return 'Non-hazardous'
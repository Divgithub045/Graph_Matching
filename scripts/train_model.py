# #File: scripts/train_model.py

# from os.path import exists
# import pandas as pd
# import numpy as np
# import json
# from sklearn.model_selection import train_test_split
# from sklearn.preprocessing import LabelEncoder, StandardScaler
# from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
# import xgboost as xgb
# import pickle
# data = "/content/drive/MyDrive/Innovate/data"
# model_dir= "/content/drive/MyDrive/Innovate/models"
# os.makedirs(model_dir,exist_ok = True)
# # Load training data
# df = pd.read_csv(data+'/training_data.csv')

# print(f"Loaded {len(df)} training samples")

# # Feature engineering
# def prepare_features(df):
#     """Convert categorical variables to numerical features"""
    
#     # Encode categorical variables
#     le_industry = LabelEncoder()
#     le_product = LabelEncoder()
#     le_process = LabelEncoder()
#     le_machinery = LabelEncoder()
#     le_scale = LabelEncoder()
    
#     df['industry_encoded'] = le_industry.fit_transform(df['industry'])
#     df['product_encoded'] = le_product.fit_transform(df['product'])
#     df['process_encoded'] = le_process.fit_transform(df['process'])
#     df['machinery_encoded'] = le_machinery.fit_transform(df['machinery'])
#     df['scale_encoded'] = le_scale.fit_transform(df['scale'])
    
#     # Create interaction features
#     df['industry_process'] = df['industry_encoded'] * 100 + df['process_encoded']
#     df['process_machinery'] = df['process_encoded'] * 100 + df['machinery_encoded']
    
#     # Scale numerical features
#     scaler = StandardScaler()
#     df['units_scaled'] = scaler.fit_transform(df[['units_per_month']])
    
#     # Save encoders
#     encoders = {
#         'industry': le_industry,
#         'product': le_product,
#         'process': le_process,
#         'machinery': le_machinery,
#         'scale': le_scale,
#         'scaler': scaler
#     }
    
#     with open(model_dir+'/encoders.pkl', 'wb') as f:
#         pickle.dump(encoders, f)
    
#     return df, encoders

# df, encoders = prepare_features(df)

# # Prepare feature matrix
# feature_cols = [
#     'industry_encoded', 'product_encoded', 'process_encoded', 
#     'machinery_encoded', 'scale_encoded', 'units_scaled',
#     'industry_process', 'process_machinery'
# ]

# X = df[feature_cols]

# # Model 1: Waste Type Prediction (Multi-label Classification)
# print("\n=== Training Waste Type Classifier ===")

# # Extract all unique waste types from waste_streams
# all_waste_types = set()
# for streams in df['waste_streams']:
#     for waste in json.loads(streams):
#         all_waste_types.add(waste['type'])

# waste_types_list = sorted(list(all_waste_types))
# print(f"Found {len(waste_types_list)} unique waste types")

# # Create multi-label target
# y_waste_types = np.zeros((len(df), len(waste_types_list)))
# for i, streams in enumerate(df['waste_streams']):
#     for waste in json.loads(streams):
#         idx = waste_types_list.index(waste['type'])
#         y_waste_types[i, idx] = 1

# # Train one classifier per waste type (multi-label)
# waste_classifiers = {}
# for i, waste_type in enumerate(waste_types_list):
#     print(f"Training classifier for {waste_type}...")
    
#     clf = xgb.XGBClassifier(
#         n_estimators=100,
#         max_depth=6,
#         learning_rate=0.1,
#         random_state=42
#     )
    
#     clf.fit(X, y_waste_types[:, i])
#     waste_classifiers[waste_type] = clf

# # Save waste type classifiers
# with open(model_dir + '/waste_type_classifiers.pkl', 'wb') as f:
#     pickle.dump(waste_classifiers, f)

# print("✅ Waste type classifiers saved")

# # Model 2: Quantity Prediction (one model per waste type)
# print("\n=== Training Quantity Regressors ===")

# quantity_models = {}
# for waste_type in waste_types_list:
#     print(f"Training quantity model for {waste_type}...")
    
#     # Extract quantities for this waste type
#     X_qty = []
#     y_qty = []
    
#     for idx, streams in enumerate(df['waste_streams']):
#         for waste in json.loads(streams):
#             if waste['type'] == waste_type:
#                 X_qty.append(X.iloc[idx].values)
#                 avg_qty = (waste['quantity_min_tons'] + waste['quantity_max_tons']) / 2
#                 y_qty.append(avg_qty)
    
#     if len(X_qty) > 10:  # Only train if we have enough samples
#         X_qty = np.array(X_qty)
#         y_qty = np.array(y_qty)
        
#         model = RandomForestRegressor(
#             n_estimators=100,
#             max_depth=10,
#             random_state=42
#         )
        
#         model.fit(X_qty, y_qty)
#         quantity_models[waste_type] = model

# # Save quantity models
# with open(model_dir + '/quantity_models.pkl', 'wb') as f:
#     pickle.dump(quantity_models, f)

# print("✅ Quantity models saved")

# # Model 3: Quality/Contamination Prediction
# print("\n=== Training Quality Models ===")

# quality_models = {}
# contamination_models = {}

# for waste_type in waste_types_list:
#     print(f"Training quality models for {waste_type}...")
    
#     X_qual = []
#     y_quality = []
#     y_contamination = []
    
#     for idx, streams in enumerate(df['waste_streams']):
#         for waste in json.loads(streams):
#             if waste['type'] == waste_type:
#                 X_qual.append(X.iloc[idx].values)
#                 y_quality.append(waste['quality_grade'])
#                 y_contamination.append(waste['contamination_pct'])
    
#     if len(X_qual) > 10:
#         X_qual = np.array(X_qual)
        
#         # Quality classifier
#         le_quality = LabelEncoder()
#         y_quality_encoded = le_quality.fit_transform(y_quality)
        
#         qual_clf = RandomForestClassifier(n_estimators=50, random_state=42)
#         qual_clf.fit(X_qual, y_quality_encoded)
        
#         quality_models[waste_type] = {
#             'model': qual_clf,
#             'encoder': le_quality
#         }
        
#         # Contamination regressor
#         contam_model = RandomForestRegressor(n_estimators=50, random_state=42)
#         contam_model.fit(X_qual, y_contamination)
        
#         contamination_models[waste_type] = contam_model

# # Save quality models
# with open(model_dir + '/quality_models.pkl', 'wb') as f:
#     pickle.dump(quality_models, f)

# with open(model_dir + '/contamination_models.pkl', 'wb') as f:
#     pickle.dump(contamination_models, f)

# print("✅ Quality and contamination models saved")

# print("\n🎉 All models trained and saved successfully!")
# print("\nModel files created:")
# print("  - models/encoders.pkl")
# print("  - models/waste_type_classifiers.pkl")
# print("  - models/quantity_models.pkl")
# print("  - models/quality_models.pkl")
# print("  - models/contamination_models.pkl")
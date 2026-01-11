# import pandas as pd
# import numpy as np
# from datetime import datetime, timedelta
# import random
# import json
# import os

# # Define industrial knowledge base
# INDUSTRIES = {
#     'automotive': {
#         'products': ['engine_components', 'transmissions', 'body_panels', 'electrical_systems'],
#         'processes': ['cnc_machining', 'stamping', 'welding', 'assembly', 'painting'],
#         'machinery': ['cnc_lathe', 'milling_machine', 'press', 'welding_robot', 'spray_booth'],
#         'waste_profiles': [
#             {'type': 'metal_scrap_steel', 'category': 'metal', 'qty_factor': 0.15, 'contamination': (1, 3)},
#             {'type': 'metal_scrap_aluminum', 'category': 'metal', 'qty_factor': 0.08, 'contamination': (1, 5)},
#             {'type': 'used_coolant', 'category': 'chemical', 'qty_factor': 0.02, 'contamination': (5, 15)},
#             {'type': 'used_lubricant', 'category': 'chemical', 'qty_factor': 0.01, 'contamination': (10, 25)},
#             {'type': 'paint_sludge', 'category': 'chemical', 'qty_factor': 0.03, 'contamination': (15, 30)}
#         ]
#     },
#     'electronics': {
#         'products': ['circuit_boards', 'semiconductors', 'displays', 'connectors'],
#         'processes': ['smt_assembly', 'wave_soldering', 'testing', 'packaging'],
#         'machinery': ['pick_place', 'reflow_oven', 'wave_solder', 'aoi_machine'],
#         'waste_profiles': [
#             {'type': 'pcb_scrap', 'category': 'electronic', 'qty_factor': 0.05, 'contamination': (2, 8)},
#             {'type': 'solder_dross', 'category': 'metal', 'qty_factor': 0.02, 'contamination': (5, 15)},
#             {'type': 'electronic_components', 'category': 'electronic', 'qty_factor': 0.03, 'contamination': (1, 5)},
#             {'type': 'plastic_packaging', 'category': 'plastic', 'qty_factor': 0.04, 'contamination': (2, 10)}
#         ]
#     },
#     'food_processing': {
#         'products': ['packaged_foods', 'beverages', 'frozen_goods', 'snacks'],
#         'processes': ['cooking', 'mixing', 'packaging', 'sterilization', 'freezing'],
#         'machinery': ['industrial_oven', 'mixer', 'packaging_line', 'autoclave', 'blast_freezer'],
#         'waste_profiles': [
#             {'type': 'organic_waste', 'category': 'organic', 'qty_factor': 0.12, 'contamination': (5, 20)},
#             {'type': 'packaging_plastic', 'category': 'plastic', 'qty_factor': 0.06, 'contamination': (3, 12)},
#             {'type': 'packaging_cardboard', 'category': 'paper', 'qty_factor': 0.08, 'contamination': (2, 8)},
#             {'type': 'wastewater', 'category': 'liquid', 'qty_factor': 0.25, 'contamination': (10, 30)}
#         ]
#     },
#     'textiles': {
#         'products': ['fabric', 'garments', 'home_textiles', 'industrial_textiles'],
#         'processes': ['weaving', 'dyeing', 'cutting', 'sewing', 'finishing'],
#         'machinery': ['loom', 'dyeing_machine', 'cutting_table', 'sewing_machine', 'heat_press'],
#         'waste_profiles': [
#             {'type': 'fabric_scraps', 'category': 'textile', 'qty_factor': 0.15, 'contamination': (1, 5)},
#             {'type': 'thread_waste', 'category': 'textile', 'qty_factor': 0.03, 'contamination': (1, 3)},
#             {'type': 'dye_wastewater', 'category': 'liquid', 'qty_factor': 0.20, 'contamination': (20, 40)},
#             {'type': 'packaging_materials', 'category': 'mixed', 'qty_factor': 0.05, 'contamination': (5, 15)}
#         ]
#     },
#     'metalworking': {
#         'products': ['structural_steel', 'custom_parts', 'tools', 'metal_fixtures'],
#         'processes': ['cutting', 'welding', 'grinding', 'drilling', 'heat_treatment'],
#         'machinery': ['plasma_cutter', 'welder', 'grinder', 'drill_press', 'furnace'],
#         'waste_profiles': [
#             {'type': 'metal_shavings', 'category': 'metal', 'qty_factor': 0.18, 'contamination': (2, 8)},
#             {'type': 'welding_slag', 'category': 'metal', 'qty_factor': 0.04, 'contamination': (5, 15)},
#             {'type': 'cutting_coolant', 'category': 'chemical', 'qty_factor': 0.02, 'contamination': (10, 25)},
#             {'type': 'grinding_dust', 'category': 'metal', 'qty_factor': 0.03, 'contamination': (15, 35)}
#         ]
#     },
#     'chemical': {
#         'products': ['industrial_chemicals', 'solvents', 'cleaning_agents', 'coatings'],
#         'processes': ['mixing', 'distillation', 'filtration', 'reaction', 'packaging'],
#         'machinery': ['reactor', 'distillation_column', 'filter_press', 'mixer', 'filling_machine'],
#         'waste_profiles': [
#             {'type': 'chemical_residue', 'category': 'chemical', 'qty_factor': 0.08, 'contamination': (10, 30)},
#             {'type': 'contaminated_solvents', 'category': 'chemical', 'qty_factor': 0.06, 'contamination': (15, 40)},
#             {'type': 'filter_waste', 'category': 'mixed', 'qty_factor': 0.04, 'contamination': (20, 50)},
#             {'type': 'packaging_drums', 'category': 'metal', 'qty_factor': 0.03, 'contamination': (5, 15)}
#         ]
#     }
# }

# LOCATIONS = [
#     {'city': 'Lucknow',   'state': 'Uttar Pradesh',   'lat': 26.85, 'lng': 80.95},
#     {'city': 'Mumbai',    'state': 'Maharashtra',     'lat': 19.08, 'lng': 72.88},
#     {'city': 'Delhi',     'state': 'Delhi',           'lat': 28.61, 'lng': 77.21},
#     {'city': 'Bengaluru', 'state': 'Karnataka',       'lat': 12.97, 'lng': 77.59},
#     {'city': 'Chennai',   'state': 'Tamil Nadu',      'lat': 13.08, 'lng': 80.27},
#     {'city': 'Hyderabad', 'state': 'Telangana',       'lat': 17.39, 'lng': 78.49},
#     {'city': 'Kolkata',   'state': 'West Bengal',     'lat': 22.57, 'lng': 88.36},
#     {'city': 'Pune',      'state': 'Maharashtra',     'lat': 18.52, 'lng': 73.85},
#     {'city': 'Ahmedabad', 'state': 'Gujarat',         'lat': 23.02, 'lng': 72.57},
#     {'city': 'Jaipur',    'state': 'Rajasthan',       'lat': 26.91, 'lng': 75.79}

# ]

# SCALES = [
#     {'name': 'small', 'units_min': 100, 'units_max': 1000, 'multiplier': 1},
#     {'name': 'medium', 'units_min': 1000, 'units_max': 10000, 'multiplier': 5},
#     {'name': 'large', 'units_min': 10000, 'units_max': 100000, 'multiplier': 20}
# ]

# def generate_synthetic_data(num_samples=10000):
#     """Generate synthetic training data for waste prediction"""
    
#     data = []
    
#     for i in range(num_samples):
#         # Random industry
#         industry_name = random.choice(list(INDUSTRIES.keys()))
#         industry = INDUSTRIES[industry_name]
        
#         # Random selections
#         product = random.choice(industry['products'])
#         process = random.choice(industry['processes'])
#         machinery = random.choice(industry['machinery'])
#         scale = random.choice(SCALES)
#         location = random.choice(LOCATIONS)
        
#         # Production volume
#         units_per_month = random.randint(scale['units_min'], scale['units_max'])
        
#         # Generate waste streams
#         waste_streams = []
#         for waste_template in industry['waste_profiles']:
#             # Not all facilities generate all waste types
#             if random.random() > 0.3:  # 70% chance of generating this waste
#                 base_qty = units_per_month * waste_template['qty_factor'] * scale['multiplier'] / 1000  # tons
                
#                 # Add variability
#                 qty_min = base_qty * random.uniform(0.8, 1.0)
#                 qty_max = base_qty * random.uniform(1.0, 1.3)
                
#                 contamination = random.uniform(*waste_template['contamination'])
                
#                 # Quality grade based on contamination
#                 if contamination < 5:
#                     quality = 'Grade A'
#                 elif contamination < 15:
#                     quality = 'Grade B'
#                 else:
#                     quality = 'Grade C'
                
#                 # Hazard classification
#                 hazard = 'Hazardous' if waste_template['category'] == 'chemical' and contamination > 10 else 'Non-hazardous'
                
#                 waste_streams.append({
#                     'type': waste_template['type'],
#                     'category': waste_template['category'],
#                     'quantity_min_tons': round(qty_min, 2),
#                     'quantity_max_tons': round(qty_max, 2),
#                     'contamination_pct': round(contamination, 1),
#                     'quality_grade': quality,
#                     'hazard_class': hazard
#                 })
        
#         # Create record
#         record = {
#             'facility_id': f'FAC_{i:05d}',
#             'industry': industry_name,
#             'product': product,
#             'process': process,
#             'machinery': machinery,
#             'scale': scale['name'],
#             'units_per_month': units_per_month,
#             'location_city': location['city'],
#             'location_state': location['state'],
#             'location_lat': location['lat'],
#             'location_lng': location['lng'],
#             'waste_streams': json.dumps(waste_streams),
#             'num_waste_types': len(waste_streams)
#         }
        
#         data.append(record)
    
#     return pd.DataFrame(data)
  

# # Generate and save
# from google.colab import drive
# drive.mount('/content/drive')
# location = "/content/drive/MyDrive/Innovate/data"
# os.makedirs(location, exist_ok=True)
# print("Generating 1000 synthetic training samples...")
# df = generate_synthetic_data(1000)
# df.to_csv(location+'/training_data.csv', index=False)
# print(f"✅ Saved {len(df)} samples to data/training_data.csv")
# print(f"\nSample record:")
# print(df.iloc[0])
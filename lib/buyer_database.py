import pandas as pd
import numpy as np
filename = "data/waste_buyers_india_updated_cities.csv"
class BuyerDatabase:
    def __init__(self, filename):
        self.df = pd.read_csv(filename)
        self._process_data()
    
    def _process_data(self):
        """Process and validate buyer data"""
        
        # Split comma-separated values
        self.df['accepted_waste_types'] = self.df['accepted_waste_types'].apply(
            lambda x: [w.strip() for w in str(x).split(',')]
        )
        self.df['accepted_categories'] = self.df['accepted_categories'].apply(
            lambda x: [c.strip() for c in str(x).split(',')]
        )
        self.df['certifications'] = self.df['certifications'].apply(
            lambda x: [c.strip() for c in str(x).split(',')]
        )
    
    def get_all_buyers(self):
        """Return all buyers as list of dicts"""
        return self.df.to_dict('records')
    
    def search_buyers(self, waste_type=None, category=None, location=None, max_distance_km=None):
        """Search for matching buyers"""
        
        filtered = self.df.copy()
        
        if waste_type:
            filtered = filtered[
                filtered['accepted_waste_types'].apply(lambda x: waste_type in x)
            ]
        
        if category:
            filtered = filtered[
                filtered['accepted_categories'].apply(lambda x: category in x)
            ]
        
        if location and max_distance_km:
            distances = filtered.apply(
                lambda row: self._haversine_distance(
                    location['lat'], location['lng'],
                    row['lat'], row['lng']
                ),
                axis=1
            )
            filtered = filtered[distances <= max_distance_km]
        
        return filtered.to_dict('records')
    
    @staticmethod
    def _haversine_distance(lat1, lon1, lat2, lon2):
        """Calculate distance between two points in km"""
        R = 6371  # Earth radius in km
        
        lat1, lon1, lat2, lon2 = map(np.radians, [lat1, lon1, lat2, lon2])
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        
        a = np.sin(dlat/2)**2 + np.cos(lat1) * np.cos(lat2) * np.sin(dlon/2)**2
        c = 2 * np.arcsin(np.sqrt(a))
        
        return R * c
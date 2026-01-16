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
    
    def search_by_location(self, location, max_distance_km=500):
        """
        Search for buyers by location (city name or coordinates).
        Returns buyers in the specified city, or nearby buyers within max_distance_km.
        Uses haversine distance calculation for geographic proximity.
        """
        # City to coordinates mapping for common Indian cities
        city_coordinates = {
            'delhi': (28.61, 77.21),
            'mumbai': (19.08, 72.88),
            'bangalore': (12.97, 77.59),
            'hyderabad': (17.39, 78.49),
            'pune': (18.52, 73.86),
            'ahmedabad': (23.02, 72.57),
            'kolkata': (22.57, 88.36),
            'chennai': (13.08, 80.27),
            'jaipur': (26.91, 75.78),
            'lucknow': (26.85, 80.95)
        }
        
        # Try exact city match first (case-insensitive)
        location_lower = location.lower()
        exact_match = self.df[self.df['city'].str.lower() == location_lower]
        
        if len(exact_match) > 0:
            return exact_match.to_dict('records')
        
        # If no exact match, try to find nearby cities using coordinates
        if location_lower in city_coordinates:
            target_lat, target_lng = city_coordinates[location_lower]
            
            # Calculate distance to all buyers
            distances = self.df.apply(
                lambda row: self._haversine_distance(
                    target_lat, target_lng,
                    row['lat'], row['lng']
                ),
                axis=1
            )
            
            # Filter by max_distance_km
            nearby = self.df[distances <= max_distance_km]
            
            if len(nearby) > 0:
                return nearby.to_dict('records')
        
        # If still no results, return all buyers as last resort
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


import networkx as nx
import numpy as np
from typing import List, Dict
import matplotlib.pyplot as plt

class GraphMatcher:
    def __init__(self, buyer_database):
        """
        Initialize matcher with buyer database
        buyer_database: BuyerDatabase instance
        """
        self.buyer_db = buyer_database
        self.graph = None
    
    def build_graph(self, waste_profile: Dict, buyers: List[Dict]) -> nx.DiGraph:
        """
        Build weighted directed bipartite graph
        
        Nodes:
            - Waste streams (source nodes)
            - Buyers (sink nodes)
        
        Edges:
            - Weighted by match quality (0-1)
            - Directed from waste to buyer
        """
        
        G = nx.DiGraph()
        
        # Add waste stream nodes
        for i, waste in enumerate(waste_profile['waste_streams']):
            node_id = f"waste_{i}_{waste['type']}"
            G.add_node(
                node_id,
                node_type='waste',
                waste_data=waste,
                facility_location=waste_profile['location']
            )
        
        # Add buyer nodes
        for buyer in buyers:
            buyer_id = f"buyer_{buyer['buyer_id']}"
            G.add_node(
                buyer_id,
                node_type='buyer',
                buyer_data=buyer
            )
        
        # Create edges with weights
        edge_count = 0
        for i, waste in enumerate(waste_profile['waste_streams']):
            waste_node = f"waste_{i}_{waste['type']}"
            
            for buyer in buyers:
                buyer_node = f"buyer_{buyer['buyer_id']}"
                
                # Calculate comprehensive match score
                score_data = self._calculate_match_score(
                    waste, 
                    buyer,
                    waste_profile['location']
                )
                
                # Only add edge if score above threshold
                if score_data['total_score'] > 0.3:
                    G.add_edge(
                        waste_node,
                        buyer_node,
                        weight=score_data['total_score'],
                        **score_data  # Include all score components
                    )
                    edge_count += 1
        
        print(f"Graph built: {G.number_of_nodes()} nodes, {edge_count} edges")
        self.graph = G
        return G
    
    def _calculate_match_score(self, waste: Dict, buyer: Dict, facility_location: Dict) -> Dict:
        """
        Multi-dimensional scoring function
        
        Dimensions:
            1. Material compatibility (35%)
            2. Quality fit (20%)
            3. Volume match (15%)
            4. Distance/logistics (20%)
            5. Regulatory compliance (10%)
        """
        
        # 1. Material Compatibility
        material_score = self._score_material_match(waste, buyer)
        
        # 2. Quality Fit
        quality_score = self._score_quality_match(waste, buyer)
        
        # 3. Volume Fit
        volume_score = self._score_volume_match(waste, buyer)
        
        # 4. Distance Score
        distance_km = self._haversine_distance(
            facility_location['lat'], facility_location['lng'],
            buyer['lat'], buyer['lng']
        )
        distance_score = self._score_distance(distance_km)
        
        # 5. Compliance Score
        compliance_score = self._score_compliance(waste, buyer)
        
        # Weighted total
        weights = {
            'material': 0.35,
            'quality': 0.20,
            'volume': 0.15,
            'distance': 0.20,
            'compliance': 0.10
        }
        
        total_score = (
            material_score * weights['material'] +
            quality_score * weights['quality'] +
            volume_score * weights['volume'] +
            distance_score * weights['distance'] +
            compliance_score * weights['compliance']
        )
        
        # Economic calculations
        economics = self._calculate_economics(waste, buyer, distance_km)
        
        # Environmental impact
        environmental = self._calculate_environmental_impact(waste, distance_km)
        
        return {
            'total_score': round(total_score, 3),
            'score_breakdown': {
                'material': round(material_score, 3),
                'quality': round(quality_score, 3),
                'volume': round(volume_score, 3),
                'distance': round(distance_score, 3),
                'compliance': round(compliance_score, 3)
            },
            'distance_km': round(distance_km, 1),
            'economics': economics,
            'environmental': environmental
        }
    
    def _score_material_match(self, waste: Dict, buyer: Dict) -> float:
        """Score material compatibility"""
        
        waste_type = waste['type']
        waste_category = waste['category']
        
        accepted_types = buyer.get('accepted_waste_types', [])
        accepted_categories = buyer.get('accepted_categories', [])
        
        # Exact type match = 1.0
        if waste_type in accepted_types:
            return 1.0
        
        # Category match = 0.7
        if waste_category in accepted_categories:
            return 0.7
        
        # No match
        return 0.0
    
    def _score_quality_match(self, waste: Dict, buyer: Dict) -> float:
        """Score quality alignment"""
        
        quality_hierarchy = {
            'Grade A': 4,
            'Clean': 3,
            'Grade B': 2,
            'Grade C': 1,
            'Mixed': 1,
            'As-Is': 0
        }
        
        waste_quality = waste.get('quality_grade', 'Grade B')
        min_required = buyer.get('min_quality_grade', 'Grade C')
        
        waste_level = quality_hierarchy.get(waste_quality, 2)
        required_level = quality_hierarchy.get(min_required, 1)
        
        if waste_level >= required_level:
            # Exceeds requirements
            return 1.0
        elif waste_level == required_level - 1:
            # Close but below
            return 0.6
        else:
            # Significantly below
            return 0.3
    
    def _score_volume_match(self, waste: Dict, buyer: Dict) -> float:
        """Score volume compatibility"""
        
        avg_waste_qty = (waste['quantity_min_tons'] + waste['quantity_max_tons']) / 2
        
        min_vol = buyer.get('min_monthly_volume_tons', 0)
        max_vol = buyer.get('max_monthly_volume_tons', float('inf'))
        
        if min_vol <= avg_waste_qty <= max_vol:
            # Perfect fit
            return 1.0
        elif avg_waste_qty < min_vol:
            # Below minimum - partial credit
            ratio = avg_waste_qty / min_vol if min_vol > 0 else 0
            return max(0.3, min(ratio, 1.0))
        else:
            # Above maximum - can split/batch
            return 0.7
    
    def _score_distance(self, distance_km: float) -> float:
        """Score based on logistics distance"""
        
        # Scoring curve
        if distance_km <= 50:
            return 1.0
        elif distance_km <= 150:
            return 0.85
        elif distance_km <= 300:
            return 0.65
        elif distance_km <= 500:
            return 0.45
        elif distance_km <= 800:
            return 0.25
        else:
            return 0.1
    
    def _score_compliance(self, waste: Dict, buyer: Dict) -> float:
        """Score regulatory compliance"""
        
        hazard_class = waste.get('hazard_class', 'Non-hazardous')
        certifications = buyer.get('certifications', [])
        
        # Check if hazardous waste requires special permits
        if 'Hazardous' in hazard_class:
            required_certs = ['CPCB', 'SPCB', 'MoEFCC', 'Hazardous_Waste_Authorization']
            
            # Check if buyer has any required certification
            certs_str = ' '.join(certifications).upper()
            has_hazmat_cert = any(
                cert.upper().replace('_', '') in certs_str.replace('_', '')
                for cert in required_certs
            )
            
            return 1.0 if has_hazmat_cert else 0.2
        
        # Non-hazardous always compliant
        return 1.0
    
    def _haversine_distance(self, lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """Calculate distance between two coordinates in km"""
        
        R = 6371  # Earth radius in km
        
        lat1, lon1, lat2, lon2 = map(np.radians, [lat1, lon1, lat2, lon2])
        
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        
        a = np.sin(dlat/2)**2 + np.cos(lat1) * np.cos(lat2) * np.sin(dlon/2)**2
        c = 2 * np.arcsin(np.sqrt(a))
        
        return R * c
    
    def _calculate_economics(self, waste: Dict, buyer: Dict, distance: float) -> Dict:
        """Calculate economic impact in INR"""
        
        avg_qty = (waste['quantity_min_tons'] + waste['quantity_max_tons']) / 2
        annual_qty = avg_qty * 12
        
        # Parse pricing
        pricing = buyer.get('pricing_model', '₹10000-12000/ton')
        pricing_clean = pricing.replace('₹', '').replace(',', '').strip()
        
        # Handle different formats
        if '-' in pricing_clean:
            parts = pricing_clean.split('-')
            try:
                min_price = float(parts[0])
                max_price = float(parts[1].split('/')[0])
                avg_price = (min_price + max_price) / 2
            except:
                avg_price = 10000
        elif 'Market_Rate' in pricing:
            avg_price = 12000
        elif 'Negotiable' in pricing:
            avg_price = 10000
        elif 'Collection_Fee' in pricing:
            # This is a cost, not revenue
            try:
                fee = float(pricing_clean.split(':')[1].split('-')[0])
                avg_price = -fee  # Negative indicates cost
            except:
                avg_price = -5000
        else:
            avg_price = 10000
        
        # Calculate revenue/cost
        annual_revenue = annual_qty * avg_price
        
        # Transport cost (₹4/km/ton average in India)
        transport_cost_per_ton = distance * 4
        annual_transport = annual_qty * transport_cost_per_ton
        
        # Current disposal cost avoided (₹6000/ton average)
        disposal_savings = annual_qty * 6000
        
        # Net benefit
        if avg_price > 0:
            # Revenue model
            net_benefit = annual_revenue - annual_transport + disposal_savings
        else:
            # Collection fee model
            net_benefit = disposal_savings - abs(annual_revenue) - annual_transport
        
        return {
            'annual_revenue': round(annual_revenue, 0),
            'annual_transport_cost': round(annual_transport, 0),
            'disposal_cost_avoided': round(disposal_savings, 0),
            'net_annual_benefit': round(net_benefit, 0),
            'price_per_ton': round(avg_price, 0),
            'annual_quantity_tons': round(annual_qty, 1),
            'currency': 'INR'
        }
    
    def _calculate_environmental_impact(self, waste: Dict, distance: float) -> Dict:
        """Calculate environmental metrics"""
        
        avg_qty = (waste['quantity_min_tons'] + waste['quantity_max_tons']) / 2
        annual_qty = avg_qty * 12
        
        # CO2 emission factors (tons CO2 per ton waste)
        emission_factors = {
            'landfill': 0.8,
            'recycling': 0.15,
            'transport_per_km': 0.00012  # per ton-km
        }
        
        # Emissions from landfill (baseline)
        landfill_emissions = annual_qty * emission_factors['landfill']
        
        # Emissions from recycling + transport
        recycling_emissions = annual_qty * emission_factors['recycling']
        transport_emissions = annual_qty * distance * emission_factors['transport_per_km'] * 2  # Round trip
        
        # Net CO2 saved
        net_co2_saved = landfill_emissions - (recycling_emissions + transport_emissions)
        
        # Virgin material avoided (assume 75% recovery rate)
        virgin_material_avoided = annual_qty * 0.75
        
        return {
            'co2_saved_tons_annual': round(max(0, net_co2_saved), 2),
            'landfill_diverted_tons_annual': round(annual_qty, 1),
            'virgin_material_avoided_tons': round(virgin_material_avoided, 1),
            'recycling_efficiency_pct': 75
        }
    
    def find_optimal_matches(self, waste_profile: Dict, max_matches: int = 10) -> List[Dict]:
        """
        Find and rank optimal matches using graph algorithms
        
        Returns:
            List of match dictionaries sorted by score (frontend-compatible format)
        """
        
        # Get all buyers
        all_buyers = self.buyer_db.get_all_buyers()
        
        # Build graph
        G = self.build_graph(waste_profile, all_buyers)
        
        # Extract all viable matches with buyer deduplication
        buyer_matches = {}  # Key: buyer_id, Value: best match data
        
        for waste_node in [n for n, d in G.nodes(data=True) if d.get('node_type') == 'waste']:
            waste_data = G.nodes[waste_node]['waste_data']
            
            # Get all outgoing edges (potential buyers)
            for buyer_node in G.successors(waste_node):
                edge_data = G.edges[waste_node, buyer_node]
                buyer_data = G.nodes[buyer_node]['buyer_data']
                buyer_id = buyer_data['buyer_id']
                
                match_score = edge_data['score_breakdown']['material'] * 100
                
                # If this buyer not seen before, or this match scores higher, update
                if buyer_id not in buyer_matches or match_score > buyer_matches[buyer_id]['overallScore']:
                    buyer_matches[buyer_id] = {
                        'id': int(buyer_id.replace('B', '')),
                        'company': buyer_data['company_name'],
                        'type': buyer_data['company_type'],
                        'materialMatch': round(edge_data['score_breakdown']['material'] * 100, 1),
                        'qualityFit': round(edge_data['score_breakdown']['quality'] * 100, 1),
                        'distance': edge_data['distance_km'],
                        'costSaving': edge_data['economics']['net_annual_benefit'] / 1000,  # Convert to thousands for display
                        'environmentalImpact': {
                            'co2Saved': edge_data['environmental']['co2_saved_tons_annual'],
                            'landfillDiverted': edge_data['environmental']['landfill_diverted_tons_annual']
                        },
                        'compliance': 'Compliant' if edge_data['score_breakdown']['compliance'] > 0.5 else 'Review Required',
                        'overallScore': round(edge_data['total_score'] * 100, 1),
                        'requirements': f"Min {buyer_data.get('min_monthly_volume_tons', 'N/A')} tons/month",
                        'pricing': buyer_data.get('pricing_model', 'Market dependent')
                    }
        
        # Convert to list and sort by overall score (descending)
        matches = list(buyer_matches.values())
        matches.sort(key=lambda x: x['overallScore'], reverse=True)
        
        return matches[:max_matches]
    
    def visualize_graph(self, save_path: str = 'graph_visualization.png'):
        """Visualize the matching graph"""
        
        if not self.graph:
            print("No graph to visualize. Build graph first.")
            return
        
        plt.figure(figsize=(16, 10))
        
        # Separate node types
        waste_nodes = [n for n, d in self.graph.nodes(data=True) if d.get('node_type') == 'waste']
        buyer_nodes = [n for n, d in self.graph.nodes(data=True) if d.get('node_type') == 'buyer']
        
        # Position nodes
        pos = {}
        for i, node in enumerate(waste_nodes):
            pos[node] = (0, i)
        for i, node in enumerate(buyer_nodes):
            pos[node] = (2, i)
        
        # Draw
        nx.draw_networkx_nodes(self.graph, pos, nodelist=waste_nodes, 
                              node_color='lightcoral', node_size=800, label='Waste')
        nx.draw_networkx_nodes(self.graph, pos, nodelist=buyer_nodes,
                              node_color='lightgreen', node_size=800, label='Buyers')
        
        # Draw edges with weight-based width
        edges = self.graph.edges(data=True)
        weights = [d['weight'] * 3 for u, v, d in edges]
        nx.draw_networkx_edges(self.graph, pos, width=weights, alpha=0.6, arrows=True)
        
        # Labels
        labels = {n: n.split('_')[-1][:15] for n in self.graph.nodes()}
        nx.draw_networkx_labels(self.graph, pos, labels, font_size=8)
        
        plt.title("Waste-Buyer Matching Graph", fontsize=16)
        plt.legend()
        plt.axis('off')
        plt.tight_layout()
        plt.savefig(save_path, dpi=150, bbox_inches='tight')
        print(f"Graph visualization saved to {save_path}")
        plt.close()
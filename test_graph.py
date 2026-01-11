from lib.buyer_database import BuyerDatabase
from lib.graph_matching import GraphMatcher
from lib.ml_inference import WastePredictor
import json

# Load buyer database
print("Loading buyer database...")
buyer_db = BuyerDatabase('data/waste_buyers_india_updated_cities.csv')
print(f"✅ Loaded {len(buyer_db.get_all_buyers())} buyers")

# Load ML model and generate waste profile
print("\nGenerating waste profile...")
predictor = WastePredictor()

# Sample facility input
facility_input = {
    'industry': 'automotive',
    'product': 'engine_components',
    'process': 'cnc_machining',
    'machinery': 'cnc_lathe',
    'scale': 'medium',
    'units_per_month': 5000
}

# Predict waste
waste_profile = predictor.predict(facility_input)

# Add location (this would come from user input)
waste_profile['location'] = {
    'city': 'Pune',
    'state': 'Maharashtra',
    'lat': 18.52,
    'lng': 73.85
}

print(f"✅ Predicted {len(waste_profile['waste_streams'])} waste types")
print(f"   Confidence: {waste_profile['overall_confidence']*100:.1f}%")

# Print waste streams
for waste in waste_profile['waste_streams']:
    print(f"   - {waste['type']}: {waste['quantity_min_tons']}-{waste['quantity_max_tons']} tons/month")

# Find matches using graph algorithm
print("\nBuilding matching graph...")
matcher = GraphMatcher(buyer_db)
matches = matcher.find_optimal_matches(waste_profile, max_matches=10)

print(f"\n✅ Found {len(matches)} matches\n")

# Display top 5 matches
print("="*80)
print("TOP MATCHES")
print("="*80)

for i, match in enumerate(matches[:5], 1):
    print(f"\n{i}. {match['buyer_name']} ({match['buyer_type']})")
    print(f"   Match Score: {match['match_score']}/100")
    print(f"   Location: {match['buyer_location']} ({match['distance_km']} km)")
    print(f"   Waste: {match['waste_type']}")
    
    print(f"\n   Score Breakdown:")
    for key, val in match['score_breakdown'].items():
        print(f"      {key.capitalize()}: {val}/100")
    
    print(f"\n   Economics (Annual):")
    econ = match['economics']
    print(f"      Revenue: ₹{econ['annual_revenue']:,.0f}")
    print(f"      Transport Cost: ₹{econ['annual_transport_cost']:,.0f}")
    print(f"      Disposal Savings: ₹{econ['disposal_cost_avoided']:,.0f}")
    print(f"      NET BENEFIT: ₹{econ['net_annual_benefit']:,.0f}")
    
    print(f"\n   Environmental Impact (Annual):")
    env = match['environmental']
    print(f"      CO₂ Saved: {env['co2_saved_tons_annual']} tons")
    print(f"      Landfill Diverted: {env['landfill_diverted_tons_annual']} tons")
    
    print(f"\n   Contact:")
    print(f"      {match['buyer_contact_name']}")
    print(f"      {match['buyer_contact_email']}")
    print(f"      {match['buyer_phone']}")
    print("-"*80)

# Visualize graph
print("\nGenerating graph visualization...")
matcher.visualize_graph('output/matching_graph.png')

# Save results to JSON
with open('output/matches.json', 'w') as f:
    json.dump(matches, f, indent=2)
print("✅ Matches saved to output/matches.json")
export const INDUSTRIES: Record<string, {
  products: string[];
  processes: string[];
  machinery: string[];
}> = {
  automotive: {
    products: ['engine_components', 'transmissions', 'body_panels', 'electrical_systems'],
    processes: ['cnc_machining', 'stamping', 'welding', 'assembly', 'painting'],
    machinery: ['cnc_lathe', 'milling_machine', 'press', 'welding_robot', 'spray_booth']
  },
  electronics: {
    products: ['circuit_boards', 'semiconductors', 'displays', 'connectors'],
    processes: ['smt_assembly', 'wave_soldering', 'testing', 'packaging'],
    machinery: ['pick_place', 'reflow_oven', 'wave_solder', 'aoi_machine']
  },
  food_processing: {
    products: ['packaged_foods', 'beverages', 'frozen_goods', 'snacks'],
    processes: ['cooking', 'mixing', 'packaging', 'sterilization', 'freezing'],
    machinery: ['industrial_oven', 'mixer', 'packaging_line', 'autoclave', 'blast_freezer']
  },
  textiles: {
    products: ['fabric', 'garments', 'home_textiles', 'industrial_textiles'],
    processes: ['weaving', 'dyeing', 'cutting', 'sewing', 'finishing'],
    machinery: ['loom', 'dyeing_machine', 'cutting_table', 'sewing_machine', 'heat_press']
  },
  metalworking: {
    products: ['structural_steel', 'custom_parts', 'tools', 'metal_fixtures'],
    processes: ['cutting', 'welding', 'grinding', 'drilling', 'heat_treatment'],
    machinery: ['plasma_cutter', 'welder', 'grinder', 'drill_press', 'furnace']
  },
  chemical: {
    products: ['industrial_chemicals', 'solvents', 'cleaning_agents', 'coatings'],
    processes: ['mixing', 'distillation', 'filtration', 'reaction', 'packaging'],
    machinery: ['reactor', 'distillation_column', 'filter_press', 'mixer', 'filling_machine']
  }
};

export const LOCATIONS: Array<{ city: string; state: string; lat: number; lng: number }> = [
  { city: 'Lucknow',   state: 'Uttar Pradesh',   lat: 26.85, lng: 80.95 },
  { city: 'Mumbai',    state: 'Maharashtra',     lat: 19.08, lng: 72.88 },
  { city: 'Delhi',     state: 'Delhi',           lat: 28.61, lng: 77.21 },
  { city: 'Bengaluru', state: 'Karnataka',       lat: 12.97, lng: 77.59 },
  { city: 'Chennai',   state: 'Tamil Nadu',      lat: 13.08, lng: 80.27 },
  { city: 'Hyderabad', state: 'Telangana',       lat: 17.39, lng: 78.49 },
  { city: 'Kolkata',   state: 'West Bengal',     lat: 22.57, lng: 88.36 },
  { city: 'Pune',      state: 'Maharashtra',     lat: 18.52, lng: 73.85 },
  { city: 'Ahmedabad', state: 'Gujarat',         lat: 23.02, lng: 72.57 },
  { city: 'Jaipur',    state: 'Rajasthan',       lat: 26.91, lng: 75.79 }
];

export const SCALES = ['small', 'medium', 'large', 'xlarge'] as const;
export type ScaleName = typeof SCALES[number];
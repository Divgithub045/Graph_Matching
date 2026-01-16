import React, { useEffect, useMemo, useState } from 'react';
import { Trash2, Factory, TrendingUp, Mail, AlertTriangle, CheckCircle, Loader } from 'lucide-react';
import { INDUSTRIES, LOCATIONS, SCALES } from './data';
import { RefreshCw,Sprout,Recycle,Handshake} from 'lucide-react';


interface WasteType {
  type: string;
  quantity: string;
  quality: string;
  contamination: string;
  hazardLevel: string;
  composition: Record<string, number>;
}

interface WasteProfile {
  wasteTypes: WasteType[];
  confidence: number;
  regulatoryFlags: string[];
  location: string;
  industry: string;
}

interface Match {
  id: number;
  company: string;
  type: string;
  materialMatch: number;
  qualityFit: number;
  distance: number;
  costSaving: number;
  environmentalImpact: {
    co2Saved: number;
    landfillDiverted: number;
  };
  compliance: string;
  overallScore: number;
  requirements: string;
  pricing: string;
}

const WasteCircularPlatform = () => {
  const [step, setStep] = useState(1);
  const [loading, setLoading] = useState(false);
  const [operationalData, setOperationalData] = useState({
    industry: '',
    product: '',
    process: '',
    machinery: '',
    scale: '',
    location: '',
    units_per_month: 1000
  });
  const [wasteProfile, setWasteProfile] = useState<WasteProfile | null>(null);
  const [matches, setMatches] = useState<Match[]>([]);
  const [outreachSent, setOutreachSent] = useState(false);

  // Simulated industrial ontology and AI inference
  const inferWasteProfile = async (data: typeof operationalData): Promise<WasteProfile> => {
    setLoading(true);
    await new Promise(resolve => setTimeout(resolve, 2000));
    
    // Simulate AI-powered waste profile generation
    const profile: WasteProfile = {
      wasteTypes: [
        { 
          type: 'Metal Scrap (Steel)', 
          quantity: '15-20 tons/month',
          quality: 'Grade A (92% confidence)',
          contamination: 'Low (< 2%)',
          hazardLevel: 'Non-hazardous',
          composition: { steel: 95, other: 5 }
        },
        {
          type: 'Lubricant Oil (Used)',
          quantity: '200-300 liters/month',
          quality: 'Moderate degradation',
          contamination: 'Metal particles present',
          hazardLevel: 'Hazardous - Class 3',
          composition: { oil: 85, water: 10, solids: 5 }
        }
      ],
      confidence: 0.87,
      regulatoryFlags: ['CPCB hazardous waste permit required for oil', 'Metal scrap exempt under E-Waste Rules'],
      location: data.location,
      industry: data.industry
    };
    
    setWasteProfile(profile);
    setLoading(false);
    return profile;
  };

  // Simulated matching algorithm with weighted graph
  const findMatches = async (profile: WasteProfile): Promise<void> => {
    setLoading(true);
    await new Promise(resolve => setTimeout(resolve, 1500));
    
    const potentialMatches: Match[] = [
      {
        id: 1,
        company: 'Bharat Steel Recycling Pvt Ltd',
        type: 'Metal Recycler',
        materialMatch: 98,
        qualityFit: 95,
        distance: 45,
        costSaving: 2800,
        environmentalImpact: { co2Saved: 12.5, landfillDiverted: 18 },
        compliance: 'Fully compliant',
        overallScore: 94,
        requirements: 'Min 10 tons/month, Grade A-B steel',
        pricing: '₹15,000-18,000/ton'
      },
      {
        id: 2,
        company: 'Maharashtra Oil Reclamation Ltd',
        type: 'Oil Processor',
        materialMatch: 92,
        qualityFit: 88,
        distance: 78,
        costSaving: 1200,
        environmentalImpact: { co2Saved: 3.2, landfillDiverted: 0.3 },
        compliance: 'CPCB certified',
        overallScore: 87,
        requirements: 'Used industrial lubricants, min 150L/month',
        pricing: '₹40-65/liter collection fee'
      },
      {
        id: 3,
        company: 'India Circular Metals Network',
        type: 'Metal Broker',
        materialMatch: 85,
        qualityFit: 90,
        distance: 120,
        costSaving: 2200,
        environmentalImpact: { co2Saved: 10.8, landfillDiverted: 18 },
        compliance: 'ISO 14001 certified',
        overallScore: 82,
        requirements: 'Mixed metal scrap, flexible volumes',
        pricing: '₹12,000-16,000/ton'
      }
    ];
    
    setMatches(potentialMatches.sort((a, b) => b.overallScore - a.overallScore));
    setLoading(false);
  };

  // Simulated MCP agent outreach
  const sendOutreach = async () => {
    setLoading(true);
    await new Promise(resolve => setTimeout(resolve, 1000));
    setOutreachSent(true);
    setLoading(false);
  };

  // Rule-based calculation for units_per_month based on scale
  const calculateUnitsPerMonth = (scale: string): number => {
    const scaleMap: Record<string, number> = {
      'small': 500,
      'medium': 5000,
      'large': 50000,
      'xlarge': 100000
    };
    return scaleMap[scale.toLowerCase()] || 1000;
  };

  const handleInputChange = (field: string, value: string) => {
    setOperationalData(prev => {
      const updated = { ...prev, [field]: value };
      
      // Auto-calculate units_per_month when scale changes
      if (field === 'scale') {
        updated.units_per_month = calculateUnitsPerMonth(value);
      }

      // Reset dependent fields when industry changes
      if (field === 'industry') {
        updated.product = '';
        updated.process = '';
        updated.machinery = '';
      }
      
      return updated;
    });
  };

  const handlePredictWaste = async () => {
    setLoading(true);
    try {
      const response = await fetch('http://localhost:8000/api/predict-waste', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(operationalData)
      });
      const result = await response.json();
      
      if (result.success && result.waste_profile) {
        const waste = result.waste_profile;
        
        // Transform backend response to UI format
        const transformedProfile: WasteProfile = {
          wasteTypes: waste.waste_streams.map((stream: any) => ({
            type: stream.type,
            quantity: `${stream.quantity_min_tons}-${stream.quantity_max_tons} tons/month`,
            quality: stream.quality_grade,
            contamination: `${stream.contamination_pct}%`,
            hazardLevel: stream.hazard_class,
            composition: { primary: 100 }
          })),
          confidence: waste.overall_confidence,
          regulatoryFlags: waste.waste_streams
            .filter((s: any) => s.hazard_class === 'Hazardous')
            .map((s: any) => `${s.type}: Hazardous waste requires special handling and CPCB permits`),
          location: operationalData.location,
          industry: operationalData.industry
        };
        
        setWasteProfile(transformedProfile);
        setStep(2);
      }
    } catch (error) {
      console.error('Error predicting waste:', error);
      alert('Error predicting waste profile. Check console for details.');
    }
    setLoading(false);
  };

  const handleFindMatches = async () => {
    setLoading(true);
    try {
      const response = await fetch('http://localhost:8000/api/find-matches', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(operationalData)
      });
      const result = await response.json();
      
      if (result.success && result.matches) {
        // If backend returns raw matches, transform them
        const processedMatches = result.matches.map((match: any, idx: number) => ({
          id: match.id || idx + 1,
          company: match.company || 'Unknown Buyer',
          type: match.type || 'Waste Buyer',
          materialMatch: match.materialMatch || 85,
          qualityFit: match.qualityFit || 80,
          distance: match.distance || 0,
          costSaving: match.costSaving || 1000,
          environmentalImpact: match.environmentalImpact || { co2Saved: 5, landfillDiverted: 10 },
          compliance: match.compliance || 'Compliant',
          overallScore: match.overallScore || 80,
          requirements: match.requirements || 'Standard waste acceptance',
          pricing: match.pricing || 'Market dependent'
        }));
        
        setMatches(processedMatches);
        setStep(3);
      }
    } catch (error) {
      console.error('Error finding matches:', error);
      alert('Error finding matches. Check console for details.');
    }
    setLoading(false);
  };

  const handleSendOutreach = async () => {
    setLoading(true);
    try {
      // Save matches to backend
      const matchResults = matches.map(m => ({
        id: m.id,
        company: m.company,
        type: m.type,
        materialMatch: m.materialMatch,
        qualityFit: m.qualityFit,
        distance: m.distance,
        costSaving: m.costSaving,
        environmentalImpact: m.environmentalImpact,
        compliance: m.compliance,
        overallScore: m.overallScore
      }));
      
      const saveResponse = await fetch('http://localhost:8000/api/save-matches', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(matchResults)
      });
      
      if (saveResponse.ok) {
        await new Promise(resolve => setTimeout(resolve, 500));
        setOutreachSent(true);
        setStep(4);
      }
    } catch (error) {
      console.error('Error sending outreach:', error);
      alert('Error saving matches. Check console for details.');
    }
    setLoading(false);
  };

  const handleSaveForm = async () => {
    try {
      const response = await fetch('http://localhost:8000/api/save-form', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          operational_data: operationalData,
          timestamp: new Date().toISOString()
        })
      });
      
      if (response.ok) {
        alert('Form saved successfully!');
      } else {
        alert('Error saving form');
      }
    } catch (error) {
      console.error('Error saving form:', error);
      alert('Error saving form. Check console for details.');
    }
  };

  return (
  <div
  className="
    min-h-screen
    text-white
    p-6
    flex flex-col
    bg-gradient-to-b
    from-slate-950
    via-slate-900
    to-slate-950
  "
>


      <div className="max-w-7xl mx-auto flex-1 w-full">
        {/* Header - Always visible */}
        <div className="text-center mb-8">
          <div className="flex items-center justify-center gap-3 mb-4">
          <RefreshCw className="w-12 h-12 text-teal-500" />

            <h1 className="text-4xl font-bold">ReLoop</h1>
          </div>
          <p className="text-slate-300 text-lg">India’s Circular Resource Exchange Platform for Industrial Residues</p>
        </div>

        {/* Mobile Stats - Show only on step 1 and small screens */}
        {step === 1 && (
          <div className="grid grid-cols-2 gap-4 mb-8 lg:hidden">
            <div className="bg-slate-800 rounded-lg p-4 border-l-4 border-teal-500">
              <div className="text-2xl font-bold text-teal-400 mb-1">2.4K+</div>
              <div className="text-xs text-slate-300">Tons Waste Diverted</div>
            </div>
            <div className="bg-slate-800 rounded-lg p-4 border-l-4 border-blue-500">
              <div className="text-2xl font-bold text-blue-400 mb-1">8.50K+</div>
              <div className="text-xs text-slate-300">Tons CO₂ Reduced</div>
            </div>
            <div className="bg-slate-800 rounded-lg p-4 border-l-4 border-purple-500">
              <div className="text-2xl font-bold text-purple-400 mb-1">120+</div>
              <div className="text-xs text-slate-300">Active Partnerships</div>
            </div>
            <div className="bg-slate-800 rounded-lg p-4 border-l-4 border-yellow-500">
              <div className="text-2xl font-bold text-yellow-400 mb-1">₹4.50Cr+</div>
              <div className="text-xs text-slate-300">Value Unlocked</div>
            </div>
          </div>
        )}

        {/* Hero Section - Show only on step 1 */}
        {step === 1 && (
          <div className="bg-gradient-to-r from-teal-900/50 to-slate-800/50 rounded-xl p-8 mb-8 border border-teal-500/30">
            <div className="max-w-4xl mx-auto text-center">
              <h2 className="text-3xl font-bold mb-4 text-teal-400">Our Vision</h2>
              <p className="text-xl text-slate-200 mb-4">
                "Transforming Industrial Waste into Valuable Resources Through AI-Powered Circular Economy Solutions"
              </p>
              <p className="text-slate-300 leading-relaxed">
                We leverage cutting-edge artificial intelligence to connect waste generators with material processors or secondary buyers, 
                creating a sustainable industrial ecosystem where nothing goes to waste. Every ton of waste diverted 
                is a step towards a cleaner, more profitable future.
              </p>
            </div>
          </div>
        )}

        {/* Progress Steps - Always visible */}
        <div className="flex justify-between mb-12 max-w-3xl mx-auto">
          {[
            { num: 1, label: 'Input Data' },
            { num: 2, label: 'Waste Profile' },
            { num: 3, label: 'Match & Optimize' },
            { num: 4, label: 'Outreach' }
          ].map((s, i) => (
            <div key={i} className="flex items-center">
              <div className={`flex flex-col items-center ${step >= s.num ? 'opacity-100' : 'opacity-40'}`}>
                <div className={`w-10 h-10 rounded-full flex items-center justify-center font-bold ${
                  step >= s.num ? 'bg-teal-500' : 'bg-slate-700'
                }`}>
                  {s.num}
                </div>
                <span className="text-xs mt-2">{s.label}</span>
              </div>
              {i < 3 && <div className={`h-0.5 w-20 mx-2 ${step > s.num ? 'bg-teal-500' : 'bg-slate-700'}`} />}
            </div>
          ))}
        </div>

        {/* Three Column Layout with Sidebars - Only on Step 1 */}
        {step === 1 ? (
          <div className="flex gap-6">
            {/* Left Sidebar - Global Impact Stats */}
            <aside className="hidden lg:block w-64 flex-shrink-0">
              <div className="sticky top-6 space-y-4">
                <div className="bg-slate-800 rounded-lg p-4 border-l-4 border-teal-500 hover:scale-105 transition-transform">
                  <div className="text-2xl font-bold text-teal-400 mb-1">2.4K+</div>
                  <div className="text-xs text-slate-300">Tons Waste Diverted</div>
                </div>
                <div className="bg-slate-800 rounded-lg p-4 border-l-4 border-blue-500 hover:scale-105 transition-transform">
                  <div className="text-2xl font-bold text-blue-400 mb-1">8.50K+</div>
                  <div className="text-xs text-slate-300">Tons CO₂ Reduced</div>
                </div>
                <div className="bg-slate-800 rounded-lg p-4 border-l-4 border-purple-500 hover:scale-105 transition-transform">
                  <div className="text-2xl font-bold text-purple-400 mb-1">120+</div>
                  <div className="text-xs text-slate-300">Active Partnerships</div>
                </div>
                <div className="bg-slate-800 rounded-lg p-4 border-l-4 border-yellow-500 hover:scale-105 transition-transform">
                  <div className="text-2xl font-bold text-yellow-400 mb-1">₹4.50Cr+</div>
                  <div className="text-xs text-slate-300">Value Unlocked</div>
                </div>
              </div>
            </aside>

            {/* Main Content - Step 1 Form */}
            <div className="flex-1 min-w-0">
              <div className="bg-slate-800 rounded-xl p-8 shadow-2xl">
                <h2 className="text-2xl font-bold mb-6 flex items-center gap-2">
                  <Factory className="w-6 h-6 text-teal-400" />
                  Operational Input
                </h2>
                <div className="grid md:grid-cols-2 gap-6">
                  {/* Industry */}
                  <div>
                    <label className="block text-sm font-medium mb-2 text-slate-300">Industry Sector</label>
                    <select
                      value={operationalData.industry}
                      onChange={(e) => handleInputChange('industry', e.target.value)}
                      className="w-full px-4 py-3 bg-slate-700 border border-slate-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-teal-500 text-white"
                    >
                      <option value="">Select industry</option>
                      {Object.keys(INDUSTRIES).map(key => (
                        <option key={key} value={key}>{key}</option>
                      ))}
                    </select>
                  </div>

                  {/* Product */}
                  <div>
                    <label className="block text-sm font-medium mb-2 text-slate-300">Primary Product</label>
                    <select
                      value={operationalData.product}
                      onChange={(e) => handleInputChange('product', e.target.value)}
                      disabled={!operationalData.industry}
                      className="w-full px-4 py-3 bg-slate-700 border border-slate-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-teal-500 text-white disabled:opacity-50"
                    >
                      <option value="">{operationalData.industry ? 'Select product' : 'Select industry first'}</option>
                      {operationalData.industry && INDUSTRIES[operationalData.industry]?.products.map(p => (
                        <option key={p} value={p}>{p}</option>
                      ))}
                    </select>
                  </div>

                  {/* Process */}
                  <div>
                    <label className="block text-sm font-medium mb-2 text-slate-300">Manufacturing Process</label>
                    <select
                      value={operationalData.process}
                      onChange={(e) => handleInputChange('process', e.target.value)}
                      disabled={!operationalData.industry}
                      className="w-full px-4 py-3 bg-slate-700 border border-slate-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-teal-500 text-white disabled:opacity-50"
                    >
                      <option value="">{operationalData.industry ? 'Select process' : 'Select industry first'}</option>
                      {operationalData.industry && INDUSTRIES[operationalData.industry]?.processes.map(p => (
                        <option key={p} value={p}>{p}</option>
                      ))}
                    </select>
                  </div>

                  {/* Machinery */}
                  <div>
                    <label className="block text-sm font-medium mb-2 text-slate-300">Key Machinery</label>
                    <select
                      value={operationalData.machinery}
                      onChange={(e) => handleInputChange('machinery', e.target.value)}
                      disabled={!operationalData.industry}
                      className="w-full px-4 py-3 bg-slate-700 border border-slate-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-teal-500 text-white disabled:opacity-50"
                    >
                      <option value="">{operationalData.industry ? 'Select machinery' : 'Select industry first'}</option>
                      {operationalData.industry && INDUSTRIES[operationalData.industry]?.machinery.map(m => (
                        <option key={m} value={m}>{m}</option>
                      ))}
                    </select>
                  </div>

                  {/* Scale */}
                  <div>
                    <label className="block text-sm font-medium mb-2 text-slate-300">Production Scale</label>
                    <select
                      value={operationalData.scale}
                      onChange={(e) => handleInputChange('scale', e.target.value)}
                      className="w-full px-4 py-3 bg-slate-700 border border-slate-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-teal-500 text-white"
                    >
                      <option value="">Select scale</option>
                      {SCALES.map(s => (
                        <option key={s} value={s}>{s}</option>
                      ))}
                    </select>
                  </div>

                  {/* Location */}
                  <div>
                    <label className="block text-sm font-medium mb-2 text-slate-300">Facility Location</label>
                    <select
                      value={operationalData.location}
                      onChange={(e) => handleInputChange('location', e.target.value)}
                      className="w-full px-4 py-3 bg-slate-700 border border-slate-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-teal-500 text-white"
                    >
                      <option value="">Select city</option>
                      {LOCATIONS.map(loc => (
                        <option key={loc.city} value={loc.city}>{`${loc.city}, ${loc.state}`}</option>
                      ))}
                    </select>
                  </div>
                  <div>
                    <label className="block text-sm font-medium mb-2 text-slate-300">
                      Units Per Month
                      <span className="text-xs text-slate-400 ml-2">(auto-calculated from scale)</span>
                    </label>
                    <div className="flex gap-2">
                      <input
                        type="number"
                        value={operationalData.units_per_month}
                        onChange={(e) => setOperationalData(prev => ({ ...prev, units_per_month: parseInt(e.target.value) || 1000 }))}
                        placeholder="e.g., 1000"
                        className="flex-1 px-4 py-3 bg-slate-700 border border-slate-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-teal-500 text-white placeholder-slate-400"
                      />
                      <button
                        onClick={() => setOperationalData(prev => ({ 
                          ...prev, 
                          units_per_month: calculateUnitsPerMonth(prev.scale) 
                        }))}
                        className="px-3 py-3 bg-slate-600 hover:bg-slate-500 rounded-lg text-sm font-medium transition-all"
                        title="Reset to auto-calculated value"
                      >
                        Reset
                      </button>
                    </div>
                    <p className="text-xs text-slate-400 mt-1">
                      {operationalData.scale && `Auto value for ${operationalData.scale}: ${calculateUnitsPerMonth(operationalData.scale).toLocaleString()}`}
                    </p>
                  </div>
                </div>
                <button
                  onClick={handlePredictWaste}
                  disabled={!operationalData.industry || loading}
                  className="mt-8 w-full bg-teal-600 hover:bg-teal-700 disabled:bg-slate-600 disabled:cursor-not-allowed px-6 py-4 rounded-lg font-semibold text-lg transition-all flex items-center justify-center gap-2"
                >
                  {loading ? <Loader className="w-5 h-5 animate-spin" /> : <TrendingUp className="w-5 h-5" />}
                  Generate AI Waste Profile
                </button>
                <button
                  onClick={handleSaveForm}
                  className="mt-4 w-full bg-slate-600 hover:bg-slate-700 px-6 py-4 rounded-lg font-semibold text-lg transition-all"
                >
                  Save This Form
                </button>
              </div>
            </div>

            {/* Right Sidebar - Additional Info */}
            <aside className="hidden xl:block w-64 flex-shrink-0">
              <div className="sticky top-6 space-y-4">
                {/* Sustainability Quote */}
               <div className="bg-slate-900/80 border-l-2 border-teal-400 rounded-lg p-4">
  <p className="text-sm text-slate-200 leading-relaxed mb-3">
   Waste is only waste if we waste it
  </p>
  <p className="text-xs text-slate-400">
    — Ellen MacArthur
  </p>
</div>


                {/* Quick Stats */}
                <div className="bg-slate-800 rounded-lg p-4 border border-slate-700">
                  <h4 className="font-bold text-sm mb-3 text-teal-400">Platform Impact</h4>
                  <div className="space-y-3 text-xs">
                    <div>
                      <div className="text-slate-400">Avg Match Score</div>
                      <div className="text-lg font-bold text-white">89%</div>
                    </div>
                    {/* <div>
                      <div className="text-slate-400">Response Time</div>
                      <div className="text-lg font-bold text-white">&lt;2 hrs</div>
                    </div> */}
                    <div>
                      <div className="text-slate-400">Success Rate</div>
                      <div className="text-lg font-bold text-white">94%</div>
                    </div>
                  </div>
                </div>

                {/* Industries Served */}
                <div className="bg-slate-800 rounded-lg p-4 border border-slate-700">
                  <h4 className="font-bold text-sm mb-3 text-teal-400">Industries Served</h4>
                  <div className="flex flex-wrap gap-2">
                    {['Automotive', 'Electronics', 'Textiles', 'Food', 'Metal', 'Chemical'].map(ind => (
                      <span key={ind} className="text-xs bg-teal-900/30 border border-teal-500/50 px-2 py-1 rounded">
                        {ind}
                      </span>
                    ))}
                  </div>
                </div>
              </div>
            </aside>
          </div>
        ) : (
          /* Single Column Layout for Steps 2, 3, 4 - No Sidebars */
          <div className="max-w-4xl mx-auto">
            {/* Step 2: Waste Profile */}
            {step === 2 && wasteProfile && (
              <div className="bg-slate-800 rounded-xl p-8 shadow-2xl">
                <h2 className="text-2xl font-bold mb-6 flex items-center gap-2">
                  <Trash2 className="w-6 h-6 text-teal-400" />
                  Predicted Waste Profile
                </h2>
                <div className="mb-6 p-4 bg-slate-700 rounded-lg">
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-slate-300">AI Confidence Score</span>
                    <span className="text-teal-400 font-bold">{(wasteProfile.confidence * 100).toFixed(0)}%</span>
                  </div>
                  <div className="w-full bg-slate-600 rounded-full h-2">
                    <div className="bg-teal-500 h-2 rounded-full" style={{ width: `${wasteProfile.confidence * 100}%` }} />
                  </div>
                </div>

                <div className="space-y-6">
                  {wasteProfile.wasteTypes.map((waste: WasteType, idx: number) => (
                    <div key={idx} className="bg-slate-700 rounded-lg p-6 border-l-4 border-teal-500">
                      <h3 className="text-xl font-bold mb-4 text-teal-400">{waste.type}</h3>
                      <div className="grid md:grid-cols-2 gap-4">
                        <div>
                          <p className="text-sm text-slate-400">Predicted Quantity</p>
                          <p className="font-semibold">{waste.quantity}</p>
                        </div>
                        <div>
                          <p className="text-sm text-slate-400">Quality Assessment</p>
                          <p className="font-semibold">{waste.quality}</p>
                        </div>
                        <div>
                          <p className="text-sm text-slate-400">Contamination Level</p>
                          <p className="font-semibold">{waste.contamination}</p>
                        </div>
                        <div>
                          <p className="text-sm text-slate-400">Hazard Classification</p>
                          <p className={`font-semibold ${waste.hazardLevel.includes('Non') ? 'text-teal-400' : 'text-yellow-400'}`}>
                            {waste.hazardLevel}
                          </p>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>

                {wasteProfile.regulatoryFlags.length > 0 && (
                  <div className="mt-6 p-4 bg-yellow-900/30 border border-yellow-600 rounded-lg">
                    <h4 className="font-bold flex items-center gap-2 mb-2 text-yellow-400">
                      <AlertTriangle className="w-5 h-5" />
                      Regulatory Requirements
                    </h4>
                    <ul className="space-y-1">
                      {wasteProfile.regulatoryFlags.map((flag: string, idx: number) => (
                        <li key={idx} className="text-sm text-slate-300">• {flag}</li>
                      ))}
                    </ul>
                  </div>
                )}

                <button
                  onClick={handleFindMatches}
                  disabled={loading}
                  className="mt-8 w-full bg-teal-600 hover:bg-teal-700 disabled:bg-slate-600 px-6 py-4 rounded-lg font-semibold text-lg transition-all flex items-center justify-center gap-2"
                >
                  {loading ? <Loader className="w-5 h-5 animate-spin" /> : <TrendingUp className="w-5 h-5" />}
                  Find Circular Matches
                </button>
              </div>
            )}

            {/* Step 3: Matches */}
            {step === 3 && matches.length > 0 && (
              <div className="bg-slate-800 rounded-xl p-8 shadow-2xl">
                <h2 className="text-2xl font-bold mb-6 flex items-center gap-2">
                  <CheckCircle className="w-6 h-6 text-teal-400" />
                  Optimized Matches ({matches.length})
                </h2>
                
                <div className="space-y-6">
                  {matches.map((match: Match) => (
                    <div key={match.id} className="bg-slate-700 rounded-lg p-6 border-l-4 border-teal-500 hover:bg-slate-650 transition-all">
                      <div className="flex justify-between items-start mb-4">
                        <div>
                          <h3 className="text-xl font-bold text-teal-400">{match.company}</h3>
                          <p className="text-slate-400">{match.type}</p>
                        </div>
                        <div className="text-right">
                          <div className="text-3xl font-bold text-teal-400">{match.overallScore}</div>
                          <div className="text-xs text-slate-400">Match Score</div>
                        </div>
                      </div>

                      <div className="grid md:grid-cols-3 gap-4 mb-4">
                        <div className="bg-slate-800 p-3 rounded">
                          <p className="text-xs text-slate-400 mb-1">Material Match</p>
                          <p className="text-lg font-bold">{match.materialMatch}%</p>
                        </div>
                        <div className="bg-slate-800 p-3 rounded">
                          <p className="text-xs text-slate-400 mb-1">Quality Fit</p>
                          <p className="text-lg font-bold">{match.qualityFit}%</p>
                        </div>
                        <div className="bg-slate-800 p-3 rounded">
                          <p className="text-xs text-slate-400 mb-1">Distance</p>
                          <p className="text-lg font-bold">{match.distance} km</p>
                        </div>
                      </div>

                      <div className="grid md:grid-cols-2 gap-4 mb-4">
                        <div>
                          <p className="text-sm text-slate-400 mb-1">Requirements</p>
                          <p className="text-sm">{match.requirements}</p>
                        </div>
                        <div>
                          <p className="text-sm text-slate-400 mb-1">Pricing</p>
                          <p className="text-sm font-semibold text-teal-400">{match.pricing}</p>
                        </div>
                      </div>

                      <div className="bg-teal-900/30 border border-teal-600 rounded p-4">
                        <p className="font-bold mb-2 text-teal-400">Impact Metrics</p>
                        <div className="grid grid-cols-3 gap-4 text-sm">
                          <div>
                            <p className="text-slate-400">Cost Savings</p>
                            <p className="font-bold">₹{(match.costSaving * 83).toLocaleString()}/yr</p>
                          </div>
                          <div>
                            <p className="text-slate-400">CO₂ Avoided</p>
                            <p className="font-bold">{match.environmentalImpact.co2Saved} tons/yr</p>
                          </div>
                          <div>
                            <p className="text-slate-400">Landfill Diverted</p>
                            <p className="font-bold">{match.environmentalImpact.landfillDiverted} tons/yr</p>
                          </div>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>

                <button
                  onClick={handleSendOutreach}
                  disabled={loading}
                  className="mt-8 w-full bg-teal-600 hover:bg-teal-700 disabled:bg-slate-600 px-6 py-4 rounded-lg font-semibold text-lg transition-all flex items-center justify-center gap-2"
                >
                  {loading ? <Loader className="w-5 h-5 animate-spin" /> : <Mail className="w-5 h-5" />}
                  Send Automated Outreach to Top Matches
                </button>
              </div>
            )}

            {/* Step 4: Outreach Confirmation */}
            {step === 4 && outreachSent && (
              <div className="bg-slate-800 rounded-xl p-8 shadow-2xl text-center">
                <CheckCircle className="w-16 h-16 text-teal-400 mx-auto mb-6" />
                <h2 className="text-3xl font-bold mb-4">Outreach Initiated</h2>
                <p className="text-slate-300 mb-8 text-lg">
                  MCP agents have generated and sent personalized deal briefs to {matches.length} potential partners.
                  Responses will be tracked and fed back into the system for continuous improvement.
                </p>
                
                <div className="bg-slate-700 rounded-lg p-6 max-w-2xl mx-auto text-left">
                  <h3 className="font-bold mb-4 text-teal-400">Sample Outreach Email Preview:</h3>
                  <div className="text-sm space-y-3 text-slate-300">
                    <p><strong>To:</strong> partnerships@bharatsteel-recycling.in</p>
                    <p><strong>Subject:</strong> Circular Opportunity: 15-20 tons/month Grade A Steel Scrap</p>
                    <div className="border-l-2 border-teal-500 pl-4 mt-4">
                      <p className="mb-2">Dear Bharat Steel Recycling Team,</p>
                      <p className="mb-2">
                        Our AI matching platform has identified a high-compatibility opportunity between your material requirements 
                        and our facility's waste stream in Pune, Maharashtra.
                      </p>
                      <p className="mb-2"><strong>Opportunity Summary:</strong></p>
                      <p className="mb-2">
                        • Material: Grade A Steel Scrap (95% purity, &lt;2% contamination)<br/>
                        • Volume: 15-20 tons/month<br/>
                        • Match Score: 94/100<br/>
                        • Estimated Value: ₹2,32,400/year cost savings<br/>
                        • Environmental Impact: 12.5 tons CO₂ avoided annually
                      </p>
                      <p>Would you be available for a brief call this week to discuss logistics and pricing?</p>
                    </div>
                  </div>
                </div>

                <button
                  onClick={() => {
                    setStep(1);
                    setWasteProfile(null);
                    setMatches([]);
                    setOutreachSent(false);
                    setOperationalData({ industry: '', product: '', process: '', machinery: '', scale: '', location: '', units_per_month: 1000 });
                  }}
                  className="mt-8 bg-slate-600 hover:bg-slate-700 px-8 py-3 rounded-lg font-semibold transition-all"
                >
                  Start New Analysis
                </button>
              </div>
            )}
          </div>
        )}

        {/* Footer - Now properly positioned */}
        <footer className="mt-auto pt-8 border-t border-slate-700 text-center text-slate-400 max-w-7xl mx-auto w-full">
          <div className="mb-6">
            <h4 className="text-lg font-bold text-teal-400 mb-2">Our Mission</h4>
            <p className="text-sm max-w-2xl mx-auto">
              Accelerating India's transition to a circular economy by making industrial waste management 
              intelligent, profitable, and sustainable. Every connection we facilitate is a step towards 
              zero-waste manufacturing.
            </p>
          </div>
         <div className="flex justify-center gap-6 text-sm mb-4">
  <span className="flex items-center gap-1.5">
    <Sprout className="w-3.5 h-3.5 text-teal-500" />
    <span>Carbon Neutral Platform</span>
  </span>

  <span className="flex items-center gap-1.5">
    <Recycle className="w-3.5 h-3.5 text-teal-500" />
    <span>500+ Tons Diverted</span>
 
  </span>

  <span className="flex items-center gap-1.5">
    <Handshake className="w-3.5 h-3.5 text-teal-500" />
    <span>120+ Active Partners</span> 
  </span>
</div>

          <p className="text-xs">© 2026 Circular Economy Platform. Powering sustainable industry.</p>
          <p className="text-xs">© CodeCraft Technologies.</p>
        </footer>
      </div>
    </div>
  );
};

export default WasteCircularPlatform;
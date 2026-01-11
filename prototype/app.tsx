import React, { useState } from 'react';
import { Trash2, Factory, TrendingUp, Mail, AlertTriangle, CheckCircle, Loader } from 'lucide-react';

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
    location: ''
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

  const handleInputChange = (field: string, value: string) => {
    setOperationalData(prev => ({ ...prev, [field]: value }));
  };

  const handleGenerateProfile = async () => {
    await inferWasteProfile(operationalData);
    setStep(2);
  };

  const handleFindMatches = async () => {
    if (wasteProfile) {
      await findMatches(wasteProfile);
      setStep(3);
    }
  };

  const handleSendOutreach = async () => {
    await sendOutreach();
    setStep(4);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900 text-white p-6">
      <div className="max-w-6xl mx-auto">
        {/* Header */}
        <div className="text-center mb-8">
          <div className="flex items-center justify-center gap-3 mb-4">
            <Factory className="w-12 h-12 text-emerald-400" />
            <h1 className="text-4xl font-bold">Circular Economy Platform</h1>
          </div>
          <p className="text-slate-300 text-lg">AI-Powered Industrial Waste Matching & Optimization</p>
        </div>

        {/* Progress Steps */}
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
                  step >= s.num ? 'bg-emerald-500' : 'bg-slate-700'
                }`}>
                  {s.num}
                </div>
                <span className="text-xs mt-2">{s.label}</span>
              </div>
              {i < 3 && <div className={`h-0.5 w-20 mx-2 ${step > s.num ? 'bg-emerald-500' : 'bg-slate-700'}`} />}
            </div>
          ))}
        </div>

        {/* Step 1: Input Operational Data */}
        {step === 1 && (
          <div className="bg-slate-800 rounded-xl p-8 shadow-2xl">
            <h2 className="text-2xl font-bold mb-6 flex items-center gap-2">
              <Factory className="w-6 h-6 text-emerald-400" />
              Operational Input
            </h2>
            <div className="grid md:grid-cols-2 gap-6">
              {[
                { field: 'industry', label: 'Industry Sector', placeholder: 'e.g., Automotive Manufacturing' },
                { field: 'product', label: 'Primary Product', placeholder: 'e.g., Engine Components' },
                { field: 'process', label: 'Manufacturing Process', placeholder: 'e.g., CNC Machining, Assembly' },
                { field: 'machinery', label: 'Key Machinery', placeholder: 'e.g., Lathes, Milling Machines' },
                { field: 'scale', label: 'Production Scale', placeholder: 'e.g., 5000 units/month' },
                { field: 'location', label: 'Facility Location', placeholder: 'e.g., Pune, Maharashtra' }
              ].map(({ field, label, placeholder }) => (
                <div key={field}>
                  <label className="block text-sm font-medium mb-2 text-slate-300">{label}</label>
                  <input
                    type="text"
                    value={operationalData[field as keyof typeof operationalData]}
                    onChange={(e) => handleInputChange(field, e.target.value)}
                    placeholder={placeholder}
                    className="w-full px-4 py-3 bg-slate-700 border border-slate-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-emerald-500 text-white placeholder-slate-400"
                  />
                </div>
              ))}
            </div>
            <button
              onClick={handleGenerateProfile}
              disabled={!operationalData.industry || loading}
              className="mt-8 w-full bg-emerald-600 hover:bg-emerald-700 disabled:bg-slate-600 disabled:cursor-not-allowed px-6 py-4 rounded-lg font-semibold text-lg transition-all flex items-center justify-center gap-2"
            >
              {loading ? <Loader className="w-5 h-5 animate-spin" /> : <TrendingUp className="w-5 h-5" />}
              Generate AI Waste Profile
            </button>
          </div>
        )}

        {/* Step 2: Waste Profile */}
        {step === 2 && wasteProfile && (
          <div className="bg-slate-800 rounded-xl p-8 shadow-2xl">
            <h2 className="text-2xl font-bold mb-6 flex items-center gap-2">
              <Trash2 className="w-6 h-6 text-emerald-400" />
              Predicted Waste Profile
            </h2>
            <div className="mb-6 p-4 bg-slate-700 rounded-lg">
              <div className="flex items-center justify-between mb-2">
                <span className="text-slate-300">AI Confidence Score</span>
                <span className="text-emerald-400 font-bold">{(wasteProfile.confidence * 100).toFixed(0)}%</span>
              </div>
              <div className="w-full bg-slate-600 rounded-full h-2">
                <div className="bg-emerald-500 h-2 rounded-full" style={{ width: `${wasteProfile.confidence * 100}%` }} />
              </div>
            </div>

            <div className="space-y-6">
              {wasteProfile.wasteTypes.map((waste: WasteType, idx: number) => (
                <div key={idx} className="bg-slate-700 rounded-lg p-6 border-l-4 border-emerald-500">
                  <h3 className="text-xl font-bold mb-4 text-emerald-400">{waste.type}</h3>
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
                      <p className={`font-semibold ${waste.hazardLevel.includes('Non') ? 'text-emerald-400' : 'text-yellow-400'}`}>
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
              className="mt-8 w-full bg-emerald-600 hover:bg-emerald-700 disabled:bg-slate-600 px-6 py-4 rounded-lg font-semibold text-lg transition-all flex items-center justify-center gap-2"
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
              <CheckCircle className="w-6 h-6 text-emerald-400" />
              Optimized Matches ({matches.length})
            </h2>
            
            <div className="space-y-6">
              {matches.map((match: Match) => (
                <div key={match.id} className="bg-slate-700 rounded-lg p-6 border-l-4 border-emerald-500 hover:bg-slate-650 transition-all">
                  <div className="flex justify-between items-start mb-4">
                    <div>
                      <h3 className="text-xl font-bold text-emerald-400">{match.company}</h3>
                      <p className="text-slate-400">{match.type}</p>
                    </div>
                    <div className="text-right">
                      <div className="text-3xl font-bold text-emerald-400">{match.overallScore}</div>
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
                      <p className="text-sm font-semibold text-emerald-400">{match.pricing}</p>
                    </div>
                  </div>

                  <div className="bg-emerald-900/30 border border-emerald-600 rounded p-4">
                    <p className="font-bold mb-2 text-emerald-400">Impact Metrics</p>
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
              className="mt-8 w-full bg-emerald-600 hover:bg-emerald-700 disabled:bg-slate-600 px-6 py-4 rounded-lg font-semibold text-lg transition-all flex items-center justify-center gap-2"
            >
              {loading ? <Loader className="w-5 h-5 animate-spin" /> : <Mail className="w-5 h-5" />}
              Send Automated Outreach to Top Matches
            </button>
          </div>
        )}

        {/* Step 4: Outreach Confirmation */}
        {step === 4 && outreachSent && (
          <div className="bg-slate-800 rounded-xl p-8 shadow-2xl text-center">
            <CheckCircle className="w-16 h-16 text-emerald-400 mx-auto mb-6" />
            <h2 className="text-3xl font-bold mb-4">Outreach Initiated</h2>
            <p className="text-slate-300 mb-8 text-lg">
              MCP agents have generated and sent personalized deal briefs to {matches.length} potential partners.
              Responses will be tracked and fed back into the system for continuous improvement.
            </p>
            
            <div className="bg-slate-700 rounded-lg p-6 max-w-2xl mx-auto text-left">
              <h3 className="font-bold mb-4 text-emerald-400">Sample Outreach Email Preview:</h3>
              <div className="text-sm space-y-3 text-slate-300">
                <p><strong>To:</strong> partnerships@bharatsteel-recycling.in</p>
                <p><strong>Subject:</strong> Circular Opportunity: 15-20 tons/month Grade A Steel Scrap</p>
                <div className="border-l-2 border-emerald-500 pl-4 mt-4">
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
                setOperationalData({ industry: '', product: '', process: '', machinery: '', scale: '', location: '' });
              }}
              className="mt-8 bg-slate-600 hover:bg-slate-700 px-8 py-3 rounded-lg font-semibold transition-all"
            >
              Start New Analysis
            </button>
          </div>
        )}
      </div>
    </div>
  );
};

export default WasteCircularPlatform;
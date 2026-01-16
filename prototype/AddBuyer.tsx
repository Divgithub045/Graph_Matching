import React, { useState } from 'react';
import { Plus, ArrowLeft, CheckCircle, Loader } from 'lucide-react';
import { LOCATIONS } from './data';

interface BuyerFormData {
  company_name: string;
  company_type: string;
  accepted_waste_types: string;
  accepted_categories: string;
  min_quality_grade: string;
  min_monthly_volume_tons: number;
  max_monthly_volume_tons: number;
  city: string;
  state: string;
  lat: number;
  lng: number;
  pricing_model: string;
  certifications: string;
  contact_email: string;
  contact_name: string;
}

const COMPANY_TYPES = [
  'Hazardous Waste Facility',
  'Waste Broker',
  'Wire Manufacturer',
  'Recycling Facility',
  'Metal Recycler',
  'Plastic Recycler',
  'E-Waste Processor',
  'Oil Reclamation Unit',
  'Chemical Processor'
];

const WASTE_CATEGORIES = [
  'hazardous',
  'mixed',
  'metal',
  'plastic',
  'electronic',
  'organic',
  'chemical'
];

const QUALITY_GRADES = [
  'Grade A',
  'Grade B',
  'Grade C',
  'Clean',
  'Contaminated'
];

const CERTIFICATIONS = [
  'CPCB_Auth',
  'SPCB_Auth',
  'MoEFCC',
  'ISO_14001',
  'ISO_9001'
];

const AddBuyer = ({ onBack }: { onBack: () => void }) => {
  const [formData, setFormData] = useState<BuyerFormData>({
    company_name: '',
    company_type: '',
    accepted_waste_types: '',
    accepted_categories: '',
    min_quality_grade: '',
    min_monthly_volume_tons: 1,
    max_monthly_volume_tons: 100,
    city: '',
    state: '',
    lat: 0,
    lng: 0,
    pricing_model: '',
    certifications: '',
    contact_email: '',
    contact_name: ''
  });

  const [selectedCertifications, setSelectedCertifications] = useState<string[]>([]);
  const [loading, setLoading] = useState(false);
  const [success, setSuccess] = useState(false);

  const handleLocationChange = (city: string) => {
    const location = LOCATIONS.find(loc => loc.city === city);
    if (location) {
      setFormData(prev => ({
        ...prev,
        city: location.city,
        state: location.state,
        lat: location.lat,
        lng: location.lng
      }));
    }
  };

  const handleCertificationToggle = (cert: string) => {
    setSelectedCertifications(prev => {
      if (prev.includes(cert)) {
        return prev.filter(c => c !== cert);
      } else {
        return [...prev, cert];
      }
    });
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);

    try {
      // Prepare data with certifications
      const dataToSend = {
        ...formData,
        certifications: selectedCertifications.join(',')
      };

      const response = await fetch('http://localhost:8000/api/add-buyer', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(dataToSend)
      });

      const result = await response.json();

      if (result.success) {
        setSuccess(true);
        setTimeout(() => {
          onBack();
        }, 2000);
      } else {
        alert('Error adding buyer: ' + (result.message || 'Unknown error'));
      }
    } catch (error) {
      console.error('Error adding buyer:', error);
      alert('Error adding buyer. Check console for details.');
    } finally {
      setLoading(false);
    }
  };

  if (success) {
    return (
      <div className="min-h-screen bg-gradient-to-b from-slate-950 via-slate-900 to-slate-950 text-white p-6 flex items-center justify-center">
        <div className="text-center">
          <CheckCircle className="w-20 h-20 text-teal-400 mx-auto mb-6" />
          <h2 className="text-3xl font-bold mb-4">Buyer Added Successfully!</h2>
          <p className="text-slate-300">Redirecting back to main page...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-b from-slate-950 via-slate-900 to-slate-950 text-white p-6">
      <div className="max-w-4xl mx-auto">
        {/* Header */}
        <button
          onClick={onBack}
          className="mb-6 flex items-center gap-2 text-teal-400 hover:text-teal-300 transition-colors"
        >
          <ArrowLeft className="w-5 h-5" />
          Back to Main
        </button>

        <div className="bg-slate-800 rounded-xl p-8 shadow-2xl">
          <h1 className="text-3xl font-bold mb-2 flex items-center gap-3">
            <Plus className="w-8 h-8 text-teal-400" />
            Add New Buyer
          </h1>
          <p className="text-slate-400 mb-8">Register a new waste buyer in the database</p>

          <form onSubmit={handleSubmit} className="space-y-6">
            {/* Company Information */}
            <div className="space-y-4">
              <h3 className="text-xl font-semibold text-teal-400">Company Information</h3>
              
              <div className="grid md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium mb-2 text-slate-300">Company Name *</label>
                  <input
                    type="text"
                    required
                    value={formData.company_name}
                    onChange={(e) => setFormData({ ...formData, company_name: e.target.value })}
                    className="w-full px-4 py-3 bg-slate-700 border border-slate-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-teal-500 text-white"
                    placeholder="e.g., Green Recyclers Pvt Ltd"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium mb-2 text-slate-300">Company Type *</label>
                  <select
                    required
                    value={formData.company_type}
                    onChange={(e) => setFormData({ ...formData, company_type: e.target.value })}
                    className="w-full px-4 py-3 bg-slate-700 border border-slate-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-teal-500 text-white"
                  >
                    <option value="">Select type</option>
                    {COMPANY_TYPES.map(type => (
                      <option key={type} value={type}>{type}</option>
                    ))}
                  </select>
                </div>
              </div>
            </div>

            {/* Waste Acceptance Criteria */}
            <div className="space-y-4">
              <h3 className="text-xl font-semibold text-teal-400">Waste Acceptance Criteria</h3>
              
              <div>
                <label className="block text-sm font-medium mb-2 text-slate-300">Accepted Waste Types *</label>
                <input
                  type="text"
                  required
                  value={formData.accepted_waste_types}
                  onChange={(e) => setFormData({ ...formData, accepted_waste_types: e.target.value })}
                  className="w-full px-4 py-3 bg-slate-700 border border-slate-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-teal-500 text-white"
                  placeholder="e.g., metal_scrap,plastic_waste,batteries (comma-separated)"
                />
              </div>

              <div className="grid md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium mb-2 text-slate-300">Accepted Category *</label>
                  <select
                    required
                    value={formData.accepted_categories}
                    onChange={(e) => setFormData({ ...formData, accepted_categories: e.target.value })}
                    className="w-full px-4 py-3 bg-slate-700 border border-slate-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-teal-500 text-white"
                  >
                    <option value="">Select category</option>
                    {WASTE_CATEGORIES.map(cat => (
                      <option key={cat} value={cat}>{cat}</option>
                    ))}
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-medium mb-2 text-slate-300">Min Quality Grade *</label>
                  <select
                    required
                    value={formData.min_quality_grade}
                    onChange={(e) => setFormData({ ...formData, min_quality_grade: e.target.value })}
                    className="w-full px-4 py-3 bg-slate-700 border border-slate-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-teal-500 text-white"
                  >
                    <option value="">Select grade</option>
                    {QUALITY_GRADES.map(grade => (
                      <option key={grade} value={grade}>{grade}</option>
                    ))}
                  </select>
                </div>
              </div>

              <div className="grid md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium mb-2 text-slate-300">Min Monthly Volume (tons) *</label>
                  <input
                    type="number"
                    required
                    min="0"
                    value={formData.min_monthly_volume_tons}
                    onChange={(e) => setFormData({ ...formData, min_monthly_volume_tons: parseInt(e.target.value) })}
                    className="w-full px-4 py-3 bg-slate-700 border border-slate-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-teal-500 text-white"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium mb-2 text-slate-300">Max Monthly Volume (tons) *</label>
                  <input
                    type="number"
                    required
                    min="0"
                    value={formData.max_monthly_volume_tons}
                    onChange={(e) => setFormData({ ...formData, max_monthly_volume_tons: parseInt(e.target.value) })}
                    className="w-full px-4 py-3 bg-slate-700 border border-slate-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-teal-500 text-white"
                  />
                </div>
              </div>
            </div>

            {/* Location */}
            <div className="space-y-4">
              <h3 className="text-xl font-semibold text-teal-400">Location</h3>
              
              <div>
                <label className="block text-sm font-medium mb-2 text-slate-300">City *</label>
                <select
                  required
                  value={formData.city}
                  onChange={(e) => handleLocationChange(e.target.value)}
                  className="w-full px-4 py-3 bg-slate-700 border border-slate-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-teal-500 text-white"
                >
                  <option value="">Select city</option>
                  {LOCATIONS.map(loc => (
                    <option key={loc.city} value={loc.city}>{loc.city}, {loc.state}</option>
                  ))}
                </select>
              </div>
            </div>

            {/* Pricing & Certifications */}
            <div className="space-y-4">
              <h3 className="text-xl font-semibold text-teal-400">Pricing & Certifications</h3>
              
              <div>
                <label className="block text-sm font-medium mb-2 text-slate-300">Pricing Model *</label>
                <input
                  type="text"
                  required
                  value={formData.pricing_model}
                  onChange={(e) => setFormData({ ...formData, pricing_model: e.target.value })}
                  className="w-full px-4 py-3 bg-slate-700 border border-slate-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-teal-500 text-white"
                  placeholder="e.g., Market_Rate or Collection_Fee: ₹1500-2000/ton"
                />
              </div>

              <div>
                <label className="block text-sm font-medium mb-2 text-slate-300">Certifications</label>
                <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
                  {CERTIFICATIONS.map(cert => (
                    <label
                      key={cert}
                      className="flex items-center gap-2 p-3 bg-slate-700 rounded-lg cursor-pointer hover:bg-slate-600 transition-colors"
                    >
                      <input
                        type="checkbox"
                        checked={selectedCertifications.includes(cert)}
                        onChange={() => handleCertificationToggle(cert)}
                        className="w-4 h-4 text-teal-500 bg-slate-600 border-slate-500 rounded focus:ring-teal-500"
                      />
                      <span className="text-sm">{cert}</span>
                    </label>
                  ))}
                </div>
              </div>
            </div>

            {/* Contact Information */}
            <div className="space-y-4">
              <h3 className="text-xl font-semibold text-teal-400">Contact Information</h3>
              
              <div className="grid md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium mb-2 text-slate-300">Contact Name *</label>
                  <input
                    type="text"
                    required
                    value={formData.contact_name}
                    onChange={(e) => setFormData({ ...formData, contact_name: e.target.value })}
                    className="w-full px-4 py-3 bg-slate-700 border border-slate-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-teal-500 text-white"
                    placeholder="e.g., John Doe"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium mb-2 text-slate-300">Contact Email *</label>
                  <input
                    type="email"
                    required
                    value={formData.contact_email}
                    onChange={(e) => setFormData({ ...formData, contact_email: e.target.value })}
                    className="w-full px-4 py-3 bg-slate-700 border border-slate-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-teal-500 text-white"
                    placeholder="e.g., contact@company.com"
                  />
                </div>
              </div>
            </div>

            {/* Submit Button */}
            <button
              type="submit"
              disabled={loading}
              className="w-full bg-teal-600 hover:bg-teal-700 disabled:bg-slate-600 disabled:cursor-not-allowed px-6 py-4 rounded-lg font-semibold text-lg transition-all flex items-center justify-center gap-2"
            >
              {loading ? (
                <>
                  <Loader className="w-5 h-5 animate-spin" />
                  Adding Buyer...
                </>
              ) : (
                <>
                  <Plus className="w-5 h-5" />
                  Add Buyer to Database
                </>
              )}
            </button>
          </form>
        </div>
      </div>
    </div>
  );
};

export default AddBuyer;

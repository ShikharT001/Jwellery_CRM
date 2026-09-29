'use client';

import { useState, useEffect } from 'react';
import { Package, Plus, Search, Filter, Sparkles, Scale, Gem, ShieldCheck, Eye, Trash2 } from 'lucide-react';
import { apiClient } from '@/lib/api/client';
import toast from 'react-hot-toast';

export const dynamic = 'force-dynamic';

export default function InventoryPage() {
  const [items, setItems] = useState([]);
  const [loading, setLoading] = useState(false);
  const [showModal, setShowModal] = useState(false);

  const [search, setSearch] = useState('');
  const [categoryFilter, setCategoryFilter] = useState('');
  const [metalFilter, setMetalFilter] = useState('');

  // Form Fields
  const [name, setName] = useState('');
  const [sku, setSku] = useState('');
  const [category, setCategory] = useState('Ring');
  const [metalType, setMetalType] = useState('Gold');
  const [purity, setPurity] = useState('22K');
  const [purityPercentage, setPurityPercentage] = useState('91.6');
  const [grossWeight, setGrossWeight] = useState('');
  const [netWeight, setNetWeight] = useState('');
  const [stoneWeight, setStoneWeight] = useState('0');
  const [makingChargeType, setMakingChargeType] = useState('per_gram');
  const [makingChargeRate, setMakingChargeRate] = useState('');
  const [quantity, setQuantity] = useState('1');
  const [saving, setSaving] = useState(false);

  // Auto-calculate Net Weight and Purity % on input changes
  useEffect(() => {
    const gross = parseFloat(grossWeight) || 0;
    const stone = parseFloat(stoneWeight) || 0;
    if (gross > 0) {
      setNetWeight(Math.max(0, gross - stone).toFixed(3));
    }
  }, [grossWeight, stoneWeight]);

  useEffect(() => {
    if (metalType === 'Gold') {
      if (purity === '24K') setPurityPercentage('99.9');
      else if (purity === '22K') setPurityPercentage('91.6');
      else if (purity === '18K') setPurityPercentage('75.0');
      else if (purity === '14K') setPurityPercentage('58.5');
    } else if (metalType === 'Silver') {
      setPurityPercentage('92.5');
    } else if (metalType === 'Platinum') {
      setPurityPercentage('95.0');
    }
  }, [purity, metalType]);

  const handleAddItem = (e) => {
    e.preventDefault();
    setSaving(true);
    
    // Create new item object
    const gross = parseFloat(grossWeight) || 0;
    const net = parseFloat(netWeight) || gross;
    const purPct = parseFloat(purityPercentage) || 91.6;
    const fine = parseFloat((net * (purPct / 100.0)).toFixed(3));

    const newItem = {
      id: Math.random().toString(),
      sku: sku || `JWL-${metalType.charAt(0)}-${Math.floor(10000 + Math.random() * 90000)}`,
      name,
      category,
      metal_type: metalType,
      purity,
      purity_percentage: purPct,
      gross_weight: gross,
      net_weight: net,
      fine_weight: fine,
      stone_weight: parseFloat(stoneWeight) || 0,
      making_charge_type: makingChargeType,
      making_charge_rate: parseFloat(makingChargeRate) || 0,
      quantity: parseInt(quantity) || 1,
      status: 'in_stock',
      created_at: new Date().toISOString(),
    };

    setItems([newItem, ...items]);
    toast.success(`Inventory Item '${name}' added successfully!`);
    
    // Reset Form
    setShowModal(false);
    setName('');
    setSku('');
    setGrossWeight('');
    setNetWeight('');
    setStoneWeight('0');
    setMakingChargeRate('');
    setSaving(false);
  };

  // Filtered items
  const filteredItems = items.filter((item) => {
    const matchesSearch = search ? item.name.toLowerCase().includes(search.toLowerCase()) || item.sku.toLowerCase().includes(search.toLowerCase()) : true;
    const matchesCategory = categoryFilter ? item.category === categoryFilter : true;
    const matchesMetal = metalFilter ? item.metal_type === metalFilter : true;
    return matchesSearch && matchesCategory && matchesMetal;
  });

  // Calculate Metrics
  const totalGrossWeight = filteredItems.reduce((acc, item) => acc + (item.gross_weight * item.quantity), 0).toFixed(3);
  const totalFineWeight = filteredItems.reduce((acc, item) => acc + (item.fine_weight * item.quantity), 0).toFixed(3);

  return (
    <div className="space-y-8 max-w-7xl mx-auto">
      {/* Top Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-display font-bold text-white flex items-center gap-3">
            <Package className="w-8 h-8 text-brand-light" /> Inventory Management
          </h1>
          <p className="text-gray-400 mt-1 text-sm">Real-time stock tracking, fine weight calculation, and tag management</p>
        </div>
        <button
          onClick={() => setShowModal(true)}
          className="px-5 py-2.5 bg-gradient-gold text-white font-medium rounded-lg hover:shadow-lg hover:shadow-brand/20 transition-all flex items-center gap-2 active:scale-95"
        >
          <Plus className="w-5 h-5" /> Add New Item
        </button>
      </div>

      {/* Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <div className="glass-card p-6 flex items-center justify-between">
          <div>
            <p className="text-xs font-medium text-gray-400 uppercase tracking-wider">Total Items Stock</p>
            <h3 className="text-3xl font-bold text-white mt-1">{filteredItems.length}</h3>
          </div>
          <div className="w-12 h-12 rounded-xl bg-brand/10 border border-brand/20 flex items-center justify-center text-brand-light">
            <Package className="w-6 h-6" />
          </div>
        </div>

        <div className="glass-card p-6 flex items-center justify-between">
          <div>
            <p className="text-xs font-medium text-gray-400 uppercase tracking-wider">Total Gross Wt (g)</p>
            <h3 className="text-3xl font-bold text-amber-400 mt-1">{totalGrossWeight} g</h3>
          </div>
          <div className="w-12 h-12 rounded-xl bg-amber-500/10 border border-amber-500/20 flex items-center justify-center text-amber-400">
            <Scale className="w-6 h-6" />
          </div>
        </div>

        <div className="glass-card p-6 flex items-center justify-between">
          <div>
            <p className="text-xs font-medium text-gray-400 uppercase tracking-wider">Fine Metal Wt (g)</p>
            <h3 className="text-3xl font-bold text-emerald-400 mt-1">{totalFineWeight} g</h3>
          </div>
          <div className="w-12 h-12 rounded-xl bg-emerald-500/10 border border-emerald-500/20 flex items-center justify-center text-emerald-400">
            <ShieldCheck className="w-6 h-6" />
          </div>
        </div>

        <div className="glass-card p-6 flex items-center justify-between">
          <div>
            <p className="text-xs font-medium text-gray-400 uppercase tracking-wider">Metal Types</p>
            <h3 className="text-3xl font-bold text-purple-400 mt-1">Gold / Silver</h3>
          </div>
          <div className="w-12 h-12 rounded-xl bg-purple-500/10 border border-purple-500/20 flex items-center justify-center text-purple-400">
            <Gem className="w-6 h-6" />
          </div>
        </div>
      </div>

      {/* Filter Bar */}
      <div className="glass-card p-4 flex flex-col md:flex-row items-center justify-between gap-4">
        <div className="relative flex-1 w-full">
          <Search className="w-4 h-4 text-gray-400 absolute left-3 top-1/2 -translate-y-1/2" />
          <input
            type="text"
            placeholder="Search inventory by Item Name or Tag/SKU..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="glass-input w-full pl-9 pr-4 py-2 text-sm"
          />
        </div>

        <div className="flex items-center gap-3 w-full md:w-auto">
          <select
            value={categoryFilter}
            onChange={(e) => setCategoryFilter(e.target.value)}
            className="glass-input px-4 py-2 text-sm bg-navy text-white"
          >
            <option value="">All Categories</option>
            <option value="Ring">Rings</option>
            <option value="Necklace">Necklaces</option>
            <option value="Chain">Chains</option>
            <option value="Bangle">Bangles</option>
            <option value="Earrings">Earrings</option>
            <option value="Bracelet">Bracelets</option>
            <option value="Coin">Coins / Bars</option>
          </select>

          <select
            value={metalFilter}
            onChange={(e) => setMetalFilter(e.target.value)}
            className="glass-input px-4 py-2 text-sm bg-navy text-white"
          >
            <option value="">All Metals</option>
            <option value="Gold">Gold</option>
            <option value="Silver">Silver</option>
            <option value="Platinum">Platinum</option>
          </select>
        </div>
      </div>

      {/* Inventory Items Table */}
      <div className="glass-card overflow-hidden">
        <table className="w-full text-left text-sm text-gray-300">
          <thead className="bg-white/5 text-xs uppercase font-semibold text-gray-400 border-b border-white/10">
            <tr>
              <th className="py-3.5 px-4">Item Details & SKU</th>
              <th className="py-3.5 px-4">Category</th>
              <th className="py-3.5 px-4">Metal & Purity</th>
              <th className="py-3.5 px-4">Gross Wt (g)</th>
              <th className="py-3.5 px-4">Net Wt (g)</th>
              <th className="py-3.5 px-4">Fine Wt (g)</th>
              <th className="py-3.5 px-4">Making Charges</th>
              <th className="py-3.5 px-4 text-right">Status</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-white/5">
            {filteredItems.length === 0 ? (
              <tr>
                <td colSpan={8} className="py-12 text-center text-gray-400">
                  <div className="flex flex-col items-center space-y-2">
                    <Package className="w-8 h-8 text-gray-500" />
                    <p className="text-sm font-medium">No inventory items found.</p>
                    <p className="text-xs text-gray-500">Click '+ Add New Item' above to add your first stock item.</p>
                  </div>
                </td>
              </tr>
            ) : (
              filteredItems.map((item) => (
                <tr key={item.id} className="hover:bg-white/5 transition-colors">
                  <td className="py-3.5 px-4 font-semibold text-white">
                    {item.name}
                    <p className="text-xs font-mono text-brand-light font-normal mt-0.5">SKU: {item.sku}</p>
                  </td>
                  <td className="py-3.5 px-4">
                    <span className="px-2.5 py-1 rounded-full text-xs font-medium bg-white/5 border border-white/10">
                      {item.category}
                    </span>
                  </td>
                  <td className="py-3.5 px-4 text-xs font-medium">
                    <span className="text-amber-400">{item.metal_type}</span> • {item.purity} ({item.purity_percentage}%)
                  </td>
                  <td className="py-3.5 px-4 font-mono font-medium text-white">{item.gross_weight} g</td>
                  <td className="py-3.5 px-4 font-mono font-medium text-gray-300">{item.net_weight} g</td>
                  <td className="py-3.5 px-4 font-mono font-bold text-emerald-400">{item.fine_weight} g</td>
                  <td className="py-3.5 px-4 text-xs">
                    ₹{item.making_charge_rate} <span className="text-gray-400">/{item.making_charge_type === 'per_gram' ? 'g' : 'fixed'}</span>
                  </td>
                  <td className="py-3.5 px-4 text-right">
                    <span className="px-2.5 py-1 rounded-full text-xs font-medium bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
                      In Stock ({item.quantity})
                    </span>
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>

      {/* Add Item Modal */}
      {showModal && (
        <div className="fixed inset-0 bg-black/75 backdrop-blur-sm z-50 flex items-center justify-center p-4 overflow-y-auto">
          <div className="glass-card w-full max-w-2xl p-6 space-y-6 my-8 animate-fade-in">
            <div className="flex justify-between items-center border-b border-white/10 pb-4">
              <h2 className="text-xl font-bold text-white flex items-center gap-2">
                <Package className="w-6 h-6 text-brand-light" /> Add Jewellery Inventory Item
              </h2>
              <button onClick={() => setShowModal(false)} className="text-gray-400 hover:text-white text-lg">✕</button>
            </div>

            <form onSubmit={handleAddItem} className="space-y-4 text-sm">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="text-xs font-medium text-gray-300">Item Name *</label>
                  <input
                    type="text"
                    placeholder="e.g. 22K Royal Gold Bridal Necklace"
                    value={name}
                    onChange={(e) => setName(e.target.value)}
                    className="glass-input w-full px-3 py-2 mt-1"
                    required
                  />
                </div>
                <div>
                  <label className="text-xs font-medium text-gray-300">Tag / SKU Number (Auto generated if blank)</label>
                  <input
                    type="text"
                    placeholder="JWL-G-88219"
                    value={sku}
                    onChange={(e) => setSku(e.target.value)}
                    className="glass-input w-full px-3 py-2 mt-1 font-mono text-xs"
                  />
                </div>
              </div>

              <div className="grid grid-cols-3 gap-4">
                <div>
                  <label className="text-xs font-medium text-gray-300">Category *</label>
                  <select
                    value={category}
                    onChange={(e) => setCategory(e.target.value)}
                    className="glass-input w-full px-3 py-2 mt-1 bg-navy text-white"
                  >
                    <option value="Ring">Ring</option>
                    <option value="Necklace">Necklace</option>
                    <option value="Chain">Chain</option>
                    <option value="Bangle">Bangle</option>
                    <option value="Earrings">Earrings</option>
                    <option value="Bracelet">Bracelet</option>
                    <option value="Coin">Coin / Bar</option>
                  </select>
                </div>

                <div>
                  <label className="text-xs font-medium text-gray-300">Metal Type *</label>
                  <select
                    value={metalType}
                    onChange={(e) => setMetalType(e.target.value)}
                    className="glass-input w-full px-3 py-2 mt-1 bg-navy text-white"
                  >
                    <option value="Gold">Gold</option>
                    <option value="Silver">Silver</option>
                    <option value="Platinum">Platinum</option>
                  </select>
                </div>

                <div>
                  <label className="text-xs font-medium text-gray-300">Purity *</label>
                  <select
                    value={purity}
                    onChange={(e) => setPurity(e.target.value)}
                    className="glass-input w-full px-3 py-2 mt-1 bg-navy text-white"
                  >
                    {metalType === 'Gold' ? (
                      <>
                        <option value="24K">24K (99.9%)</option>
                        <option value="22K">22K (91.6%)</option>
                        <option value="18K">18K (75.0%)</option>
                        <option value="14K">14K (58.5%)</option>
                      </>
                    ) : metalType === 'Silver' ? (
                      <option value="925 Silver">925 Silver</option>
                    ) : (
                      <option value="950 Platinum">950 Platinum</option>
                    )}
                  </select>
                </div>
              </div>

              {/* Weight Details */}
              <div className="p-4 rounded-xl bg-white/5 border border-white/10 space-y-3">
                <h4 className="text-xs font-bold uppercase text-brand-light tracking-wider">Weight & Fine Weight Metrics</h4>
                <div className="grid grid-cols-3 gap-4">
                  <div>
                    <label className="text-xs text-gray-300">Gross Weight (grams) *</label>
                    <input
                      type="number"
                      step="0.001"
                      placeholder="12.500"
                      value={grossWeight}
                      onChange={(e) => setGrossWeight(e.target.value)}
                      className="glass-input w-full px-3 py-2 mt-1 font-mono font-bold"
                      required
                    />
                  </div>

                  <div>
                    <label className="text-xs text-gray-300">Stone Wt (grams)</label>
                    <input
                      type="number"
                      step="0.001"
                      placeholder="0.500"
                      value={stoneWeight}
                      onChange={(e) => setStoneWeight(e.target.value)}
                      className="glass-input w-full px-3 py-2 mt-1 font-mono"
                    />
                  </div>

                  <div>
                    <label className="text-xs text-gray-300">Net Weight (grams)</label>
                    <input
                      type="number"
                      step="0.001"
                      value={netWeight}
                      onChange={(e) => setNetWeight(e.target.value)}
                      className="glass-input w-full px-3 py-2 mt-1 font-mono text-gray-300"
                      required
                    />
                  </div>
                </div>

                <div className="p-2.5 rounded-lg bg-emerald-500/10 border border-emerald-500/20 text-xs flex justify-between items-center text-emerald-400">
                  <span>Calculated Fine Metal Weight ({purityPercentage}%):</span>
                  <span className="font-mono font-bold text-sm">
                    {((parseFloat(netWeight) || 0) * ((parseFloat(purityPercentage) || 91.6) / 100.0)).toFixed(3)} g
                  </span>
                </div>
              </div>

              {/* Making Charges */}
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="text-xs font-medium text-gray-300">Making Charge Type</label>
                  <select
                    value={makingChargeType}
                    onChange={(e) => setMakingChargeType(e.target.value)}
                    className="glass-input w-full px-3 py-2 mt-1 bg-navy text-white"
                  >
                    <option value="per_gram">Per Gram (₹/g)</option>
                    <option value="fixed">Fixed Amount (₹)</option>
                  </select>
                </div>
                <div>
                  <label className="text-xs font-medium text-gray-300">Making Rate (₹)</label>
                  <input
                    type="number"
                    step="0.01"
                    placeholder="450"
                    value={makingChargeRate}
                    onChange={(e) => setMakingChargeRate(e.target.value)}
                    className="glass-input w-full px-3 py-2 mt-1 font-mono"
                  />
                </div>
              </div>

              <div className="flex gap-3 pt-4 border-t border-white/10">
                <button
                  type="button"
                  onClick={() => setShowModal(false)}
                  className="flex-1 py-2.5 bg-white/5 hover:bg-white/10 text-gray-300 rounded-lg font-medium text-sm"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={saving}
                  className="flex-1 py-2.5 bg-gradient-gold text-white rounded-lg font-medium text-sm shadow-lg shadow-brand/20 active:scale-95 transition-all"
                >
                  {saving ? 'Adding...' : 'Save Inventory Item'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}

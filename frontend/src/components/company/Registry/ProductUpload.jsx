import React, { useState } from 'react';
import Card from '../../common/Card';
import Button from '../../common/Button';
import Icon from '../../common/Icon';

const ProductUpload = ({ onClose }) => {
  const [formData, setFormData] = useState({
    name: '',
    nafdacNumber: '',
    category: '',
    manufacturer: '',
    expiryDate: ''
  });

  const handleSubmit = (e) => {
    e.preventDefault();
    // Handle submission
    onClose();
  };

  return (
    <Card className="max-w-2xl mx-auto">
      <div className="flex justify-between items-center mb-6">
        <h2 className="text-xl font-bold">Register New Product</h2>
        <button onClick={onClose} className="p-2 hover:bg-gray-100 rounded-lg">
          <Icon name="X" size={20} />
        </button>
      </div>

      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label className="text-sm text-gray-500 mb-1 block">Product Name</label>
          <input
            type="text"
            value={formData.name}
            onChange={(e) => setFormData({...formData, name: e.target.value})}
            className="w-full px-4 py-2 border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary/20"
            required
          />
        </div>

        <div>
          <label className="text-sm text-gray-500 mb-1 block">NAFDAC Number</label>
          <input
            type="text"
            value={formData.nafdacNumber}
            onChange={(e) => setFormData({...formData, nafdacNumber: e.target.value})}
            className="w-full px-4 py-2 border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary/20"
            placeholder="e.g., B1-4022-XP"
            required
          />
        </div>

        <div>
          <label className="text-sm text-gray-500 mb-1 block">Category</label>
          <select
            value={formData.category}
            onChange={(e) => setFormData({...formData, category: e.target.value})}
            className="w-full px-4 py-2 border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary/20"
            required
          >
            <option value="">Select Category</option>
            <option value="pharmaceuticals">Pharmaceuticals</option>
            <option value="food">Food & Beverages</option>
            <option value="cosmetics">Cosmetics</option>
          </select>
        </div>

        <div>
          <label className="text-sm text-gray-500 mb-1 block">Manufacturer</label>
          <input
            type="text"
            value={formData.manufacturer}
            onChange={(e) => setFormData({...formData, manufacturer: e.target.value})}
            className="w-full px-4 py-2 border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary/20"
            required
          />
        </div>

        <div>
          <label className="text-sm text-gray-500 mb-1 block">Expiry Date</label>
          <input
            type="date"
            value={formData.expiryDate}
            onChange={(e) => setFormData({...formData, expiryDate: e.target.value})}
            className="w-full px-4 py-2 border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary/20"
            required
          />
        </div>

        <div>
          <label className="text-sm text-gray-500 mb-1 block">Master Artwork</label>
          <div className="border-2 border-dashed border-gray-200 rounded-lg p-8 text-center hover:border-primary transition-colors cursor-pointer">
            <Icon name="Upload" size={24} className="mx-auto mb-2 text-gray-400" />
            <p className="text-sm text-gray-500">Click to upload or drag and drop</p>
            <p className="text-xs text-gray-400 mt-1">PNG, JPG up to 10MB</p>
          </div>
        </div>

        <div className="flex gap-3 pt-4">
          <Button type="submit" variant="primary" fullWidth>
            Register Product
          </Button>
          <Button type="button" variant="outline" onClick={onClose}>
            Cancel
          </Button>
        </div>
      </form>
    </Card>
  );
};

export default ProductUpload;
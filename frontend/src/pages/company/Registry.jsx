import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import CompanySidebar from '../../components/layout/CompanySidebar';
import ProductList from '../../components/company/Registry/ProductList';
import ProductUpload from '../../components/company/Registry/ProductUpload';
import Button from '../../components/common/Button';
import Icon from '../../components/common/Icon';
import Card from '../../components/common/Card';
import MobileCompanyNav from '../../components/layout/MobileCompanyNav';

const Registry = () => {
  const navigate = useNavigate();
  const [showUpload, setShowUpload] = useState(false);
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);
  const [windowWidth, setWindowWidth] = useState(typeof window !== 'undefined' ? window.innerWidth : 0);
  const [searchTerm, setSearchTerm] = useState('');
  const [filterStatus, setFilterStatus] = useState('all');

  useEffect(() => {
    const handleResize = () => {
      setWindowWidth(window.innerWidth);
    };
    
    window.addEventListener('resize', handleResize);
    return () => window.removeEventListener('resize', handleResize);
  }, []);

  // Mock stats - in real app, these would come from API
  const stats = {
    total: 156,
    active: 142,
    pending: 14,
    expired: 8
  };

  return (
    <div className="min-h-screen bg-background">
      {/* Mobile Header */}
      {windowWidth < 768 && (
        <div className="fixed top-0 left-0 right-0 bg-white shadow-soft z-40 px-4 py-3">
          <div className="flex items-center justify-between">
            <button 
              onClick={() => setIsMobileMenuOpen(true)}
              className="p-2 hover:bg-gray-100 rounded-lg"
            >
              <Icon name="Menu" size={24} className="text-gray-600" library="fi" />
            </button>
            <div className="flex items-center gap-2">
              <div className="w-8 h-8 bg-primary/10 rounded-lg flex items-center justify-center">
                <Icon name="Package" size={16} className="text-primary" library="fi" />
              </div>
              <span className="font-bold text-lg">Product Registry</span>
            </div>
            <button 
              onClick={() => setShowUpload(true)}
              className="p-2 bg-primary text-white rounded-lg"
            >
              <Icon name="Plus" size={20} library="fi" />
            </button>
          </div>
        </div>
      )}

      {/* Mobile Menu */}
      <MobileCompanyNav 
        isOpen={isMobileMenuOpen} 
        onClose={() => setIsMobileMenuOpen(false)}
      />

      {/* Desktop Sidebar */}
      {windowWidth >= 768 && <CompanySidebar />}
      
      {/* Main Content */}
      <div className={`${windowWidth >= 768 ? 'lg:ml-64' : ''} ${windowWidth < 768 ? 'pt-16' : 'pt-8'} px-4 md:px-6 lg:px-8 pb-8`}>
        {/* Header */}
        <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4 mb-6">
          <h1 className="text-xl md:text-2xl font-bold text-gray-900">Product Registry</h1>
          
          {windowWidth >= 768 && (
            <Button
              variant="primary"
              icon="Plus"
              onClick={() => setShowUpload(true)}
            >
              Register New Product
            </Button>
          )}
        </div>

        {/* Stats Cards - Responsive Grid */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-3 md:gap-4 mb-6">
          <Card className="p-3 md:p-4">
            <p className="text-xs md:text-sm text-gray-400 mb-1">Total Products</p>
            <p className="text-lg md:text-2xl font-bold text-primary">{stats.total}</p>
          </Card>
          <Card className="p-3 md:p-4">
            <p className="text-xs md:text-sm text-gray-400 mb-1">Active</p>
            <p className="text-lg md:text-2xl font-bold text-success">{stats.active}</p>
          </Card>
          <Card className="p-3 md:p-4">
            <p className="text-xs md:text-sm text-gray-400 mb-1">Pending</p>
            <p className="text-lg md:text-2xl font-bold text-warning">{stats.pending}</p>
          </Card>
          <Card className="p-3 md:p-4">
            <p className="text-xs md:text-sm text-gray-400 mb-1">Expired</p>
            <p className="text-lg md:text-2xl font-bold text-danger">{stats.expired}</p>
          </Card>
        </div>

        {/* Search and Filter Bar */}
        <div className="flex flex-col sm:flex-row gap-3 mb-6">
          <div className="relative flex-1">
            <Icon name="Search" size={18} className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" library="fi" />
            <input
              type="text"
              placeholder="Search products by name or NAFDAC number..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-full pl-10 pr-4 py-3 border border-gray-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-primary/20"
            />
          </div>
          <select
            value={filterStatus}
            onChange={(e) => setFilterStatus(e.target.value)}
            className="px-4 py-3 border border-gray-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-primary/20 bg-white"
          >
            <option value="all">All Status</option>
            <option value="active">Active</option>
            <option value="pending">Pending</option>
            <option value="expired">Expired</option>
          </select>
        </div>

        {/* Main Content Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Product List - Takes 2 columns on desktop */}
          <div className="lg:col-span-2">
            <ProductList 
              searchTerm={searchTerm}
              filterStatus={filterStatus}
            />
          </div>
          
          {/* Quick Stats Sidebar - Hidden on mobile, visible on desktop */}
          {windowWidth >= 1024 && (
            <div className="lg:col-span-1">
              <Card className="sticky top-6">
                <h3 className="font-semibold text-lg mb-4">Quick Stats</h3>
                
                <div className="space-y-4">
                  <div>
                    <p className="text-sm text-gray-500 mb-2">Categories</p>
                    <div className="space-y-2">
                      <div className="flex justify-between text-sm">
                        <span>Pharmaceuticals</span>
                        <span className="font-medium">84</span>
                      </div>
                      <div className="flex justify-between text-sm">
                        <span>Food & Beverages</span>
                        <span className="font-medium">42</span>
                      </div>
                      <div className="flex justify-between text-sm">
                        <span>Cosmetics</span>
                        <span className="font-medium">30</span>
                      </div>
                    </div>
                  </div>
                  
                  <div className="pt-4 border-t border-gray-100">
                    <p className="text-sm text-gray-500 mb-2">Recent Activity</p>
                    <p className="text-xs text-gray-400">Last updated: Today, 10:30 AM</p>
                    <p className="text-xs text-success mt-2">✓ 3 products verified today</p>
                  </div>

                  <div className="pt-4 border-t border-gray-100">
                    <button className="w-full text-primary text-sm font-medium hover:underline">
                      View All Products
                    </button>
                  </div>
                </div>
              </Card>
            </div>
          )}
        </div>

        {/* Mobile Quick Stats */}
        {windowWidth < 1024 && (
          <Card className="mt-6 p-4">
            <h3 className="font-semibold mb-3">Quick Stats</h3>
            <div className="grid grid-cols-2 gap-4">
              <div>
                <p className="text-xs text-gray-400">Pharmaceuticals</p>
                <p className="text-lg font-bold">84</p>
              </div>
              <div>
                <p className="text-xs text-gray-400">Food & Beverages</p>
                <p className="text-lg font-bold">42</p>
              </div>
              <div>
                <p className="text-xs text-gray-400">Cosmetics</p>
                <p className="text-lg font-bold">30</p>
              </div>
              <div>
                <p className="text-xs text-gray-400">Last Updated</p>
                <p className="text-sm font-medium">Today</p>
              </div>
            </div>
          </Card>
        )}

        {/* Upload Modal - Responsive */}
        {showUpload && (
          <ProductUpload 
            onClose={() => setShowUpload(false)} 
            isMobile={windowWidth < 768}
          />
        )}
      </div>
    </div>
  );
};

export default Registry;
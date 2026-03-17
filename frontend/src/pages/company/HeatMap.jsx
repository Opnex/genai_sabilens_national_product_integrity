import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import CompanySidebar from '../../components/layout/CompanySidebar';
import MapView from '../../components/company/HeatMap/MapView';
import MapFilters from '../../components/company/HeatMap/MapFilters';
import Icon from '../../components/common/Icon';
import Card from '../../components/common/Card';
import MobileCompanyNav from '../../components/layout/MobileCompanyNav';

const HeatMap = () => {
  const navigate = useNavigate();
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);
  const [windowWidth, setWindowWidth] = useState(typeof window !== 'undefined' ? window.innerWidth : 0);
  const [showFilters, setShowFilters] = useState(true);
  const [selectedRegion, setSelectedRegion] = useState(null);

  useEffect(() => {
    const handleResize = () => {
      setWindowWidth(window.innerWidth);
      if (window.innerWidth >= 1024) {
        setShowFilters(true);
      }
    };
    
    window.addEventListener('resize', handleResize);
    handleResize();
    
    return () => window.removeEventListener('resize', handleResize);
  }, []);

  // Mock data for heat map stats
  const stats = {
    totalHotspots: 23,
    criticalZones: 8,
    highRiskZones: 10,
    mediumRiskZones: 5
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
                <Icon name="Map" size={16} className="text-primary" library="fi" />
              </div>
              <span className="font-bold text-lg">Heat Map</span>
            </div>
            <button 
              onClick={() => setShowFilters(!showFilters)}
              className="p-2 hover:bg-gray-100 rounded-lg"
            >
              <Icon name="Filter" size={20} className="text-gray-600" library="fi" />
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
          <h1 className="text-xl md:text-2xl font-bold text-gray-900">Risk Heat Map</h1>
          
          {/* Legend - Desktop */}
          {windowWidth >= 768 && (
            <div className="flex gap-4 bg-white p-2 rounded-xl shadow-soft">
              <div className="flex items-center gap-2">
                <div className="w-3 h-3 rounded-full bg-danger" />
                <span className="text-xs">Critical</span>
              </div>
              <div className="flex items-center gap-2">
                <div className="w-3 h-3 rounded-full bg-warning" />
                <span className="text-xs">High</span>
              </div>
              <div className="flex items-center gap-2">
                <div className="w-3 h-3 rounded-full bg-primary" />
                <span className="text-xs">Medium</span>
              </div>
              <div className="flex items-center gap-2">
                <div className="w-3 h-3 rounded-full bg-success" />
                <span className="text-xs">Low</span>
              </div>
            </div>
          )}
        </div>

        {/* Stats Cards - Mobile */}
        {windowWidth < 768 && (
          <div className="grid grid-cols-2 gap-3 mb-4">
            <Card className="p-3">
              <p className="text-xs text-gray-400">Hotspots</p>
              <p className="text-lg font-bold text-primary">{stats.totalHotspots}</p>
            </Card>
            <Card className="p-3">
              <p className="text-xs text-gray-400">Critical</p>
              <p className="text-lg font-bold text-danger">{stats.criticalZones}</p>
            </Card>
            <Card className="p-3">
              <p className="text-xs text-gray-400">High Risk</p>
              <p className="text-lg font-bold text-warning">{stats.highRiskZones}</p>
            </Card>
            <Card className="p-3">
              <p className="text-xs text-gray-400">Medium</p>
              <p className="text-lg font-bold text-primary">{stats.mediumRiskZones}</p>
            </Card>
          </div>
        )}

        {/* Main Content Grid */}
        <div className="flex flex-col lg:flex-row gap-6">
          {/* Map Container */}
          <div className={`${showFilters && windowWidth < 1024 ? 'hidden' : 'flex-1'}`}>
            <MapView onRegionSelect={setSelectedRegion} />
          </div>

          {/* Filters Sidebar - Desktop */}
          {windowWidth >= 1024 && (
            <div className="w-80">
              <MapFilters 
                selectedRegion={selectedRegion}
                onRegionChange={setSelectedRegion}
              />
            </div>
          )}

          {/* Filters - Mobile Collapsible */}
          {windowWidth < 1024 && showFilters && (
            <div className="w-full">
              <MapFilters 
                selectedRegion={selectedRegion}
                onRegionChange={setSelectedRegion}
                isMobile={true}
              />
            </div>
          )}
        </div>

        {/* Region Details - Mobile */}
        {selectedRegion && windowWidth < 768 && (
          <Card className="mt-4 p-4">
            <h3 className="font-semibold mb-3">{selectedRegion} Details</h3>
            <div className="space-y-2 text-sm">
              <p>Total Reports: 156</p>
              <p>Counterfeit: 45</p>
              <p>Suspicious: 32</p>
              <p>Last Report: Today, 2:30 PM</p>
            </div>
          </Card>
        )}
      </div>
    </div>
  );
};

export default HeatMap;
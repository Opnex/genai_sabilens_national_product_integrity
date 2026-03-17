import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import Icon from '../../components/common/Icon';
import Card from '../../components/common/Card';
import Button from '../../components/common/Button';
import Modal from '../../components/common/Modal';

const CompanyApprovals = () => {
  const navigate = useNavigate();
  const [companies, setCompanies] = useState([]);
  const [modalOpen, setModalOpen] = useState(false);
  const [modalConfig, setModalConfig] = useState({});

  useEffect(() => {
    loadCompanies();
  }, []);

  const loadCompanies = () => {
    const allCompanies = JSON.parse(localStorage.getItem('companies') || '[]');
    setCompanies(allCompanies);
  };

  const approveCompany = (companyId) => {
    const allCompanies = JSON.parse(localStorage.getItem('companies') || '[]');
    const updatedCompanies = allCompanies.map(company => {
      if (company.id === companyId) {
        company.status = 'approved';
      }
      return company;
    });
    
    localStorage.setItem('companies', JSON.stringify(updatedCompanies));
    loadCompanies();
    
    setModalConfig({
      type: 'success',
      title: 'Company Approved',
      message: 'The company has been approved and can now log in.'
    });
    setModalOpen(true);
  };

  const rejectCompany = (companyId) => {
    const allCompanies = JSON.parse(localStorage.getItem('companies') || '[]');
    const updatedCompanies = allCompanies.map(company => {
      if (company.id === companyId) {
        company.status = 'rejected';
      }
      return company;
    });
    
    localStorage.setItem('companies', JSON.stringify(updatedCompanies));
    loadCompanies();
    
    setModalConfig({
      type: 'warning',
      title: 'Company Rejected',
      message: 'The company application has been rejected.'
    });
    setModalOpen(true);
  };

  const getStatusBadge = (status) => {
    switch(status) {
      case 'approved':
        return <span className="px-2 py-1 bg-success/10 text-success text-xs rounded-full">Approved</span>;
      case 'pending':
        return <span className="px-2 py-1 bg-warning/10 text-warning text-xs rounded-full">Pending</span>;
      case 'rejected':
        return <span className="px-2 py-1 bg-danger/10 text-danger text-xs rounded-full">Rejected</span>;
      default:
        return <span className="px-2 py-1 bg-gray-100 text-gray-500 text-xs rounded-full">{status}</span>;
    }
  };

  return (
    <div className="min-h-screen bg-background p-8">
      <div className="max-w-6xl mx-auto">
        {/* Header */}
        <div className="flex items-center gap-4 mb-8">
          <button
            onClick={() => navigate('/')}
            className="p-2 hover:bg-gray-100 rounded-lg"
          >
            <Icon name="ArrowLeft" size={20} library="fi" />
          </button>
          <h1 className="text-2xl font-bold text-gray-900">Company Approvals</h1>
        </div>

        {/* Companies Table */}
        <Card>
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="border-b border-gray-100">
                  <th className="text-left py-4 px-4 text-sm font-medium text-gray-400">Company</th>
                  <th className="text-left py-4 px-4 text-sm font-medium text-gray-400">Email</th>
                  <th className="text-left py-4 px-4 text-sm font-medium text-gray-400">Registration</th>
                  <th className="text-left py-4 px-4 text-sm font-medium text-gray-400">Location</th>
                  <th className="text-left py-4 px-4 text-sm font-medium text-gray-400">Status</th>
                  <th className="text-left py-4 px-4 text-sm font-medium text-gray-400">Actions</th>
                </tr>
              </thead>
              <tbody>
                {companies.length === 0 ? (
                  <tr>
                    <td colSpan="6" className="text-center py-8 text-gray-400">
                      No companies registered yet
                    </td>
                  </tr>
                ) : (
                  companies.map((company) => (
                    <tr key={company.id} className="border-b border-gray-50 hover:bg-gray-50">
                      <td className="py-4 px-4">
                        <div>
                          <p className="font-medium">{company.name}</p>
                          <p className="text-xs text-gray-400">{company.phone}</p>
                        </div>
                      </td>
                      <td className="py-4 px-4 text-gray-600">{company.email}</td>
                      <td className="py-4 px-4">
                        <p className="text-sm">{company.registrationNumber}</p>
                        <p className="text-xs text-gray-400">ID: {company.id.slice(0, 8)}...</p>
                      </td>
                      <td className="py-4 px-4">
                        <p className="text-sm">{company.city}</p>
                        <p className="text-xs text-gray-400">{company.state}</p>
                      </td>
                      <td className="py-4 px-4">
                        {getStatusBadge(company.status)}
                      </td>
                      <td className="py-4 px-4">
                        <div className="flex gap-2">
                          {company.status === 'pending' && (
                            <>
                              <button
                                onClick={() => approveCompany(company.id)}
                                className="p-2 bg-success/10 text-success rounded-lg hover:bg-success/20"
                                title="Approve"
                              >
                                <Icon name="Check" size={16} library="fi" />
                              </button>
                              <button
                                onClick={() => rejectCompany(company.id)}
                                className="p-2 bg-danger/10 text-danger rounded-lg hover:bg-danger/20"
                                title="Reject"
                              >
                                <Icon name="X" size={16} library="fi" />
                              </button>
                            </>
                          )}
                          {company.status === 'approved' && (
                            <span className="text-xs text-success">Active</span>
                          )}
                          {company.status === 'rejected' && (
                            <span className="text-xs text-danger">Rejected</span>
                          )}
                        </div>
                      </td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
        </Card>

        {/* Quick Actions */}
        <div className="mt-6 grid grid-cols-2 gap-4">
          <Card className="bg-primary/5">
            <h3 className="font-medium mb-2">Quick Approve All</h3>
            <p className="text-sm text-gray-500 mb-3">Approve all pending companies</p>
            <Button
              variant="primary"
              size="sm"
              onClick={() => {
                const allCompanies = JSON.parse(localStorage.getItem('companies') || '[]');
                const updatedCompanies = allCompanies.map(company => ({
                  ...company,
                  status: company.status === 'pending' ? 'approved' : company.status
                }));
                localStorage.setItem('companies', JSON.stringify(updatedCompanies));
                loadCompanies();
                setModalConfig({
                  type: 'success',
                  title: 'All Approved',
                  message: 'All pending companies have been approved.'
                });
                setModalOpen(true);
              }}
            >
              Approve All Pending
            </Button>
          </Card>

          <Card className="bg-gray-50">
            <h3 className="font-medium mb-2">Stats</h3>
            <div className="grid grid-cols-3 gap-2 text-center">
              <div>
                <p className="text-xl font-bold text-warning">
                  {companies.filter(c => c.status === 'pending').length}
                </p>
                <p className="text-xs text-gray-500">Pending</p>
              </div>
              <div>
                <p className="text-xl font-bold text-success">
                  {companies.filter(c => c.status === 'approved').length}
                </p>
                <p className="text-xs text-gray-500">Approved</p>
              </div>
              <div>
                <p className="text-xl font-bold text-danger">
                  {companies.filter(c => c.status === 'rejected').length}
                </p>
                <p className="text-xs text-gray-500">Rejected</p>
              </div>
            </div>
          </Card>
        </div>
      </div>

      {/* Modal */}
      <Modal
        isOpen={modalOpen}
        onClose={() => setModalOpen(false)}
        type={modalConfig.type}
        title={modalConfig.title}
        message={modalConfig.message}
      />
    </div>
  );
};

export default CompanyApprovals;
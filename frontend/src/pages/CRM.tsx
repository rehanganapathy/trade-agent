import React, { useEffect, useState } from 'react';
import {
  Building2,
  Users,
  Package,
  Plus,
} from 'lucide-react';
import { Card, StatCard } from '../components/Card';
import { Button } from '../components/Button';
import { useStore } from '../store/useStore';
import apiService from '../services/api';
import toast from 'react-hot-toast';
import { formatCurrency } from '../utils/export';

const CRM: React.FC = () => {
  const { companies, leads, products, setCompanies, setLeads, setProducts } = useStore();
  const [activeTab, setActiveTab] = useState<'companies' | 'leads' | 'products'>('companies');

  useEffect(() => {
    loadCRMData();
  }, []);

  const loadCRMData = async () => {
    try {
      const [companiesData, leadsData, productsData] = await Promise.all([
        apiService.getCompanies(),
        apiService.getLeads(),
        apiService.getProducts(),
      ]);
      setCompanies(companiesData);
      setLeads(leadsData);
      setProducts(productsData);
    } catch (error) {
      console.error('Error loading CRM data:', error);
      toast.error('Failed to load CRM data');
    }
  };

  const tabs = [
    { id: 'companies' as const, name: 'Companies', icon: Building2, count: companies.length },
    { id: 'leads' as const, name: 'Leads', icon: Users, count: leads.length },
    { id: 'products' as const, name: 'Products', icon: Package, count: products.length },
  ];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-4xl font-bold text-white mb-2">CRM Dashboard</h1>
          <p className="text-white/80">Manage customers, leads, and products</p>
        </div>
        <Button variant="primary" icon={<Plus className="w-5 h-5" />}>
          Add New
        </Button>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <StatCard
          title="Total Companies"
          value={companies.length}
          icon={<Building2 className="w-6 h-6" />}
        />
        <StatCard
          title="Active Leads"
          value={leads.filter((l) => l.status !== 'won' && l.status !== 'lost').length}
          icon={<Users className="w-6 h-6" />}
        />
        <StatCard
          title="Products"
          value={products.length}
          icon={<Package className="w-6 h-6" />}
        />
      </div>

      {/* Tabs */}
      <div className="flex space-x-2 bg-white/10 backdrop-blur-md rounded-lg p-1">
        {tabs.map((tab) => {
          const Icon = tab.icon;
          return (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`
                flex-1 flex items-center justify-center space-x-2 px-4 py-3 rounded-lg
                transition-all duration-200 font-medium
                ${
                  activeTab === tab.id
                    ? 'bg-white text-primary-600 shadow-lg'
                    : 'text-white hover:bg-white/10'
                }
              `}
            >
              <Icon className="w-5 h-5" />
              <span>{tab.name}</span>
              <span
                className={`
                px-2 py-0.5 rounded-full text-xs
                ${
                  activeTab === tab.id
                    ? 'bg-primary-100 text-primary-600'
                    : 'bg-white/20 text-white'
                }
              `}
              >
                {tab.count}
              </span>
            </button>
          );
        })}
      </div>

      {/* Content */}
      <Card>
        {activeTab === 'companies' && (
          <div>
            {companies.length === 0 ? (
              <div className="text-center py-12 text-gray-500">
                <Building2 className="w-16 h-16 mx-auto mb-4 opacity-30" />
                <p className="text-lg">No companies yet</p>
                <p className="text-sm mt-2">Add your first company to get started</p>
              </div>
            ) : (
              <div className="overflow-x-auto">
                <table className="min-w-full divide-y divide-gray-200">
                  <thead className="bg-gray-50">
                    <tr>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                        Name
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                        Type
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                        Status
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                        Country
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                        Contact
                      </th>
                    </tr>
                  </thead>
                  <tbody className="bg-white divide-y divide-gray-200">
                    {companies.map((company) => (
                      <tr key={company.id} className="hover:bg-gray-50">
                        <td className="px-6 py-4 whitespace-nowrap">
                          <div className="text-sm font-medium text-gray-900">
                            {company.name}
                          </div>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap">
                          <span className="px-2 py-1 text-xs font-medium rounded-full bg-blue-100 text-blue-800">
                            {company.company_type || 'N/A'}
                          </span>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap">
                          <span
                            className={`px-2 py-1 text-xs font-medium rounded-full ${
                              company.status === 'active'
                                ? 'bg-green-100 text-green-800'
                                : 'bg-gray-100 text-gray-800'
                            }`}
                          >
                            {company.status || 'N/A'}
                          </span>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                          {company.country || 'N/A'}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                          {company.email || 'N/A'}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </div>
        )}

        {activeTab === 'leads' && (
          <div>
            {leads.length === 0 ? (
              <div className="text-center py-12 text-gray-500">
                <Users className="w-16 h-16 mx-auto mb-4 opacity-30" />
                <p className="text-lg">No leads yet</p>
                <p className="text-sm mt-2">Add your first lead to track opportunities</p>
              </div>
            ) : (
              <div className="overflow-x-auto">
                <table className="min-w-full divide-y divide-gray-200">
                  <thead className="bg-gray-50">
                    <tr>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                        Company
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                        Contact
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                        Status
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                        Value
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                        Source
                      </th>
                    </tr>
                  </thead>
                  <tbody className="bg-white divide-y divide-gray-200">
                    {leads.map((lead) => (
                      <tr key={lead.id} className="hover:bg-gray-50">
                        <td className="px-6 py-4 whitespace-nowrap">
                          <div className="text-sm font-medium text-gray-900">
                            {lead.company_name}
                          </div>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap">
                          <div className="text-sm text-gray-900">{lead.contact_name}</div>
                          <div className="text-xs text-gray-500">{lead.email}</div>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap">
                          <span
                            className={`px-2 py-1 text-xs font-medium rounded-full ${
                              lead.status === 'won'
                                ? 'bg-green-100 text-green-800'
                                : lead.status === 'lost'
                                ? 'bg-red-100 text-red-800'
                                : 'bg-yellow-100 text-yellow-800'
                            }`}
                          >
                            {lead.status || 'new'}
                          </span>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                          {formatCurrency(lead.value)}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                          {lead.source || 'N/A'}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </div>
        )}

        {activeTab === 'products' && (
          <div>
            {products.length === 0 ? (
              <div className="text-center py-12 text-gray-500">
                <Package className="w-16 h-16 mx-auto mb-4 opacity-30" />
                <p className="text-lg">No products yet</p>
                <p className="text-sm mt-2">Add your first product to start tracking inventory</p>
              </div>
            ) : (
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {products.map((product) => (
                  <div
                    key={product.id}
                    className="bg-gray-50 rounded-lg p-4 hover:shadow-md transition-shadow"
                  >
                    <div className="flex items-start justify-between">
                      <div className="flex-1">
                        <h4 className="font-semibold text-gray-900">{product.name}</h4>
                        <p className="text-xs text-gray-500 mt-1">
                          HS Code: {product.hs_code || 'N/A'}
                        </p>
                      </div>
                      <Package className="w-8 h-8 text-primary-500" />
                    </div>
                    <div className="mt-3 space-y-1">
                      <div className="flex justify-between text-sm">
                        <span className="text-gray-600">Price:</span>
                        <span className="font-medium text-gray-900">
                          {formatCurrency(product.unit_price, product.currency)}
                        </span>
                      </div>
                      <div className="flex justify-between text-sm">
                        <span className="text-gray-600">Stock:</span>
                        <span className="font-medium text-gray-900">
                          {product.stock_quantity || 0} units
                        </span>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}
      </Card>
    </div>
  );
};

export default CRM;

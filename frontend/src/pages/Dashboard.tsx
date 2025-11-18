import React, { useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  FileText,
  CheckCircle,
  FolderOpen,
  Zap,
  TrendingUp,
  Download,
  Plus,
} from 'lucide-react';
import { StatCard, Card } from '../components/Card';
import { Button } from '../components/Button';
import { useStore } from '../store/useStore';
import apiService from '../services/api';
import toast from 'react-hot-toast';
import { exportToPDF, exportToExcel, formatDate } from '../utils/export';

const Dashboard: React.FC = () => {
  const navigate = useNavigate();
  const { stats, submissions, setStats, setSubmissions, setLoading } = useStore();

  useEffect(() => {
    loadDashboardData();
  }, []);

  const loadDashboardData = async () => {
    try {
      setLoading(true);
      const [statsData, submissionsData] = await Promise.all([
        apiService.getDashboardStats(),
        apiService.getSubmissions(10),
      ]);
      setStats(statsData);
      setSubmissions(submissionsData);
    } catch (error) {
      console.error('Error loading dashboard data:', error);
      toast.error('Failed to load dashboard data');
    } finally {
      setLoading(false);
    }
  };

  const handleExportPDF = () => {
    if (submissions.length === 0) {
      toast.error('No data to export');
      return;
    }

    const exportData = submissions.map((sub) => ({
      Template: sub.template,
      Date: formatDate(sub.created_at),
      Fields: Object.keys(sub.filled_form).length,
    }));

    exportToPDF(exportData, 'Recent Submissions');
    toast.success('Exported to PDF');
  };

  const handleExportExcel = () => {
    if (submissions.length === 0) {
      toast.error('No data to export');
      return;
    }

    const exportData = submissions.map((sub) => ({
      Template: sub.template,
      Date: formatDate(sub.created_at),
      Fields: Object.keys(sub.filled_form).length,
      Data: JSON.stringify(sub.filled_form),
    }));

    exportToExcel(exportData, 'recent_submissions');
    toast.success('Exported to Excel');
  };

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-4xl font-bold text-white mb-2">Dashboard</h1>
          <p className="text-white/80">AI-Powered Trade Form Automation</p>
        </div>
        <Button
          variant="primary"
          icon={<Plus className="w-5 h-5" />}
          onClick={() => navigate('/fill-form')}
        >
          New Form
        </Button>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <StatCard
          title="Total Forms"
          value={stats?.total_forms || 0}
          icon={<FileText className="w-6 h-6" />}
        />
        <StatCard
          title="Completed"
          value={stats?.completed_forms || 0}
          icon={<CheckCircle className="w-6 h-6" />}
        />
        <StatCard
          title="Templates"
          value={stats?.total_templates || 0}
          icon={<FolderOpen className="w-6 h-6" />}
        />
        <StatCard
          title="AI Status"
          value={stats?.ai_status || 'Active'}
          icon={<Zap className="w-6 h-6" />}
        />
      </div>

      {/* Quick Actions */}
      <Card title="Quick Actions" icon={<TrendingUp className="w-5 h-5" />}>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <Button variant="outline" onClick={() => navigate('/fill-form')}>
            <FileText className="w-4 h-4 mr-2" />
            New Form
          </Button>
          <Button variant="outline" onClick={() => navigate('/templates')}>
            <FolderOpen className="w-4 h-4 mr-2" />
            Templates
          </Button>
          <Button variant="outline" onClick={() => navigate('/history')}>
            <Download className="w-4 h-4 mr-2" />
            History
          </Button>
          <Button variant="outline" onClick={handleExportPDF}>
            <Download className="w-4 h-4 mr-2" />
            Export All
          </Button>
        </div>
      </Card>

      {/* Recent Activity */}
      <Card
        title="Recent Submissions"
        subtitle={`Last ${submissions.length} form submissions`}
      >
        <div className="space-y-4">
          {submissions.length === 0 ? (
            <div className="text-center py-8 text-gray-500">
              <FileText className="w-12 h-12 mx-auto mb-3 opacity-50" />
              <p>No submissions yet. Start by filling your first form!</p>
              <Button
                variant="primary"
                className="mt-4"
                onClick={() => navigate('/fill-form')}
              >
                Fill Your First Form
              </Button>
            </div>
          ) : (
            <>
              <div className="overflow-x-auto">
                <table className="min-w-full divide-y divide-gray-200">
                  <thead className="bg-gray-50">
                    <tr>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Template
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Date
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Fields
                      </th>
                      <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Actions
                      </th>
                    </tr>
                  </thead>
                  <tbody className="bg-white divide-y divide-gray-200">
                    {submissions.map((submission, index) => (
                      <tr key={submission.id || index} className="hover:bg-gray-50">
                        <td className="px-6 py-4 whitespace-nowrap">
                          <div className="text-sm font-medium text-gray-900">
                            {submission.template}
                          </div>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap">
                          <div className="text-sm text-gray-500">
                            {formatDate(submission.created_at)}
                          </div>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap">
                          <div className="text-sm text-gray-500">
                            {Object.keys(submission.filled_form).length} fields
                          </div>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                          <button className="text-primary-600 hover:text-primary-900">
                            View
                          </button>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
              <div className="flex justify-end space-x-2 pt-4 border-t">
                <Button variant="outline" size="sm" onClick={handleExportPDF}>
                  <Download className="w-4 h-4 mr-2" />
                  Export PDF
                </Button>
                <Button variant="outline" size="sm" onClick={handleExportExcel}>
                  <Download className="w-4 h-4 mr-2" />
                  Export Excel
                </Button>
              </div>
            </>
          )}
        </div>
      </Card>
    </div>
  );
};

export default Dashboard;

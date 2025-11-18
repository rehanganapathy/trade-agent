import React, { useEffect, useState } from 'react';
import { History as HistoryIcon, Search, Download, Eye } from 'lucide-react';
import { Card } from '../components/Card';
import { Button } from '../components/Button';
import { Input } from '../components/Input';
import { useStore } from '../store/useStore';
import apiService from '../services/api';
import toast from 'react-hot-toast';
import { exportToPDF, exportToExcel, formatDate } from '../utils/export';
import type { FormSubmission } from '../types';

const History: React.FC = () => {
  const { submissions, setSubmissions } = useStore();
  const [searchQuery, setSearchQuery] = useState('');
  const [filteredSubmissions, setFilteredSubmissions] = useState<FormSubmission[]>([]);
  const [selectedSubmission, setSelectedSubmission] = useState<FormSubmission | null>(null);

  useEffect(() => {
    loadSubmissions();
  }, []);

  useEffect(() => {
    if (searchQuery.trim()) {
      const filtered = submissions.filter(
        (sub) =>
          sub.template.toLowerCase().includes(searchQuery.toLowerCase()) ||
          JSON.stringify(sub.filled_form).toLowerCase().includes(searchQuery.toLowerCase())
      );
      setFilteredSubmissions(filtered);
    } else {
      setFilteredSubmissions(submissions);
    }
  }, [searchQuery, submissions]);

  const loadSubmissions = async () => {
    try {
      const data = await apiService.getSubmissions();
      setSubmissions(data);
    } catch (error) {
      console.error('Error loading submissions:', error);
      toast.error('Failed to load history');
    }
  };

  const handleSearch = async () => {
    if (!searchQuery.trim()) {
      toast.error('Please enter a search query');
      return;
    }

    try {
      const results = await apiService.searchSubmissions(searchQuery);
      setFilteredSubmissions(results);
      toast.success(`Found ${results.length} results`);
    } catch (error) {
      console.error('Error searching:', error);
      toast.error('Search failed');
    }
  };

  const handleExportAll = () => {
    if (filteredSubmissions.length === 0) {
      toast.error('No data to export');
      return;
    }

    const exportData = filteredSubmissions.map((sub) => ({
      Template: sub.template,
      Date: formatDate(sub.created_at),
      Fields: Object.keys(sub.filled_form).length,
      Data: JSON.stringify(sub.filled_form),
    }));

    exportToExcel(exportData, 'submission_history');
    toast.success('Exported to Excel');
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-4xl font-bold text-white mb-2">History</h1>
          <p className="text-white/80">View and search past form submissions</p>
        </div>
        <Button
          variant="primary"
          icon={<Download className="w-5 h-5" />}
          onClick={handleExportAll}
          disabled={filteredSubmissions.length === 0}
        >
          Export All
        </Button>
      </div>

      {/* Search */}
      <Card>
        <div className="flex space-x-3">
          <Input
            placeholder="Search submissions..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            onKeyPress={(e) => e.key === 'Enter' && handleSearch()}
            icon={<Search className="w-5 h-5" />}
            className="flex-1"
          />
          <Button variant="primary" onClick={handleSearch}>
            Search
          </Button>
        </div>
      </Card>

      {/* Submissions List */}
      <Card>
        {filteredSubmissions.length === 0 ? (
          <div className="text-center py-12 text-gray-500">
            <HistoryIcon className="w-16 h-16 mx-auto mb-4 opacity-30" />
            <p className="text-lg">No submissions found</p>
            <p className="text-sm mt-2">
              {searchQuery
                ? 'Try a different search query'
                : 'Start filling forms to see history'}
            </p>
          </div>
        ) : (
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
                {filteredSubmissions.map((submission, index) => (
                  <tr key={submission.id || index} className="hover:bg-gray-50">
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="flex items-center">
                        <div className="flex-shrink-0 h-10 w-10 bg-primary-100 rounded-lg flex items-center justify-center">
                          <HistoryIcon className="w-5 h-5 text-primary-600" />
                        </div>
                        <div className="ml-4">
                          <div className="text-sm font-medium text-gray-900">
                            {submission.template}
                          </div>
                        </div>
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="text-sm text-gray-500">
                        {formatDate(submission.created_at)}
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className="px-2 inline-flex text-xs leading-5 font-semibold rounded-full bg-green-100 text-green-800">
                        {Object.keys(submission.filled_form).length} fields
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                      <button
                        onClick={() => setSelectedSubmission(submission)}
                        className="text-primary-600 hover:text-primary-900"
                      >
                        <Eye className="w-5 h-5" />
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </Card>

      {/* View Submission Modal */}
      {selectedSubmission && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <Card className="max-w-3xl w-full max-h-[90vh] overflow-y-auto">
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <div>
                  <h2 className="text-2xl font-bold text-gray-900">
                    {selectedSubmission.template}
                  </h2>
                  <p className="text-sm text-gray-500">
                    {formatDate(selectedSubmission.created_at)}
                  </p>
                </div>
              </div>

              {selectedSubmission.trade_info && (
                <div className="border-t pt-4">
                  <h3 className="font-semibold text-gray-900 mb-2">Original Input</h3>
                  <div className="bg-gray-50 p-4 rounded">
                    <p className="text-sm text-gray-700 whitespace-pre-wrap">
                      {selectedSubmission.trade_info}
                    </p>
                  </div>
                </div>
              )}

              <div className="border-t pt-4">
                <h3 className="font-semibold text-gray-900 mb-3">Filled Form Data</h3>
                <div className="space-y-2">
                  {Object.entries(selectedSubmission.filled_form).map(([key, value]) => (
                    <div key={key} className="bg-gray-50 p-3 rounded">
                      <div className="text-xs font-medium text-gray-500 uppercase">
                        {key}
                      </div>
                      <div className="text-sm text-gray-900 mt-1">
                        {String(value) || 'N/A'}
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              <div className="border-t pt-4">
                <h3 className="font-semibold text-gray-900 mb-2">JSON Output</h3>
                <div className="bg-gray-900 rounded-lg p-4 max-h-64 overflow-y-auto">
                  <pre className="text-xs text-green-400 font-mono">
                    {JSON.stringify(selectedSubmission.filled_form, null, 2)}
                  </pre>
                </div>
              </div>

              <div className="flex space-x-3 pt-4 border-t">
                <Button
                  variant="outline"
                  className="flex-1"
                  onClick={() => setSelectedSubmission(null)}
                >
                  Close
                </Button>
                <Button
                  variant="primary"
                  icon={<Download className="w-5 h-5" />}
                  onClick={() => {
                    const data = Object.entries(selectedSubmission.filled_form).map(
                      ([key, value]) => ({
                        Field: key,
                        Value: String(value),
                      })
                    );
                    exportToPDF(data, selectedSubmission.template);
                    toast.success('Exported to PDF');
                  }}
                >
                  Export PDF
                </Button>
              </div>
            </div>
          </Card>
        </div>
      )}
    </div>
  );
};

export default History;

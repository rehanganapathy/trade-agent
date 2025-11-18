import React, { useEffect, useState } from 'react';
import {
  FileText,
  Send,
  Copy,
  Download,
  CheckCircle,
  Database,
  Sparkles,
} from 'lucide-react';
import { Card } from '../components/Card';
import { Button } from '../components/Button';
import { Select, TextArea } from '../components/Input';
import { useStore } from '../store/useStore';
import apiService from '../services/api';
import toast from 'react-hot-toast';
import { exportToPDF, exportToExcel, exportToJSON, copyToClipboard } from '../utils/export';

const FormFilling: React.FC = () => {
  const {
    templates,
    selectedTemplate,
    filledForm,
    setTemplates,
    setSelectedTemplate,
    setFilledForm,
    setLoading,
    isLoading,
  } = useStore();

  const [tradeInfo, setTradeInfo] = useState('');
  const [useVectorDB, setUseVectorDB] = useState(true);
  const [saveToDB, setSaveToDB] = useState(true);

  useEffect(() => {
    loadTemplates();
  }, []);

  const loadTemplates = async () => {
    try {
      const data = await apiService.getTemplates();
      setTemplates(data);
      if (data.length > 0) {
        setSelectedTemplate(data[0]);
      }
    } catch (error) {
      console.error('Error loading templates:', error);
      toast.error('Failed to load templates');
    }
  };

  const handleTemplateChange = async (templateName: string) => {
    try {
      const template = templates.find((t) => t.name === templateName);
      if (template) {
        setSelectedTemplate(template);
      }
    } catch (error) {
      console.error('Error selecting template:', error);
    }
  };

  const handleFillForm = async () => {
    if (!selectedTemplate) {
      toast.error('Please select a template');
      return;
    }

    if (!tradeInfo.trim()) {
      toast.error('Please enter trade information');
      return;
    }

    try {
      setLoading(true);
      const response = await apiService.fillForm({
        template: selectedTemplate.name,
        trade_info: tradeInfo,
        use_vector_db: useVectorDB,
        save_to_db: saveToDB,
      });

      setFilledForm(response.filled_form);
      toast.success('Form filled successfully!');
    } catch (error: any) {
      console.error('Error filling form:', error);
      toast.error(error.response?.data?.error || 'Failed to fill form');
    } finally {
      setLoading(false);
    }
  };

  const handleCopy = async () => {
    if (!filledForm) return;
    const success = await copyToClipboard(JSON.stringify(filledForm, null, 2));
    if (success) {
      toast.success('Copied to clipboard!');
    } else {
      toast.error('Failed to copy');
    }
  };

  const handleExportPDF = () => {
    if (!filledForm) return;
    const data = Object.entries(filledForm).map(([key, value]) => ({
      Field: key,
      Value: String(value),
    }));
    exportToPDF(data, selectedTemplate?.name || 'Form');
    toast.success('Exported to PDF');
  };

  const handleExportExcel = () => {
    if (!filledForm) return;
    const data = Object.entries(filledForm).map(([key, value]) => ({
      Field: key,
      Value: String(value),
    }));
    exportToExcel(data, selectedTemplate?.name || 'form');
    toast.success('Exported to Excel');
  };

  const handleExportJSON = () => {
    if (!filledForm) return;
    exportToJSON(filledForm, selectedTemplate?.name || 'form');
    toast.success('Exported to JSON');
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-4xl font-bold text-white mb-2">AI Form Filler</h1>
        <p className="text-white/80">
          Enter your trade information and let AI fill the form for you
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Input Section */}
        <Card title="Input" icon={<FileText className="w-5 h-5" />}>
          <div className="space-y-4">
            <Select
              label="Select Template"
              options={[
                { value: '', label: 'Select a template...' },
                ...templates.map((t) => ({ value: t.name, label: t.name })),
              ]}
              value={selectedTemplate?.name || ''}
              onChange={(e) => handleTemplateChange(e.target.value)}
            />

            <TextArea
              label="Trade Information"
              placeholder="Enter trade details, invoice data, or any relevant information..."
              rows={12}
              value={tradeInfo}
              onChange={(e) => setTradeInfo(e.target.value)}
            />

            {/* Options */}
            <div className="space-y-3 pt-2">
              <label className="flex items-center space-x-3 cursor-pointer">
                <input
                  type="checkbox"
                  checked={useVectorDB}
                  onChange={(e) => setUseVectorDB(e.target.checked)}
                  className="w-5 h-5 rounded text-primary-600 focus:ring-primary-500"
                />
                <span className="flex items-center text-sm text-gray-700">
                  <Database className="w-4 h-4 mr-2" />
                  Use Vector DB Autofill
                </span>
              </label>

              <label className="flex items-center space-x-3 cursor-pointer">
                <input
                  type="checkbox"
                  checked={saveToDB}
                  onChange={(e) => setSaveToDB(e.target.checked)}
                  className="w-5 h-5 rounded text-primary-600 focus:ring-primary-500"
                />
                <span className="flex items-center text-sm text-gray-700">
                  <Sparkles className="w-4 h-4 mr-2" />
                  Save to Database for Future Use
                </span>
              </label>
            </div>

            <Button
              variant="primary"
              className="w-full"
              icon={<Send className="w-5 h-5" />}
              onClick={handleFillForm}
              loading={isLoading}
              disabled={!selectedTemplate || !tradeInfo.trim()}
            >
              Fill Form with AI
            </Button>
          </div>
        </Card>

        {/* Output Section */}
        <Card title="Output" icon={<CheckCircle className="w-5 h-5" />}>
          {!filledForm ? (
            <div className="text-center py-12 text-gray-500">
              <FileText className="w-16 h-16 mx-auto mb-4 opacity-30" />
              <p className="text-lg">Fill a form to see the results here</p>
              <p className="text-sm mt-2">The AI will extract and populate all fields</p>
            </div>
          ) : (
            <div className="space-y-4">
              {/* Field Preview */}
              <div className="bg-gray-50 rounded-lg p-4 max-h-96 overflow-y-auto">
                <h4 className="font-semibold text-gray-900 mb-3">Filled Fields:</h4>
                <div className="space-y-2">
                  {Object.entries(filledForm).map(([key, value]) => (
                    <div
                      key={key}
                      className="bg-white p-3 rounded border border-gray-200"
                    >
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

              {/* JSON Output */}
              <div className="bg-gray-900 rounded-lg p-4 max-h-64 overflow-y-auto">
                <pre className="text-xs text-green-400 font-mono">
                  {JSON.stringify(filledForm, null, 2)}
                </pre>
              </div>

              {/* Action Buttons */}
              <div className="grid grid-cols-2 gap-3">
                <Button
                  variant="outline"
                  size="sm"
                  icon={<Copy className="w-4 h-4" />}
                  onClick={handleCopy}
                >
                  Copy JSON
                </Button>
                <Button
                  variant="outline"
                  size="sm"
                  icon={<Download className="w-4 h-4" />}
                  onClick={handleExportJSON}
                >
                  Download JSON
                </Button>
                <Button
                  variant="outline"
                  size="sm"
                  icon={<Download className="w-4 h-4" />}
                  onClick={handleExportPDF}
                >
                  Export PDF
                </Button>
                <Button
                  variant="outline"
                  size="sm"
                  icon={<Download className="w-4 h-4" />}
                  onClick={handleExportExcel}
                >
                  Export Excel
                </Button>
              </div>
            </div>
          )}
        </Card>
      </div>

      {/* Template Preview */}
      {selectedTemplate && (
        <Card title="Template Fields" subtitle={selectedTemplate.description}>
          <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-3">
            {selectedTemplate.fields.map((field, index) => (
              <div
                key={index}
                className="bg-gray-50 px-3 py-2 rounded border border-gray-200"
              >
                <div className="text-xs font-medium text-gray-600">
                  {field.name}
                  {field.required && <span className="text-red-500 ml-1">*</span>}
                </div>
                <div className="text-xs text-gray-500 mt-1">{field.type}</div>
              </div>
            ))}
          </div>
        </Card>
      )}
    </div>
  );
};

export default FormFilling;

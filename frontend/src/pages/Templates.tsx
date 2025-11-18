import React, { useEffect, useState } from 'react';
import { FolderOpen, Plus, Eye, Trash2 } from 'lucide-react';
import { Card } from '../components/Card';
import { Button } from '../components/Button';
import { Input, TextArea } from '../components/Input';
import { useStore } from '../store/useStore';
import apiService from '../services/api';
import toast from 'react-hot-toast';
import type { FormTemplate, FormField } from '../types';

const Templates: React.FC = () => {
  const { templates, setTemplates } = useStore();
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [selectedTemplate, setSelectedTemplate] = useState<FormTemplate | null>(null);
  const [newTemplate, setNewTemplate] = useState<FormTemplate>({
    name: '',
    description: '',
    fields: [],
  });
  const [newField, setNewField] = useState<FormField>({
    name: '',
    type: 'text',
    required: false,
  });

  useEffect(() => {
    loadTemplates();
  }, []);

  const loadTemplates = async () => {
    try {
      const data = await apiService.getTemplates();
      setTemplates(data);
    } catch (error) {
      console.error('Error loading templates:', error);
      toast.error('Failed to load templates');
    }
  };

  const handleAddField = () => {
    if (!newField.name.trim()) {
      toast.error('Field name is required');
      return;
    }

    setNewTemplate({
      ...newTemplate,
      fields: [...newTemplate.fields, { ...newField }],
    });

    setNewField({ name: '', type: 'text', required: false });
  };

  const handleRemoveField = (index: number) => {
    setNewTemplate({
      ...newTemplate,
      fields: newTemplate.fields.filter((_, i) => i !== index),
    });
  };

  const handleCreateTemplate = async () => {
    if (!newTemplate.name.trim()) {
      toast.error('Template name is required');
      return;
    }

    if (newTemplate.fields.length === 0) {
      toast.error('Add at least one field');
      return;
    }

    try {
      await apiService.createTemplate(newTemplate);
      toast.success('Template created successfully');
      setShowCreateModal(false);
      setNewTemplate({ name: '', description: '', fields: [] });
      loadTemplates();
    } catch (error) {
      console.error('Error creating template:', error);
      toast.error('Failed to create template');
    }
  };

  const handleViewTemplate = async (templateName: string) => {
    try {
      const template = await apiService.getTemplate(templateName);
      setSelectedTemplate(template);
    } catch (error) {
      console.error('Error loading template:', error);
      toast.error('Failed to load template');
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-4xl font-bold text-white mb-2">Templates</h1>
          <p className="text-white/80">Manage your form templates</p>
        </div>
        <Button
          variant="primary"
          icon={<Plus className="w-5 h-5" />}
          onClick={() => setShowCreateModal(true)}
        >
          Create Template
        </Button>
      </div>

      {/* Templates Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {templates.map((template, index) => (
          <Card key={template.id || index} className="hover:shadow-xl transition-shadow">
            <div className="space-y-4">
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  <h3 className="text-lg font-semibold text-gray-900 mb-1">
                    {template.name}
                  </h3>
                  <p className="text-sm text-gray-500 line-clamp-2">
                    {template.description || 'No description'}
                  </p>
                </div>
                <FolderOpen className="w-8 h-8 text-primary-500" />
              </div>

              <div className="flex items-center justify-between pt-3 border-t border-gray-200">
                <span className="text-sm text-gray-600">
                  {template.fields.length} fields
                </span>
                <div className="flex space-x-2">
                  <button
                    onClick={() => handleViewTemplate(template.name)}
                    className="text-primary-600 hover:text-primary-800"
                  >
                    <Eye className="w-5 h-5" />
                  </button>
                </div>
              </div>
            </div>
          </Card>
        ))}
      </div>

      {templates.length === 0 && (
        <Card>
          <div className="text-center py-12 text-gray-500">
            <FolderOpen className="w-16 h-16 mx-auto mb-4 opacity-30" />
            <p className="text-lg">No templates found</p>
            <p className="text-sm mt-2">Create your first template to get started</p>
            <Button
              variant="primary"
              className="mt-4"
              onClick={() => setShowCreateModal(true)}
            >
              Create Template
            </Button>
          </div>
        </Card>
      )}

      {/* Create Template Modal */}
      {showCreateModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <Card className="max-w-2xl w-full max-h-[90vh] overflow-y-auto">
            <div className="space-y-4">
              <h2 className="text-2xl font-bold text-gray-900">Create New Template</h2>

              <Input
                label="Template Name"
                value={newTemplate.name}
                onChange={(e) => setNewTemplate({ ...newTemplate, name: e.target.value })}
                placeholder="e.g., Commercial Invoice"
              />

              <TextArea
                label="Description (Optional)"
                value={newTemplate.description}
                onChange={(e) =>
                  setNewTemplate({ ...newTemplate, description: e.target.value })
                }
                placeholder="Brief description of this template"
                rows={3}
              />

              <div className="border-t pt-4">
                <h3 className="font-semibold text-gray-900 mb-3">Fields</h3>

                {/* Existing Fields */}
                {newTemplate.fields.length > 0 && (
                  <div className="space-y-2 mb-4">
                    {newTemplate.fields.map((field, index) => (
                      <div
                        key={index}
                        className="flex items-center justify-between bg-gray-50 p-3 rounded"
                      >
                        <div>
                          <span className="font-medium">{field.name}</span>
                          <span className="text-sm text-gray-500 ml-2">
                            ({field.type})
                            {field.required && (
                              <span className="text-red-500 ml-1">*</span>
                            )}
                          </span>
                        </div>
                        <button
                          onClick={() => handleRemoveField(index)}
                          className="text-red-600 hover:text-red-800"
                        >
                          <Trash2 className="w-4 h-4" />
                        </button>
                      </div>
                    ))}
                  </div>
                )}

                {/* Add Field Form */}
                <div className="grid grid-cols-12 gap-3">
                  <div className="col-span-5">
                    <Input
                      placeholder="Field name"
                      value={newField.name}
                      onChange={(e) => setNewField({ ...newField, name: e.target.value })}
                    />
                  </div>
                  <div className="col-span-3">
                    <select
                      className="w-full rounded-lg border-gray-300 shadow-sm focus:ring-2 focus:ring-primary-500 focus:border-primary-500 px-4 py-2.5"
                      value={newField.type}
                      onChange={(e) => setNewField({ ...newField, type: e.target.value })}
                    >
                      <option value="text">Text</option>
                      <option value="number">Number</option>
                      <option value="date">Date</option>
                      <option value="email">Email</option>
                    </select>
                  </div>
                  <div className="col-span-2 flex items-center">
                    <label className="flex items-center space-x-2 cursor-pointer">
                      <input
                        type="checkbox"
                        checked={newField.required}
                        onChange={(e) =>
                          setNewField({ ...newField, required: e.target.checked })
                        }
                        className="rounded text-primary-600 focus:ring-primary-500"
                      />
                      <span className="text-sm">Required</span>
                    </label>
                  </div>
                  <div className="col-span-2">
                    <Button variant="outline" size="sm" onClick={handleAddField}>
                      <Plus className="w-4 h-4" />
                    </Button>
                  </div>
                </div>
              </div>

              <div className="flex space-x-3 pt-4 border-t">
                <Button
                  variant="outline"
                  className="flex-1"
                  onClick={() => setShowCreateModal(false)}
                >
                  Cancel
                </Button>
                <Button
                  variant="primary"
                  className="flex-1"
                  onClick={handleCreateTemplate}
                >
                  Create Template
                </Button>
              </div>
            </div>
          </Card>
        </div>
      )}

      {/* View Template Modal */}
      {selectedTemplate && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <Card className="max-w-2xl w-full max-h-[90vh] overflow-y-auto">
            <div className="space-y-4">
              <h2 className="text-2xl font-bold text-gray-900">
                {selectedTemplate.name}
              </h2>
              <p className="text-gray-600">{selectedTemplate.description}</p>

              <div className="border-t pt-4">
                <h3 className="font-semibold text-gray-900 mb-3">
                  Fields ({selectedTemplate.fields.length})
                </h3>
                <div className="space-y-2">
                  {selectedTemplate.fields.map((field, index) => (
                    <div key={index} className="bg-gray-50 p-3 rounded">
                      <div className="font-medium">
                        {field.name}
                        {field.required && <span className="text-red-500 ml-1">*</span>}
                      </div>
                      <div className="text-sm text-gray-500 mt-1">
                        Type: {field.type}
                        {field.description && ` • ${field.description}`}
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              <div className="flex justify-end pt-4 border-t">
                <Button variant="outline" onClick={() => setSelectedTemplate(null)}>
                  Close
                </Button>
              </div>
            </div>
          </Card>
        </div>
      )}
    </div>
  );
};

export default Templates;

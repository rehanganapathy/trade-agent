import axios, { type AxiosInstance } from 'axios';
import type {
  FormTemplate,
  FormSubmission,
  FormFillRequest,
  FormFillResponse,
  HSCodeSuggestion,
  DashboardStats,
  ApiResponse,
  Company,
  Lead,
  Product,
} from '../types';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:5000';

class ApiService {
  private client: AxiosInstance;

  constructor() {
    this.client = axios.create({
      baseURL: API_BASE_URL,
      headers: {
        'Content-Type': 'application/json',
      },
      timeout: 30000, // 30 seconds
    });

    // Add response interceptor for error handling
    this.client.interceptors.response.use(
      (response) => response,
      (error) => {
        console.error('API Error:', error);
        throw error;
      }
    );
  }

  // Form Filling APIs
  async fillForm(request: FormFillRequest): Promise<FormFillResponse> {
    const response = await this.client.post<any>('/api/fill', {
      template: request.template,
      prompt: request.trade_info,
      use_db: request.use_vector_db,
      save_to_db: request.save_to_db,
    });
    return {
      filled_form: response.data.filled_form,
      template: request.template,
    };
  }

  async getTemplates(): Promise<FormTemplate[]> {
    const response = await this.client.get<{ templates: any[] }>('/api/templates');
    return response.data.templates.map((t: any) => ({
      name: t.name,
      fields: t.fields.map((f: string) => ({ name: f, type: 'text' })),
    }));
  }

  async getTemplate(name: string): Promise<FormTemplate> {
    const response = await this.client.get<{ template: any }>(`/api/templates/${name}`);
    const templateData = response.data.template;
    return {
      name,
      fields: Object.keys(templateData).map((key) => ({
        name: key,
        type: 'text',
        description: templateData[key],
      })),
    };
  }

  async createTemplate(template: FormTemplate): Promise<ApiResponse> {
    const templateObj: Record<string, string> = {};
    template.fields.forEach((field) => {
      templateObj[field.name] = field.description || '';
    });

    const response = await this.client.post<any>('/api/templates', {
      name: template.name,
      template: templateObj,
    });
    return { success: response.data.success };
  }

  // History & Submissions
  async getSubmissions(limit: number = 50): Promise<FormSubmission[]> {
    const response = await this.client.get<{ history: any[] }>('/api/history', {
      params: { limit },
    });
    return response.data.history || [];
  }

  async searchSubmissions(query: string, template?: string): Promise<FormSubmission[]> {
    const response = await this.client.get<{ history: any[] }>('/api/history', {
      params: { query, template },
    });
    return response.data.history || [];
  }

  // HS Code Classification
  async classifyHSCode(description: string, topN: number = 5): Promise<HSCodeSuggestion[]> {
    const response = await this.client.post<{ suggestions: any[] }>('/api/classify-hs', {
      product_description: description,
      top_n: topN,
    });
    return response.data.suggestions || [];
  }

  // Dashboard Stats
  async getDashboardStats(): Promise<DashboardStats> {
    // Mock data for now since backend doesn't have this endpoint yet
    return {
      total_forms: 0,
      completed_forms: 0,
      total_templates: 0,
      ai_status: 'Active',
    };
  }

  // CRM APIs
  async getCompanies(): Promise<Company[]> {
    const response = await this.client.get<Company[]>('/api/companies');
    return response.data;
  }

  async createCompany(company: Company): Promise<ApiResponse<Company>> {
    const response = await this.client.post<ApiResponse<Company>>('/api/companies', company);
    return response.data;
  }

  async getLeads(): Promise<Lead[]> {
    const response = await this.client.get<Lead[]>('/api/leads');
    return response.data;
  }

  async createLead(lead: Lead): Promise<ApiResponse<Lead>> {
    const response = await this.client.post<ApiResponse<Lead>>('/api/leads', lead);
    return response.data;
  }

  async getProducts(): Promise<Product[]> {
    const response = await this.client.get<Product[]>('/api/products');
    return response.data;
  }

  async createProduct(product: Product): Promise<ApiResponse<Product>> {
    const response = await this.client.post<ApiResponse<Product>>('/api/products', product);
    return response.data;
  }

  // Export functionality
  async exportData(format: 'pdf' | 'excel' | 'json', data: any): Promise<Blob> {
    const response = await this.client.post(
      '/export',
      { format, data },
      { responseType: 'blob' }
    );
    return response.data;
  }
}

export const apiService = new ApiService();
export default apiService;

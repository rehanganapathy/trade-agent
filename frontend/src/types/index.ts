// Form Template Types
export interface FormField {
  name: string;
  type: string;
  required?: boolean;
  description?: string;
}

export interface FormTemplate {
  id?: string;
  name: string;
  description?: string;
  fields: FormField[];
  created_at?: string;
}

// Form Submission Types
export interface FormSubmission {
  id?: string;
  template: string;
  filled_form: Record<string, any>;
  created_at?: string;
  trade_info?: string;
}

// HS Code Types
export interface HSCodeSuggestion {
  code: string;
  description: string;
  confidence: number;
  reasoning?: string;
}

// Stats Types
export interface DashboardStats {
  total_forms: number;
  completed_forms: number;
  total_templates: number;
  ai_status: string;
}

// Export Options
export type ExportFormat = 'pdf' | 'excel' | 'json';

// API Response Types
export interface ApiResponse<T = any> {
  success: boolean;
  data?: T;
  error?: string;
  message?: string;
}

// Form Fill Request
export interface FormFillRequest {
  template: string;
  trade_info: string;
  use_vector_db?: boolean;
  save_to_db?: boolean;
}

// Form Fill Response
export interface FormFillResponse {
  filled_form: Record<string, any>;
  template: string;
  processing_time?: number;
}

// CRM Types
export interface Company {
  id?: number;
  name: string;
  email?: string;
  phone?: string;
  website?: string;
  address?: string;
  city?: string;
  state?: string;
  country?: string;
  company_type?: 'customer' | 'supplier' | 'partner' | 'competitor' | 'other';
  status?: 'active' | 'inactive' | 'prospect';
  created_at?: string;
}

export interface Lead {
  id?: number;
  company_name: string;
  contact_name?: string;
  email?: string;
  phone?: string;
  source?: string;
  status?: 'new' | 'contacted' | 'qualified' | 'proposal' | 'won' | 'lost';
  value?: number;
  created_at?: string;
}

export interface Product {
  id?: number;
  name: string;
  hs_code?: string;
  description?: string;
  unit_price?: number;
  currency?: string;
  stock_quantity?: number;
  created_at?: string;
}

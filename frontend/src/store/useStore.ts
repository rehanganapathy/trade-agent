import { create } from 'zustand';
import type {
  FormTemplate,
  FormSubmission,
  DashboardStats,
  Company,
  Lead,
  Product,
} from '../types';

interface AppState {
  // Form state
  templates: FormTemplate[];
  submissions: FormSubmission[];
  selectedTemplate: FormTemplate | null;
  filledForm: Record<string, any> | null;
  isLoading: boolean;
  error: string | null;

  // Dashboard state
  stats: DashboardStats | null;

  // CRM state
  companies: Company[];
  leads: Lead[];
  products: Product[];

  // Actions
  setTemplates: (templates: FormTemplate[]) => void;
  setSelectedTemplate: (template: FormTemplate | null) => void;
  setFilledForm: (form: Record<string, any> | null) => void;
  setSubmissions: (submissions: FormSubmission[]) => void;
  addSubmission: (submission: FormSubmission) => void;
  setStats: (stats: DashboardStats) => void;
  setCompanies: (companies: Company[]) => void;
  setLeads: (leads: Lead[]) => void;
  setProducts: (products: Product[]) => void;
  setLoading: (isLoading: boolean) => void;
  setError: (error: string | null) => void;
  clearError: () => void;
}

export const useStore = create<AppState>((set) => ({
  // Initial state
  templates: [],
  submissions: [],
  selectedTemplate: null,
  filledForm: null,
  isLoading: false,
  error: null,
  stats: null,
  companies: [],
  leads: [],
  products: [],

  // Actions
  setTemplates: (templates) => set({ templates }),
  setSelectedTemplate: (template) => set({ selectedTemplate: template }),
  setFilledForm: (form) => set({ filledForm: form }),
  setSubmissions: (submissions) => set({ submissions }),
  addSubmission: (submission) =>
    set((state) => ({ submissions: [submission, ...state.submissions] })),
  setStats: (stats) => set({ stats }),
  setCompanies: (companies) => set({ companies }),
  setLeads: (leads) => set({ leads }),
  setProducts: (products) => set({ products }),
  setLoading: (isLoading) => set({ isLoading }),
  setError: (error) => set({ error }),
  clearError: () => set({ error: null }),
}));

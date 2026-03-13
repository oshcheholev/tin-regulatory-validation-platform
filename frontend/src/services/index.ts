import api from './api';
import type {
  LoginCredentials,
  RegisterData,
  AuthTokens,
  User,
  Document,
  Country,
  TinRule,
  ValidationRequest,
  ValidationResult,
  ValidationBatch,
  Report,
  PaginatedResponse,
} from '@/types';

// Auth
export const authService = {
  login: (credentials: LoginCredentials) =>
    api.post<AuthTokens>('/auth/login/', credentials).then((r) => r.data),

  register: (data: RegisterData) =>
    api.post<User>('/auth/register/', data).then((r) => r.data),

  getMe: () => api.get<User>('/auth/me/').then((r) => r.data),

  updateMe: (data: Partial<User>) =>
    api.patch<User>('/auth/me/', data).then((r) => r.data),
};

// Documents
export const documentService = {
  list: (params?: Record<string, string>) =>
    api.get<PaginatedResponse<Document>>('/documents/', { params }).then((r) => r.data),

  upload: (formData: FormData) =>
    api.post<Document>('/documents/upload/', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    }).then((r) => r.data),

  get: (id: number) => api.get<Document>(`/documents/${id}/`).then((r) => r.data),

  delete: (id: number) => api.delete(`/documents/${id}/`),
};

// Countries & Rules
export const ruleService = {
  listCountries: () =>
    api.get<PaginatedResponse<Country>>('/rules/countries/').then((r) => r.data),

  getCountry: (code: string) =>
    api.get<Country>(`/rules/countries/${code}/`).then((r) => r.data),

  listRules: (params?: Record<string, string>) =>
    api.get<PaginatedResponse<TinRule>>('/rules/', { params }).then((r) => r.data),

  getRule: (id: number) => api.get<TinRule>(`/rules/${id}/`).then((r) => r.data),
};

// Validation
export const validationService = {
  validate: (data: ValidationRequest) =>
    api.post<ValidationResult>('/validation/validate/', data).then((r) => r.data),

  listResults: (params?: Record<string, string>) =>
    api.get<PaginatedResponse<ValidationResult>>('/validation/results/', { params }).then((r) => r.data),

  getResult: (id: number) =>
    api.get<ValidationResult>(`/validation/results/${id}/`).then((r) => r.data),

  uploadBatch: (formData: FormData) =>
    api.post<ValidationBatch>('/validation/batch/upload/', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    }).then((r) => r.data),

  listBatches: () =>
    api.get<PaginatedResponse<ValidationBatch>>('/validation/batch/').then((r) => r.data),

  getBatch: (id: number) =>
    api.get<ValidationBatch>(`/validation/batch/${id}/`).then((r) => r.data),

  getBatchResults: (batchId: number) =>
    api.get<PaginatedResponse<ValidationResult>>(`/validation/batch/${batchId}/results/`).then((r) => r.data),
};

// Reports
export const reportService = {
  list: () => api.get<PaginatedResponse<Report>>('/reports/').then((r) => r.data),

  generate: (data: { batch_id?: number; format: string; name?: string }) =>
    api.post<Report>('/reports/generate/', data).then((r) => r.data),

  get: (id: number) => api.get<Report>(`/reports/${id}/`).then((r) => r.data),

  getDownloadUrl: (id: number) => `/api/v1/reports/${id}/download/`,
};

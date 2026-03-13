// Auth types
export interface User {
  id: number;
  email: string;
  username: string;
  first_name: string;
  last_name: string;
  organization: string;
  role: 'admin' | 'analyst' | 'viewer';
  created_at: string;
}

export interface AuthTokens {
  access: string;
  refresh: string;
  user: User;
}

export interface LoginCredentials {
  email: string;
  password: string;
}

export interface RegisterData {
  email: string;
  username: string;
  first_name: string;
  last_name: string;
  organization: string;
  role: string;
  password: string;
  password_confirm: string;
}

// Document types
export interface Document {
  id: number;
  title: string;
  description: string;
  file_url: string | null;
  file_size: number;
  file_hash: string;
  status: 'pending' | 'processing' | 'completed' | 'failed';
  error_message: string;
  page_count: number;
  uploaded_by_email: string;
  task_id: string;
  created_at: string;
  updated_at: string;
}

// Country & Rule types
export interface Country {
  id: number;
  code: string;
  name: string;
  rule_count: number;
  created_at: string;
}

export interface TinRule {
  id: number;
  country_code: string;
  country_name: string;
  source_document_title: string | null;
  rule_type: string;
  description: string;
  regex_pattern: string;
  min_length: number | null;
  max_length: number | null;
  is_active: boolean;
  confidence_score: number;
  created_at: string;
  updated_at: string;
}

// Validation types
export interface ValidationRequest {
  country: string;
  tin: string;
}

export interface ValidationResult {
  id: number;
  country_code: string;
  country_name: string;
  tin: string;
  is_valid: boolean;
  status: 'valid' | 'invalid' | 'unknown';
  explanation: string;
  matched_rules: TinRule[];
  batch_id?: string;
  created_at: string;
}

export interface ValidationBatch {
  id: number;
  name: string;
  status: 'pending' | 'processing' | 'completed' | 'failed';
  total_count: number;
  valid_count: number;
  invalid_count: number;
  unknown_count: number;
  error_message: string;
  created_by_email: string;
  task_id: string;
  created_at: string;
  completed_at: string | null;
}

// Report types
export interface Report {
  id: number;
  name: string;
  batch_name: string | null;
  format: 'csv' | 'json';
  status: 'pending' | 'processing' | 'completed' | 'failed';
  file_url: string | null;
  total_records: number;
  error_message: string;
  created_by_email: string;
  created_at: string;
  completed_at: string | null;
}

// API pagination
export interface PaginatedResponse<T> {
  count: number;
  next: string | null;
  previous: string | null;
  results: T[];
}

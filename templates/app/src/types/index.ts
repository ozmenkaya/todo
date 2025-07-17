// API Types
export interface User {
  id: number;
  username: string;
  email: string;
  role: 'admin' | 'manager' | 'employee';
  department?: string;
  first_name: string;
  last_name: string;
  created_at: string;
}

export interface Task {
  id: number;
  title: string;
  description: string;
  status: 'pending' | 'in_progress' | 'completed' | 'cancelled';
  priority: 'urgent' | 'high' | 'medium' | 'low';
  created_by: number;
  assigned_to?: number[];
  due_date?: string;
  created_at: string;
  updated_at: string;
  completed_at?: string;
  creator: User;
  assignees: User[];
  is_read?: boolean;
}

export interface Report {
  id: number;
  title: string;
  content: string;
  created_by: number;
  shared_with: number[];
  created_at: string;
  updated_at: string;
  creator: User;
  shared_users: User[];
  is_read?: boolean;
}

export interface Reminder {
  id: number;
  title: string;
  description?: string;
  reminder_time: string;
  user_id: number;
  created_at: string;
  is_completed: boolean;
}

export interface Comment {
  id: number;
  content: string;
  created_by: number;
  report_id: number;
  created_at: string;
  creator: User;
}

// API Response Types
export interface ApiResponse<T> {
  success: boolean;
  data?: T;
  message?: string;
  error?: string;
}

export interface LoginRequest {
  username: string;
  password: string;
}

export interface CreateTaskRequest {
  title: string;
  description: string;
  priority: Task['priority'];
  assigned_to: number[];
  due_date?: string;
}

export interface UpdateTaskRequest extends Partial<CreateTaskRequest> {
  status?: Task['status'];
}

export interface CreateReportRequest {
  title: string;
  content: string;
  shared_with: number[];
}

export interface CreateReminderRequest {
  title: string;
  description?: string;
  reminder_time: string;
}

// UI State Types
export interface AuthState {
  user: User | null;
  isAuthenticated: boolean;
  isLoading: boolean;
}

export interface AppNotification {
  id: string;
  type: 'success' | 'error' | 'warning' | 'info';
  title: string;
  message: string;
  duration?: number;
}

export interface NavigationState {
  currentPage: string;
  isDrawerOpen: boolean;
}

// Notification Data Types
export interface NotificationCounts {
  tasks: number;
  reminders: number;
  reports: number;
}

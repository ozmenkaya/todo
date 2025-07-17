import axios from 'axios';
import type { AxiosInstance, AxiosResponse } from 'axios';
import type {
  ApiResponse,
  User,
  Task,
  Report,
  Reminder,
  LoginRequest,
  CreateTaskRequest,
  UpdateTaskRequest,
  CreateReportRequest,
  CreateReminderRequest,
  NotificationCounts
} from '../types';
import { mockApiService } from './mockApi';

class ApiService {
  private api: AxiosInstance;
  private useMockApi: boolean = false;
  private hasTestedConnection: boolean = false;
  private forceRealApi: boolean = true; // Force real API usage
  private disableMockFallback: boolean = true; // Completely disable mock fallback

  constructor() {
    const baseURL = import.meta.env.VITE_API_BASE_URL || 
                   (import.meta.env.DEV ? 'http://localhost:5005' : '/api');
    
    this.api = axios.create({
      baseURL,
      withCredentials: true,
      headers: {
        'Content-Type': 'application/json',
      },
      timeout: 10000, // 10 second timeout
    });

    console.log('🚀 API Service initialized - Force Real API:', this.forceRealApi, 'Disable Mock:', this.disableMockFallback);

    // Request interceptor
    this.api.interceptors.request.use(
      (config) => {
        // Add any auth tokens or headers here
        return config;
      },
      (error) => {
        return Promise.reject(error);
      }
    );

    // Response interceptor
    this.api.interceptors.response.use(
      (response) => {
        // If we get a successful response, backend is working
        if (!this.hasTestedConnection) {
          this.hasTestedConnection = true;
          this.useMockApi = false;
        }
        return response;
      },
      (error) => {
        // Only switch to mock on network errors, not auth errors
        if ((error.code === 'ERR_NETWORK' || error.code === 'ECONNREFUSED') && !this.hasTestedConnection) {
          console.warn('Backend not available, falling back to mock API');
          this.useMockApi = true;
          this.hasTestedConnection = true;
        }
        
        if (error.response?.status === 401) {
          // Handle unauthorized access - but don't redirect on login page
          if (!window.location.pathname.includes('/login')) {
            window.location.href = '/login';
          }
        }
        return Promise.reject(error);
      }
    );
  }

  // Helper method to use mock API when backend is unavailable
  private async tryRequest<T>(
    realApiCall: () => Promise<ApiResponse<T>>,
    mockApiCall: () => Promise<ApiResponse<T>>
  ): Promise<ApiResponse<T>> {
    // Always use real API when mock is disabled
    if (this.disableMockFallback) {
      console.log('🔵 Using Real API (mock disabled)');
      return await realApiCall();
    }

    // If forcing real API, always try real API first
    if (this.forceRealApi || !this.useMockApi) {
      try {
        console.log('🔵 Trying Real API (forced or default)');
        const result = await realApiCall();
        console.log('✅ Real API Success:', result);
        this.hasTestedConnection = true;
        return result;
      } catch (error: any) {
        console.log('❌ Real API Error:', error);
        // Only fallback to mock on connection errors, not auth errors
        if ((error.code === 'ERR_NETWORK' || error.code === 'ECONNREFUSED') && !this.hasTestedConnection && !this.forceRealApi) {
          console.warn('Backend not available, using mock API');
          this.useMockApi = true;
          return await mockApiCall();
        }
        throw error;
      }
    }

    console.log('🟡 Using Mock API');
    return await mockApiCall();
  }

  // Auth endpoints
  async login(credentials: LoginRequest): Promise<ApiResponse<User>> {
    return this.tryRequest(
      async () => {
        try {
          const response: AxiosResponse<User> = await this.api.post('/api/login', credentials);
          return { success: true, data: response.data };
        } catch (error: any) {
          return { 
            success: false, 
            error: error.response?.data?.message || 'Login failed' 
          };
        }
      },
      () => mockApiService.login(credentials)
    );
  }

  async logout(): Promise<ApiResponse<void>> {
    return this.tryRequest(
      async () => {
        try {
          await this.api.post('/api/logout');
          return { success: true };
        } catch (error: any) {
          return { 
            success: false, 
            error: error.response?.data?.message || 'Logout failed' 
          };
        }
      },
      () => mockApiService.logout()
    );
  }

  async getCurrentUser(): Promise<ApiResponse<User>> {
    return this.tryRequest(
      async () => {
        try {
          const response: AxiosResponse<User> = await this.api.get('/api/current_user');
          return { success: true, data: response.data };
        } catch (error: any) {
          return { 
            success: false, 
            error: error.response?.data?.message || 'Failed to get current user' 
          };
        }
      },
      () => mockApiService.getCurrentUser()
    );
  }

  // Task endpoints
  async getTasks(): Promise<ApiResponse<Task[]>> {
    return this.tryRequest(
      async () => {
        try {
          const response: AxiosResponse<Task[]> = await this.api.get('/api/tasks');
          return { success: true, data: response.data };
        } catch (error: any) {
          return { 
            success: false, 
            error: error.response?.data?.message || 'Failed to fetch tasks' 
          };
        }
      },
      () => mockApiService.getTasks()
    );
  }

  async getTask(id: number): Promise<ApiResponse<Task>> {
    return this.tryRequest(
      async () => {
        try {
          const response: AxiosResponse<Task> = await this.api.get(`/api/tasks/${id}`);
          return { success: true, data: response.data };
        } catch (error: any) {
          return { 
            success: false, 
            error: error.response?.data?.message || 'Failed to fetch task' 
          };
        }
      },
      () => mockApiService.getTask(id)
    );
  }

  async createTask(task: CreateTaskRequest): Promise<ApiResponse<Task>> {
    return this.tryRequest(
      async () => {
        try {
          const response: AxiosResponse<Task> = await this.api.post('/api/tasks', task);
          return { success: true, data: response.data };
        } catch (error: any) {
          return { 
            success: false, 
            error: error.response?.data?.message || 'Failed to create task' 
          };
        }
      },
      () => mockApiService.createTask()
    );
  }

  async updateTask(id: number, task: UpdateTaskRequest): Promise<ApiResponse<Task>> {
    return this.tryRequest(
      async () => {
        try {
          const response: AxiosResponse<Task> = await this.api.put(`/api/tasks/${id}`, task);
          return { success: true, data: response.data };
        } catch (error: any) {
          return { 
            success: false, 
            error: error.response?.data?.message || 'Failed to update task' 
          };
        }
      },
      () => mockApiService.updateTask()
    );
  }

  async deleteTask(id: number): Promise<ApiResponse<void>> {
    return this.tryRequest(
      async () => {
        try {
          await this.api.delete(`/api/tasks/${id}`);
          return { success: true };
        } catch (error: any) {
          return { 
            success: false, 
            error: error.response?.data?.message || 'Failed to delete task' 
          };
        }
      },
      () => mockApiService.deleteTask()
    );
  }

  async markTaskAsRead(id: number): Promise<ApiResponse<void>> {
    return this.tryRequest(
      async () => {
        try {
          await this.api.post(`/api/tasks/${id}/mark_read`);
          return { success: true };
        } catch (error: any) {
          return { 
            success: false, 
            error: error.response?.data?.message || 'Failed to mark task as read' 
          };
        }
      },
      () => mockApiService.markTaskAsRead()
    );
  }

  // Report endpoints
  async getReports(): Promise<ApiResponse<Report[]>> {
    return this.tryRequest(
      async () => {
        try {
          const response: AxiosResponse<Report[]> = await this.api.get('/api/reports');
          return { success: true, data: response.data };
        } catch (error: any) {
          return { 
            success: false, 
            error: error.response?.data?.message || 'Failed to fetch reports' 
          };
        }
      },
      () => mockApiService.getReports()
    );
  }

  async getReport(id: number): Promise<ApiResponse<Report>> {
    return this.tryRequest(
      async () => {
        try {
          const response: AxiosResponse<Report> = await this.api.get(`/api/reports/${id}`);
          return { success: true, data: response.data };
        } catch (error: any) {
          return { 
            success: false, 
            error: error.response?.data?.message || 'Failed to fetch report' 
          };
        }
      },
      () => mockApiService.getReport(id)
    );
  }

  async createReport(report: CreateReportRequest): Promise<ApiResponse<Report>> {
    return this.tryRequest(
      async () => {
        try {
          const response: AxiosResponse<Report> = await this.api.post('/api/reports', report);
          return { success: true, data: response.data };
        } catch (error: any) {
          return { 
            success: false, 
            error: error.response?.data?.message || 'Failed to create report' 
          };
        }
      },
      () => mockApiService.createReport()
    );
  }

  async markReportAsRead(id: number): Promise<ApiResponse<void>> {
    return this.tryRequest(
      async () => {
        try {
          await this.api.post(`/api/reports/${id}/mark_read`);
          return { success: true };
        } catch (error: any) {
          return { 
            success: false, 
            error: error.response?.data?.message || 'Failed to mark report as read' 
          };
        }
      },
      () => mockApiService.markReportAsRead()
    );
  }

  // Reminder endpoints
  async getReminders(): Promise<ApiResponse<Reminder[]>> {
    return this.tryRequest(
      async () => {
        try {
          const response: AxiosResponse<Reminder[]> = await this.api.get('/api/reminders');
          return { success: true, data: response.data };
        } catch (error: any) {
          return { 
            success: false, 
            error: error.response?.data?.message || 'Failed to fetch reminders' 
          };
        }
      },
      () => mockApiService.getReminders()
    );
  }

  async getTodayReminders(): Promise<ApiResponse<Reminder[]>> {
    return this.tryRequest(
      async () => {
        try {
          const response: AxiosResponse<Reminder[]> = await this.api.get('/api/today_reminders');
          return { success: true, data: response.data };
        } catch (error: any) {
          return { 
            success: false, 
            error: error.response?.data?.message || 'Failed to fetch today reminders' 
          };
        }
      },
      () => mockApiService.getTodayReminders()
    );
  }

  async createReminder(reminder: CreateReminderRequest): Promise<ApiResponse<Reminder>> {
    return this.tryRequest(
      async () => {
        try {
          const response: AxiosResponse<Reminder> = await this.api.post('/api/reminders', reminder);
          return { success: true, data: response.data };
        } catch (error: any) {
          return { 
            success: false, 
            error: error.response?.data?.message || 'Failed to create reminder' 
          };
        }
      },
      () => mockApiService.createReminder()
    );
  }

  // User endpoints
  async getUsers(): Promise<ApiResponse<User[]>> {
    return this.tryRequest(
      async () => {
        try {
          const response: AxiosResponse<User[]> = await this.api.get('/api/users');
          return { success: true, data: response.data };
        } catch (error: any) {
          return { 
            success: false, 
            error: error.response?.data?.message || 'Failed to fetch users' 
          };
        }
      },
      () => mockApiService.getUsers()
    );
  }

  // Notification endpoints
  async getNotificationCounts(): Promise<ApiResponse<NotificationCounts>> {
    return this.tryRequest(
      async () => {
        try {
          const response: AxiosResponse<NotificationCounts> = await this.api.get('/api/notification_counts');
          return { success: true, data: response.data };
        } catch (error: any) {
          return { 
            success: false, 
            error: error.response?.data?.message || 'Failed to fetch notification counts' 
          };
        }
      },
      () => mockApiService.getNotificationCounts()
    );
  }
}

export const apiService = new ApiService();

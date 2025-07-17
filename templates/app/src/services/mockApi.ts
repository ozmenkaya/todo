import type { User, Task, Report, Reminder, NotificationCounts, ApiResponse } from '../types';

// Mock data for development
const mockUser: User = {
  id: 1,
  username: 'admin',
  email: 'admin@company.com',
  role: 'admin',
  department: 'IT',
  first_name: 'Admin',
  last_name: 'User',
  created_at: '2025-01-01T00:00:00Z'
};

const mockTasks: Task[] = [
  {
    id: 1,
    title: '[MOCK] Proje planını hazırla',
    description: 'Q1 2025 için detaylı proje planı hazırlanması gerekiyor.',
    status: 'in_progress',
    priority: 'high',
    created_by: 1,
    assigned_to: [1, 2],
    due_date: '2025-07-15T00:00:00Z',
    created_at: '2025-07-10T00:00:00Z',
    updated_at: '2025-07-11T00:00:00Z',
    creator: mockUser,
    assignees: [mockUser],
    is_read: false
  },
  {
    id: 2,
    title: '[MOCK] Müşteri toplantısı',
    description: 'ABC şirketi ile ürün demo toplantısı',
    status: 'pending',
    priority: 'urgent',
    created_by: 1,
    assigned_to: [1],
    due_date: '2025-07-12T00:00:00Z',
    created_at: '2025-07-11T00:00:00Z',
    updated_at: '2025-07-11T00:00:00Z',
    creator: mockUser,
    assignees: [mockUser],
    is_read: true
  },
  {
    id: 3,
    title: '[MOCK] Rapor hazırla',
    description: 'Aylık performans raporu',
    status: 'completed',
    priority: 'medium',
    created_by: 1,
    assigned_to: [1],
    due_date: '2025-07-10T00:00:00Z',
    created_at: '2025-07-09T00:00:00Z',
    updated_at: '2025-07-10T00:00:00Z',
    completed_at: '2025-07-10T15:30:00Z',
    creator: mockUser,
    assignees: [mockUser],
    is_read: true
  }
];

const mockReports: Report[] = [
  {
    id: 1,
    title: '[MOCK] Haftalık İlerleme Raporu',
    content: 'Bu hafta tamamlanan işler ve gelecek hafta planları...',
    created_by: 1,
    shared_with: [1, 2, 3],
    created_at: '2025-07-11T00:00:00Z',
    updated_at: '2025-07-11T00:00:00Z',
    creator: mockUser,
    shared_users: [mockUser],
    is_read: false
  },
  {
    id: 2,
    title: '[MOCK] Müşteri Memnuniyet Anketi',
    content: 'Son dönemde yapılan müşteri memnuniyet anket sonuçları...',
    created_by: 1,
    shared_with: [1],
    created_at: '2025-07-10T00:00:00Z',
    updated_at: '2025-07-10T00:00:00Z',
    creator: mockUser,
    shared_users: [mockUser],
    is_read: true
  }
];

const mockReminders: Reminder[] = [
  {
    id: 1,
    title: 'Toplantı hatırlatması',
    description: 'Saat 14:00\'te ekip toplantısı',
    reminder_time: '2025-07-11T14:00:00Z',
    user_id: 1,
    created_at: '2025-07-11T00:00:00Z',
    is_completed: false
  },
  {
    id: 2,
    title: 'Rapor teslimi',
    description: 'Aylık raporu teslim etmeyi unutma',
    reminder_time: '2025-07-11T17:00:00Z',
    user_id: 1,
    created_at: '2025-07-11T00:00:00Z',
    is_completed: false
  }
];

// Mock API service for development
export class MockApiService {
  private delay(ms: number = 500): Promise<void> {
    return new Promise(resolve => setTimeout(resolve, ms));
  }

  async login(credentials: { username: string; password: string }): Promise<ApiResponse<User>> {
    await this.delay();
    
    if (credentials.username === 'admin' && credentials.password === 'admin123') {
      return { success: true, data: mockUser };
    }
    
    return { success: false, error: 'Kullanıcı adı veya şifre hatalı' };
  }

  async logout(): Promise<ApiResponse<void>> {
    await this.delay();
    return { success: true };
  }

  async getCurrentUser(): Promise<ApiResponse<User>> {
    await this.delay();
    // Simulate not authenticated for first load
    return { success: false, error: 'Not authenticated' };
  }

  async getTasks(): Promise<ApiResponse<Task[]>> {
    await this.delay();
    return { success: true, data: mockTasks };
  }

  async getTask(id: number): Promise<ApiResponse<Task>> {
    await this.delay();
    const task = mockTasks.find(t => t.id === id);
    if (task) {
      return { success: true, data: task };
    }
    return { success: false, error: 'Task not found' };
  }

  async createTask(): Promise<ApiResponse<Task>> {
    await this.delay();
    return { success: false, error: 'Not implemented in mock' };
  }

  async updateTask(): Promise<ApiResponse<Task>> {
    await this.delay();
    return { success: false, error: 'Not implemented in mock' };
  }

  async deleteTask(): Promise<ApiResponse<void>> {
    await this.delay();
    return { success: false, error: 'Not implemented in mock' };
  }

  async markTaskAsRead(): Promise<ApiResponse<void>> {
    await this.delay();
    return { success: true };
  }

  async getReports(): Promise<ApiResponse<Report[]>> {
    await this.delay();
    return { success: true, data: mockReports };
  }

  async getReport(id: number): Promise<ApiResponse<Report>> {
    await this.delay();
    const report = mockReports.find(r => r.id === id);
    if (report) {
      return { success: true, data: report };
    }
    return { success: false, error: 'Report not found' };
  }

  async createReport(): Promise<ApiResponse<Report>> {
    await this.delay();
    return { success: false, error: 'Not implemented in mock' };
  }

  async markReportAsRead(): Promise<ApiResponse<void>> {
    await this.delay();
    return { success: true };
  }

  async getReminders(): Promise<ApiResponse<Reminder[]>> {
    await this.delay();
    return { success: true, data: mockReminders };
  }

  async getTodayReminders(): Promise<ApiResponse<Reminder[]>> {
    await this.delay();
    return { success: true, data: mockReminders };
  }

  async createReminder(): Promise<ApiResponse<Reminder>> {
    await this.delay();
    return { success: false, error: 'Not implemented in mock' };
  }

  async getUsers(): Promise<ApiResponse<User[]>> {
    await this.delay();
    return { success: true, data: [mockUser] };
  }

  async getNotificationCounts(): Promise<ApiResponse<NotificationCounts>> {
    await this.delay();
    return { 
      success: true, 
      data: { 
        tasks: mockTasks.filter(t => !t.is_read).length,
        reminders: mockReminders.filter(r => !r.is_completed).length,
        reports: mockReports.filter(r => !r.is_read).length
      }
    };
  }
}

export const mockApiService = new MockApiService();

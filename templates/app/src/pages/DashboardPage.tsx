import React, { useState, useEffect } from 'react';
import {
  Container,
  Card,
  CardContent,
  Typography,
  Box,
  Chip,
  LinearProgress,
  IconButton,
  Paper,
} from '@mui/material';
import {
  Assignment,
  Description,
  CheckCircle,
  Schedule,
  Warning,
  Refresh,
} from '@mui/icons-material';
import { useAuth } from '../contexts/AuthContext';
import { useNotification } from '../contexts/NotificationContext';
import { apiService } from '../services/api';
import type { Task, Report, Reminder } from '../types';

const DashboardPage: React.FC = () => {
  const [loading, setLoading] = useState(true);
  const [tasks, setTasks] = useState<Task[]>([]);
  const [reports, setReports] = useState<Report[]>([]);
  const [reminders, setReminders] = useState<Reminder[]>([]);

  const { state: authState } = useAuth();
  const { addNotification } = useNotification();

  const loadDashboardData = async () => {
    setLoading(true);
    try {
      const [tasksRes, reportsRes, remindersRes] = await Promise.all([
        apiService.getTasks(),
        apiService.getReports(),
        apiService.getTodayReminders(),
      ]);

      if (tasksRes.success) setTasks(tasksRes.data || []);
      if (reportsRes.success) setReports(reportsRes.data || []);
      if (remindersRes.success) setReminders(remindersRes.data || []);
    } catch (error) {
      addNotification({
        type: 'error',
        title: 'Hata',
        message: 'Dashboard verileri yüklenirken hata oluştu',
      });
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadDashboardData();
  }, []);

  const getTaskStats = () => {
    const completed = tasks.filter(t => t.status === 'completed').length;
    const inProgress = tasks.filter(t => t.status === 'in_progress').length;
    const pending = tasks.filter(t => t.status === 'pending').length;
    const overdue = tasks.filter(t => 
      t.due_date && 
      new Date(t.due_date) < new Date() && 
      t.status !== 'completed'
    ).length;

    return { completed, inProgress, pending, overdue, total: tasks.length };
  };

  const taskStats = getTaskStats();

  if (loading) {
    return (
      <Container maxWidth="lg">
        <Box sx={{ width: '100%', mt: 2 }}>
          <LinearProgress />
        </Box>
      </Container>
    );
  }

  return (
    <Container maxWidth="lg" sx={{ px: { xs: 1, sm: 2 } }}>
      <Box sx={{ mt: 1, mb: 4 }}>
        {/* Welcome Section */}
        <Paper sx={{ p: 3, mb: 3, background: 'linear-gradient(135deg, #1976d2 0%, #42a5f5 100%)', color: 'white', borderRadius: 2 }}>
          <Box display="flex" justifyContent="space-between" alignItems="center">
            <Box>
              <Typography 
                variant="h4" 
                gutterBottom 
                sx={{ 
                  fontSize: { xs: '1.75rem', sm: '2.125rem' },
                  fontWeight: 500 
                }}
              >
                Hoş geldiniz, {authState.user?.first_name || authState.user?.username}!
              </Typography>
              <Typography variant="subtitle1" sx={{ opacity: 0.9 }}>
                {authState.user?.role === 'admin' ? 'Sistem Yöneticisi' :
                 authState.user?.role === 'manager' ? 'Yönetici' : 'Çalışan'} 
                {authState.user?.department && ` • ${authState.user.department}`}
              </Typography>
            </Box>
            <IconButton 
              color="inherit" 
              onClick={loadDashboardData}
              sx={{ 
                backgroundColor: 'rgba(255,255,255,0.1)',
                '&:hover': {
                  backgroundColor: 'rgba(255,255,255,0.2)',
                }
              }}
            >
              <Refresh />
            </IconButton>
          </Box>
        </Paper>

        {/* Stats Cards */}
        <Box sx={{ 
          display: 'grid', 
          gridTemplateColumns: { xs: '1fr', sm: 'repeat(2, 1fr)', md: 'repeat(4, 1fr)' }, 
          gap: 2, 
          mb: 3 
        }}>
          <Card sx={{ borderRadius: 2, boxShadow: 1 }}>
            <CardContent sx={{ textAlign: 'center', py: 3 }}>
              <Assignment sx={{ fontSize: 40, color: '#1976d2', mb: 1 }} />
              <Typography variant="h4" sx={{ fontWeight: 600, color: '#1976d2' }}>
                {taskStats.total}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Toplam Görev
              </Typography>
            </CardContent>
          </Card>

          <Card sx={{ borderRadius: 2, boxShadow: 1 }}>
            <CardContent sx={{ textAlign: 'center', py: 3 }}>
              <CheckCircle sx={{ fontSize: 40, color: '#4caf50', mb: 1 }} />
              <Typography variant="h4" sx={{ fontWeight: 600, color: '#4caf50' }}>
                {taskStats.completed}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Tamamlanan
              </Typography>
            </CardContent>
          </Card>

          <Card sx={{ borderRadius: 2, boxShadow: 1 }}>
            <CardContent sx={{ textAlign: 'center', py: 3 }}>
              <Schedule sx={{ fontSize: 40, color: '#ff9800', mb: 1 }} />
              <Typography variant="h4" sx={{ fontWeight: 600, color: '#ff9800' }}>
                {taskStats.inProgress}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Devam Eden
              </Typography>
            </CardContent>
          </Card>

          <Card sx={{ borderRadius: 2, boxShadow: 1 }}>
            <CardContent sx={{ textAlign: 'center', py: 3 }}>
              <Warning sx={{ fontSize: 40, color: '#f44336', mb: 1 }} />
              <Typography variant="h4" sx={{ fontWeight: 600, color: '#f44336' }}>
                {taskStats.overdue}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Geciken
              </Typography>
            </CardContent>
          </Card>
        </Box>

        {/* Recent Tasks */}
        <Card sx={{ mb: 3, borderRadius: 2, boxShadow: 1 }}>
          <CardContent>
            <Typography variant="h6" gutterBottom sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
              <Assignment sx={{ mr: 1, color: '#1976d2' }} />
              Son Görevler
            </Typography>
            {tasks.slice(0, 5).map((task) => (
              <Box key={task.id} sx={{ 
                p: 2, 
                borderRadius: 1, 
                backgroundColor: '#f5f5f5', 
                mb: 1,
                display: 'flex',
                justifyContent: 'space-between',
                alignItems: 'center'
              }}>
                <Box>
                  <Typography variant="subtitle2" sx={{ fontWeight: 500 }}>
                    {task.title}
                  </Typography>
                  <Typography variant="caption" color="text.secondary">
                    {task.description}
                  </Typography>
                </Box>
                <Chip 
                  label={
                    task.status === 'completed' ? 'Tamamlandı' :
                    task.status === 'in_progress' ? 'Devam Ediyor' : 'Beklemede'
                  }
                  size="small"
                  color={
                    task.status === 'completed' ? 'success' :
                    task.status === 'in_progress' ? 'primary' : 'default'
                  }
                />
              </Box>
            ))}
            {tasks.length === 0 && (
              <Typography variant="body2" color="text.secondary" sx={{ textAlign: 'center', py: 2 }}>
                Henüz görev bulunmuyor
              </Typography>
            )}
          </CardContent>
        </Card>

        {/* Recent Reports & Reminders */}
        <Box sx={{ 
          display: 'grid', 
          gridTemplateColumns: { xs: '1fr', md: 'repeat(2, 1fr)' }, 
          gap: 2 
        }}>
          {/* Recent Reports */}
          <Card sx={{ borderRadius: 2, boxShadow: 1 }}>
            <CardContent>
              <Typography variant="h6" gutterBottom sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                <Description sx={{ mr: 1, color: '#1976d2' }} />
                Son Raporlar
              </Typography>
              {reports.slice(0, 3).map((report) => (
                <Box key={report.id} sx={{ 
                  p: 2, 
                  borderRadius: 1, 
                  backgroundColor: '#f5f5f5', 
                  mb: 1 
                }}>
                  <Typography variant="subtitle2" sx={{ fontWeight: 500 }}>
                    {report.title}
                  </Typography>
                  <Typography variant="caption" color="text.secondary">
                    {new Date(report.created_at).toLocaleDateString('tr-TR')}
                  </Typography>
                </Box>
              ))}
              {reports.length === 0 && (
                <Typography variant="body2" color="text.secondary" sx={{ textAlign: 'center', py: 2 }}>
                  Henüz rapor bulunmuyor
                </Typography>
              )}
            </CardContent>
          </Card>

          {/* Today's Reminders */}
          <Card sx={{ borderRadius: 2, boxShadow: 1 }}>
            <CardContent>
              <Typography variant="h6" gutterBottom sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                <Schedule sx={{ mr: 1, color: '#1976d2' }} />
                Bugünkü Hatırlatmalar
              </Typography>
              {reminders.slice(0, 3).map((reminder) => (
                <Box key={reminder.id} sx={{ 
                  p: 2, 
                  borderRadius: 1, 
                  backgroundColor: reminder.is_completed ? '#e8f5e8' : '#fff3e0', 
                  mb: 1,
                  display: 'flex',
                  justifyContent: 'space-between',
                  alignItems: 'center'
                }}>
                  <Box>
                    <Typography variant="subtitle2" sx={{ fontWeight: 500 }}>
                      {reminder.title}
                    </Typography>
                    <Typography variant="caption" color="text.secondary">
                      {new Date(reminder.reminder_time).toLocaleTimeString('tr-TR', { 
                        hour: '2-digit', 
                        minute: '2-digit' 
                      })}
                    </Typography>
                  </Box>
                  {reminder.is_completed && (
                    <CheckCircle sx={{ color: '#4caf50', fontSize: 20 }} />
                  )}
                </Box>
              ))}
              {reminders.length === 0 && (
                <Typography variant="body2" color="text.secondary" sx={{ textAlign: 'center', py: 2 }}>
                  Bugün hatırlatma yok
                </Typography>
              )}
            </CardContent>
          </Card>
        </Box>
      </Box>
    </Container>
  );
};

export default DashboardPage;

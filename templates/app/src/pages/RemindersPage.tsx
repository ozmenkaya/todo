import React, { useState, useEffect } from 'react';
import {
  Container,
  Typography,
  Box,
  Card,
  Fab,
  CircularProgress,
  Alert,
  Chip,
  IconButton,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  ListItemSecondaryAction,
  Avatar,
  Divider,
} from '@mui/material';
import { Add, CheckCircle, Schedule } from '@mui/icons-material';
import type { Reminder } from '../types';
import { apiService } from '../services/api';
import CreateReminderModal from '../components/CreateReminderModal';

const RemindersPage: React.FC = () => {
  const [reminders, setReminders] = useState<Reminder[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [createModalOpen, setCreateModalOpen] = useState(false);

  useEffect(() => {
    loadReminders();
  }, []);

  const loadReminders = async () => {
    try {
      setLoading(true);
      setError(null);
      const response = await apiService.getReminders();
      if (response.success) {
        setReminders(response.data || []);
      } else {
        setError(response.error || 'Hatırlatmalar yüklenemedi');
      }
    } catch (error) {
      setError('Bir hata oluştu');
      console.error('Failed to load reminders:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleReminderCreated = (newReminder: Reminder) => {
    setReminders([newReminder, ...reminders]);
  };

  const isOverdue = (reminderTime: string) => {
    return new Date(reminderTime) < new Date();
  };

  const isToday = (reminderTime: string) => {
    const today = new Date();
    const reminder = new Date(reminderTime);
    return today.toDateString() === reminder.toDateString();
  };

  if (loading) {
    return (
      <Container maxWidth="lg">
        <Box sx={{ display: 'flex', justifyContent: 'center', mt: 4 }}>
          <CircularProgress />
        </Box>
      </Container>
    );
  }

  return (
    <Container maxWidth="lg" sx={{ px: { xs: 1, sm: 2 } }}>
      <Box sx={{ mt: 1, mb: 4 }}>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
          <Typography 
            variant="h4" 
            gutterBottom 
            sx={{ 
              mb: 0, 
              fontSize: { xs: '1.75rem', sm: '2.125rem' },
              fontWeight: 500,
              color: '#1976d2'
            }}
          >
            Hatırlatmalar
          </Typography>
        </Box>

        {error && (
          <Alert severity="error" sx={{ mb: 2 }} onClose={() => setError(null)}>
            {error}
          </Alert>
        )}

        {/* List View */}
        <Card sx={{ borderRadius: 2, boxShadow: 1 }}>
          <List sx={{ p: 0 }}>
            {reminders.map((reminder, index) => (
              <React.Fragment key={reminder.id}>
                <ListItem 
                  sx={{ 
                    py: 2,
                    opacity: reminder.is_completed ? 0.7 : 1,
                    borderLeft: isOverdue(reminder.reminder_time) && !reminder.is_completed ? '4px solid #f44336' : 
                               isToday(reminder.reminder_time) && !reminder.is_completed ? '4px solid #2196f3' : 'none'
                  }}
                >
                  <ListItemIcon>
                    <Avatar 
                      sx={{ 
                        backgroundColor: reminder.is_completed ? '#4caf50' : 
                                        isOverdue(reminder.reminder_time) ? '#f44336' :
                                        isToday(reminder.reminder_time) ? '#2196f3' : '#ff9800',
                        width: 48, 
                        height: 48 
                      }}
                    >
                      {reminder.is_completed ? <CheckCircle /> : <Schedule />}
                    </Avatar>
                  </ListItemIcon>
                  
                  <ListItemText
                    primary={
                      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, flexWrap: 'wrap' }}>
                        <Typography variant="subtitle1" component="span" sx={{ fontWeight: 500 }}>
                          {reminder.title}
                        </Typography>
                        {reminder.is_completed && (
                          <Chip
                            label="Tamamlandı"
                            size="small"
                            color="success"
                            sx={{ fontSize: '0.7rem' }}
                          />
                        )}
                        {isToday(reminder.reminder_time) && !reminder.is_completed && (
                          <Chip
                            label="Bugün"
                            size="small"
                            color="primary"
                            sx={{ fontSize: '0.7rem' }}
                          />
                        )}
                        {isOverdue(reminder.reminder_time) && !reminder.is_completed && (
                          <Chip
                            label="Gecikmiş"
                            size="small"
                            color="error"
                            sx={{ fontSize: '0.7rem' }}
                          />
                        )}
                      </Box>
                    }
                    secondary={
                      <Box sx={{ mt: 1 }}>
                        {reminder.description && (
                          <Typography variant="body2" color="text.secondary" sx={{ mb: 0.5 }}>
                            {reminder.description}
                          </Typography>
                        )}
                        <Typography variant="caption" color="text.secondary" sx={{ fontStyle: 'italic' }}>
                          Hatırlatma: {new Date(reminder.reminder_time).toLocaleString('tr-TR')}
                        </Typography>
                      </Box>
                    }
                  />
                  
                  <ListItemSecondaryAction>
                    <IconButton 
                      size="small" 
                      color={reminder.is_completed ? 'success' : 'default'}
                      sx={{ 
                        backgroundColor: 'rgba(0,0,0,0.04)',
                        '&:hover': {
                          backgroundColor: 'rgba(0,0,0,0.08)',
                        }
                      }}
                    >
                      <CheckCircle />
                    </IconButton>
                  </ListItemSecondaryAction>
                </ListItem>
                {index < reminders.length - 1 && <Divider />}
              </React.Fragment>
            ))}
          </List>
        </Card>

        {reminders.length === 0 && !loading && (
          <Box sx={{ textAlign: 'center', mt: 6, py: 4 }}>
            <Schedule sx={{ fontSize: 64, color: 'text.secondary', mb: 2 }} />
            <Typography variant="h6" color="text.secondary" sx={{ mb: 1 }}>
              Henüz hatırlatma bulunmuyor
            </Typography>
            <Typography variant="body2" color="text.secondary">
              Yeni hatırlatma oluşturmak için + butonuna tıklayın
            </Typography>
          </Box>
        )}

        <Fab
          color="primary"
          aria-label="add"
          sx={{ 
            position: 'fixed', 
            bottom: { xs: 88, md: 24 }, // Higher on mobile to avoid bottom nav
            right: 24,
            boxShadow: 3 
          }}
          onClick={() => setCreateModalOpen(true)}
        >
          <Add />
        </Fab>

        <CreateReminderModal
          open={createModalOpen}
          onClose={() => setCreateModalOpen(false)}
          onSuccess={handleReminderCreated}
        />
      </Box>
    </Container>
  );
};

export default RemindersPage;

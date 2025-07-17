import React, { useState, useEffect } from 'react';
import {
  Container,
  Typography,
  Box,
  Card,
  Chip,
  Fab,
  CircularProgress,
  Alert,
  Button,
  IconButton,
  Menu,
  MenuItem,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  ListItemSecondaryAction,
  Avatar,
  Divider,
  ToggleButton,
  ToggleButtonGroup,
} from '@mui/material';
import { 
  Add, 
  MoreVert, 
  Edit, 
  Delete, 
  Assignment,
  CheckCircle,
  Schedule,
  Warning
} from '@mui/icons-material';
import { useNavigate } from 'react-router-dom';
import type { Task } from '../types';
import { apiService } from '../services/api';
import CreateTaskModal from '../components/CreateTaskModal';

const TasksPage: React.FC = () => {
  const [tasks, setTasks] = useState<Task[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [createModalOpen, setCreateModalOpen] = useState(false);
  const [editTask, setEditTask] = useState<Task | null>(null);
  const [anchorEl, setAnchorEl] = useState<null | HTMLElement>(null);
  const [selectedTaskId, setSelectedTaskId] = useState<number | null>(null);
  const [statusFilter, setStatusFilter] = useState<string>('all');
  
  const navigate = useNavigate();

  useEffect(() => {
    loadTasks();
  }, []);

  const loadTasks = async () => {
    try {
      setLoading(true);
      setError(null);
      const response = await apiService.getTasks();
      if (response.success) {
        setTasks(response.data || []);
      } else {
        setError(response.error || 'Görevler yüklenemedi');
      }
    } catch (error) {
      setError('Bir hata oluştu');
      console.error('Failed to load tasks:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleTaskCreated = (newTask: Task) => {
    setTasks([newTask, ...tasks]);
  };

  const handleTaskUpdated = (updatedTask: Task) => {
    setTasks(tasks.map(task => 
      task.id === updatedTask.id ? updatedTask : task
    ));
    setEditTask(null);
  };

  const handleEditTask = (task: Task) => {
    setEditTask(task);
    setCreateModalOpen(true);
    handleMenuClose();
  };

  const handleDeleteTask = async (taskId: number) => {
    try {
      const response = await apiService.deleteTask(taskId);
      if (response.success) {
        setTasks(tasks.filter(task => task.id !== taskId));
      } else {
        setError(response.error || 'Görev silinemedi');
      }
    } catch (error) {
      setError('Bir hata oluştu');
      console.error('Failed to delete task:', error);
    }
    handleMenuClose();
  };

  const handleMenuClick = (event: React.MouseEvent<HTMLElement>, taskId: number) => {
    setAnchorEl(event.currentTarget);
    setSelectedTaskId(taskId);
  };

  const handleMenuClose = () => {
    setAnchorEl(null);
    setSelectedTaskId(null);
  };

  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case 'urgent': return '#f44336';
      case 'high': return '#ff9800';
      case 'medium': return '#2196f3';
      case 'low': return '#4caf50';
      default: return '#757575';
    }
  };

  const getPriorityLabel = (priority: string) => {
    switch (priority) {
      case 'urgent': return 'Acil';
      case 'high': return 'Yüksek';
      case 'medium': return 'Orta';
      case 'low': return 'Düşük';
      default: return priority;
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'completed': return '#4caf50';
      case 'in_progress': return '#2196f3';
      case 'pending': return '#ff9800';
      default: return '#757575';
    }
  };

  const getStatusLabel = (status: string) => {
    switch (status) {
      case 'completed': return 'Tamamlandı';
      case 'in_progress': return 'Devam Ediyor';
      case 'pending': return 'Beklemede';
      default: return status;
    }
  };

  // Filtrelenmiş görevleri hesapla
  const filteredTasks = tasks.filter(task => {
    if (statusFilter === 'all') return true;
    return task.status === statusFilter;
  });

  // Durum istatistikleri
  const getTaskStats = () => {
    return {
      all: tasks.length,
      pending: tasks.filter(t => t.status === 'pending').length,
      in_progress: tasks.filter(t => t.status === 'in_progress').length,
      completed: tasks.filter(t => t.status === 'completed').length,
    };
  };

  const stats = getTaskStats();

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
            Görevler
          </Typography>
        </Box>

        {error && (
          <Alert severity="error" sx={{ mb: 2 }} onClose={() => setError(null)}>
            {error}
          </Alert>
        )}

        {/* Filtre Butonları */}
        <Box sx={{ mb: 3 }}>
          <ToggleButtonGroup
            value={statusFilter}
            exclusive
            onChange={(_, newFilter) => setStatusFilter(newFilter || 'all')}
            size="small"
            sx={{ mb: 2 }}
          >
            <ToggleButton value="all">
              Tümü ({stats.all})
            </ToggleButton>
            <ToggleButton value="pending" sx={{ color: '#ff9800' }}>
              Beklemede ({stats.pending})
            </ToggleButton>
            <ToggleButton value="in_progress" sx={{ color: '#2196f3' }}>
              Devam Ediyor ({stats.in_progress})
            </ToggleButton>
            <ToggleButton value="completed" sx={{ color: '#4caf50' }}>
              Tamamlandı ({stats.completed})
            </ToggleButton>
          </ToggleButtonGroup>
        </Box>

        {/* Liste Görünümü */}
        <Card sx={{ borderRadius: 2, boxShadow: 1 }}>
          <List sx={{ p: 0 }}>
            {filteredTasks.map((task, index) => (
              <React.Fragment key={task.id}>
                <ListItem sx={{ py: 2 }}>
                  <ListItemIcon>
                    <Avatar 
                      sx={{ 
                        backgroundColor: task.status === 'completed' ? '#4caf50' : 
                                        task.status === 'in_progress' ? '#2196f3' : '#ff9800',
                        width: 48, 
                        height: 48 
                      }}
                    >
                      {task.status === 'completed' ? <CheckCircle /> :
                       task.status === 'in_progress' ? <Schedule /> :
                       task.priority === 'urgent' ? <Warning /> : <Assignment />}
                    </Avatar>
                  </ListItemIcon>
                  
                  <ListItemText
                    primary={
                      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, flexWrap: 'wrap' }}>
                        <Typography variant="subtitle1" component="span" sx={{ fontWeight: 500 }}>
                          {task.title}
                        </Typography>
                        <Chip
                          label={getPriorityLabel(task.priority)}
                          size="small"
                          sx={{ 
                            backgroundColor: getPriorityColor(task.priority), 
                            color: 'white',
                            fontSize: '0.7rem',
                            fontWeight: 500
                          }}
                        />
                        <Chip
                          label={getStatusLabel(task.status)}
                          size="small"
                          sx={{ 
                            backgroundColor: getStatusColor(task.status), 
                            color: 'white',
                            fontSize: '0.7rem'
                          }}
                        />
                      </Box>
                    }
                    secondary={
                      <Box sx={{ mt: 1 }}>
                        <Typography variant="body2" color="text.secondary" sx={{ mb: 0.5 }}>
                          {task.description}
                        </Typography>
                        
                        {/* Atanan Kişiler */}
                        {task.assignees && task.assignees.length > 0 && (
                          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 0.5, flexWrap: 'wrap' }}>
                            <Typography variant="caption" color="text.secondary" sx={{ fontWeight: 500 }}>
                              Atanan:
                            </Typography>
                            {task.assignees.map((assignee) => (
                              <Chip
                                key={assignee.id}
                                label={`${assignee.first_name} ${assignee.last_name}`}
                                size="small"
                                variant="outlined"
                                sx={{ 
                                  fontSize: '0.65rem',
                                  height: 20,
                                  '& .MuiChip-label': { px: 1 }
                                }}
                              />
                            ))}
                          </Box>
                        )}
                        
                        {/* Oluşturan Kişi */}
                        {task.creator && (
                          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 0.5 }}>
                            <Typography variant="caption" color="text.secondary">
                              Oluşturan: <strong>{task.creator.first_name} {task.creator.last_name}</strong>
                            </Typography>
                          </Box>
                        )}
                        
                        {task.due_date && (
                          <Typography variant="caption" color="text.secondary" sx={{ fontStyle: 'italic' }}>
                            Teslim: {new Date(task.due_date).toLocaleDateString('tr-TR', {
                              year: 'numeric',
                              month: 'long',
                              day: 'numeric',
                              hour: '2-digit',
                              minute: '2-digit'
                            })}
                          </Typography>
                        )}
                      </Box>
                    }
                  />
                  
                  <ListItemSecondaryAction>
                    <Box sx={{ display: 'flex', gap: 1, alignItems: 'center' }}>
                      <Button 
                        size="small" 
                        variant="outlined"
                        onClick={() => navigate(`/tasks/${task.id}`)}
                        sx={{ 
                          minWidth: 'auto',
                          px: 2,
                          display: { xs: 'none', sm: 'flex' }
                        }}
                      >
                        Detaylar
                      </Button>
                      <IconButton 
                        size="small"
                        onClick={(e) => handleMenuClick(e, task.id)}
                        sx={{ 
                          backgroundColor: 'rgba(0,0,0,0.04)',
                          '&:hover': {
                            backgroundColor: 'rgba(0,0,0,0.08)',
                          }
                        }}
                      >
                        <MoreVert />
                      </IconButton>
                    </Box>
                  </ListItemSecondaryAction>
                </ListItem>
                {index < filteredTasks.length - 1 && <Divider />}
              </React.Fragment>
            ))}
          </List>
        </Card>

        {filteredTasks.length === 0 && !loading && (
          <Box sx={{ textAlign: 'center', mt: 6, py: 4 }}>
            <Assignment sx={{ fontSize: 64, color: 'text.secondary', mb: 2 }} />
            <Typography variant="h6" color="text.secondary" sx={{ mb: 1 }}>
              {statusFilter === 'all' 
                ? 'Henüz görev bulunmuyor' 
                : `${getStatusLabel(statusFilter)} durumunda görev bulunmuyor`
              }
            </Typography>
            <Typography variant="body2" color="text.secondary">
              {statusFilter === 'all' 
                ? 'Yeni görev oluşturmak için + butonuna tıklayın'
                : 'Başka bir filtre seçerek diğer görevleri görüntüleyebilirsiniz'
              }
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

        <Menu
          anchorEl={anchorEl}
          open={Boolean(anchorEl)}
          onClose={handleMenuClose}
        >
          <MenuItem onClick={() => {
            const task = tasks.find(t => t.id === selectedTaskId);
            if (task) handleEditTask(task);
          }}>
            <Edit sx={{ mr: 1 }} />
            Düzenle
          </MenuItem>
          <MenuItem 
            onClick={() => selectedTaskId && handleDeleteTask(selectedTaskId)}
            sx={{ color: 'error.main' }}
          >
            <Delete sx={{ mr: 1 }} />
            Sil
          </MenuItem>
        </Menu>

        <CreateTaskModal
          open={createModalOpen}
          onClose={() => {
            setCreateModalOpen(false);
            setEditTask(null);
          }}
          onSuccess={editTask ? handleTaskUpdated : handleTaskCreated}
          editTask={editTask}
        />
      </Box>
    </Container>
  );
};

export default TasksPage;

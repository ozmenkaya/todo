import React, { useState, useEffect } from 'react';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  Button,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Chip,
  Box,
  type SelectChangeEvent,
} from '@mui/material';
import type { User, CreateTaskRequest, UpdateTaskRequest, Task } from '../types';
import { apiService } from '../services/api';

interface CreateTaskModalProps {
  open: boolean;
  onClose: () => void;
  onSuccess: (task: Task) => void;
  editTask?: Task | null;
}

const CreateTaskModal: React.FC<CreateTaskModalProps> = ({
  open,
  onClose,
  onSuccess,
  editTask
}) => {
  const [title, setTitle] = useState('');
  const [description, setDescription] = useState('');
  const [priority, setPriority] = useState<'low' | 'medium' | 'high' | 'urgent'>('medium');
  const [dueDate, setDueDate] = useState<Date | null>(null);
  const [assignedUsers, setAssignedUsers] = useState<number[]>([]);
  const [users, setUsers] = useState<User[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (open) {
      loadUsers();
      if (editTask) {
        setTitle(editTask.title);
        setDescription(editTask.description);
        setPriority(editTask.priority);
        setDueDate(editTask.due_date ? new Date(editTask.due_date) : null);
        setAssignedUsers(editTask.assigned_to || []);
      } else {
        resetForm();
      }
    }
  }, [open, editTask]);

  const loadUsers = async () => {
    try {
      const response = await apiService.getUsers();
      if (response.success) {
        setUsers(response.data || []);
      }
    } catch (error) {
      console.error('Failed to load users:', error);
    }
  };

  const resetForm = () => {
    setTitle('');
    setDescription('');
    setPriority('medium');
    setDueDate(null);
    setAssignedUsers([]);
    setError(null);
  };

  const handleSubmit = async () => {
    if (!title.trim()) {
      setError('Başlık gereklidir');
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const taskData = {
        title: title.trim(),
        description: description.trim(),
        priority,
        due_date: dueDate?.toISOString(),
        assigned_to: assignedUsers
      };

      let response;
      if (editTask) {
        response = await apiService.updateTask(editTask.id, taskData as UpdateTaskRequest);
      } else {
        response = await apiService.createTask(taskData as CreateTaskRequest);
      }

      if (response.success && response.data) {
        onSuccess(response.data);
        onClose();
      } else {
        setError(response.error || 'Görev kaydedilemedi');
      }
    } catch (error) {
      setError('Bir hata oluştu');
      console.error('Task save error:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleAssignedUsersChange = (event: SelectChangeEvent<number[]>) => {
    const value = event.target.value;
    setAssignedUsers(typeof value === 'string' ? [] : value);
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

  return (
    <Dialog open={open} onClose={onClose} maxWidth="sm" fullWidth>
      <DialogTitle>
        {editTask ? 'Görevi Düzenle' : 'Yeni Görev Oluştur'}
      </DialogTitle>
      <DialogContent>
        <Box sx={{ pt: 1 }}>
          <TextField
            autoFocus
            margin="dense"
            label="Başlık"
            fullWidth
            variant="outlined"
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            error={!!error && !title.trim()}
            helperText={error && !title.trim() ? 'Başlık gereklidir' : ''}
          />

          <TextField
            margin="dense"
            label="Açıklama"
            fullWidth
            multiline
            rows={3}
            variant="outlined"
            value={description}
            onChange={(e) => setDescription(e.target.value)}
          />

          <FormControl fullWidth margin="dense">
            <InputLabel>Öncelik</InputLabel>
            <Select
              value={priority}
              label="Öncelik"
              onChange={(e) => setPriority(e.target.value as any)}
            >
              <MenuItem value="low">
                <Chip
                  label="Düşük"
                  size="small"
                  sx={{ backgroundColor: getPriorityColor('low'), color: 'white' }}
                />
              </MenuItem>
              <MenuItem value="medium">
                <Chip
                  label="Orta"
                  size="small"
                  sx={{ backgroundColor: getPriorityColor('medium'), color: 'white' }}
                />
              </MenuItem>
              <MenuItem value="high">
                <Chip
                  label="Yüksek"
                  size="small"
                  sx={{ backgroundColor: getPriorityColor('high'), color: 'white' }}
                />
              </MenuItem>
              <MenuItem value="urgent">
                <Chip
                  label="Acil"
                  size="small"
                  sx={{ backgroundColor: getPriorityColor('urgent'), color: 'white' }}
                />
              </MenuItem>
            </Select>
          </FormControl>

          <TextField
            margin="dense"
            label="Teslim Tarihi"
            type="datetime-local"
            fullWidth
            variant="outlined"
            value={dueDate ? dueDate.toISOString().slice(0, 16) : ''}
            onChange={(e) => setDueDate(e.target.value ? new Date(e.target.value) : null)}
            InputLabelProps={{ shrink: true }}
          />

          <FormControl fullWidth margin="dense">
            <InputLabel>Atananlar</InputLabel>
            <Select
              multiple
              value={assignedUsers}
              label="Atananlar"
              onChange={handleAssignedUsersChange}
              renderValue={(selected) => (
                <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5 }}>
                  {selected.map((value) => {
                    const user = users.find(u => u.id === value);
                    return (
                      <Chip
                        key={value}
                        label={user ? `${user.first_name} ${user.last_name}` : value}
                        size="small"
                      />
                    );
                  })}
                </Box>
              )}
            >
              {users.map((user) => (
                <MenuItem key={user.id} value={user.id}>
                  {user.first_name} {user.last_name} ({user.username})
                </MenuItem>
              ))}
            </Select>
          </FormControl>

          {error && (
            <Box sx={{ color: 'error.main', mt: 1, fontSize: '0.875rem' }}>
              {error}
            </Box>
          )}
        </Box>
      </DialogContent>
      <DialogActions>
        <Button onClick={onClose}>İptal</Button>
        <Button
          onClick={handleSubmit}
          variant="contained"
          disabled={loading}
        >
          {loading ? 'Kaydediliyor...' : (editTask ? 'Güncelle' : 'Oluştur')}
        </Button>
      </DialogActions>
    </Dialog>
  );
};

export default CreateTaskModal;

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
import type { User, CreateReportRequest, Report } from '../types';
import { apiService } from '../services/api';

interface CreateReportModalProps {
  open: boolean;
  onClose: () => void;
  onSuccess: (report: Report) => void;
}

const CreateReportModal: React.FC<CreateReportModalProps> = ({
  open,
  onClose,
  onSuccess
}) => {
  const [title, setTitle] = useState('');
  const [content, setContent] = useState('');
  const [sharedUsers, setSharedUsers] = useState<number[]>([]);
  const [users, setUsers] = useState<User[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (open) {
      loadUsers();
      resetForm();
    }
  }, [open]);

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
    setContent('');
    setSharedUsers([]);
    setError(null);
  };

  const handleSubmit = async () => {
    if (!title.trim()) {
      setError('Başlık gereklidir');
      return;
    }

    if (!content.trim()) {
      setError('İçerik gereklidir');
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const reportData: CreateReportRequest = {
        title: title.trim(),
        content: content.trim(),
        shared_with: sharedUsers
      };

      const response = await apiService.createReport(reportData);

      if (response.success && response.data) {
        onSuccess(response.data);
        onClose();
      } else {
        setError(response.error || 'Rapor kaydedilemedi');
      }
    } catch (error) {
      setError('Bir hata oluştu');
      console.error('Report save error:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleSharedUsersChange = (event: SelectChangeEvent<number[]>) => {
    const value = event.target.value;
    setSharedUsers(typeof value === 'string' ? [] : value);
  };

  return (
    <Dialog open={open} onClose={onClose} maxWidth="md" fullWidth>
      <DialogTitle>
        Yeni Rapor Oluştur
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
            label="İçerik"
            fullWidth
            multiline
            rows={6}
            variant="outlined"
            value={content}
            onChange={(e) => setContent(e.target.value)}
            error={!!error && !content.trim()}
            helperText={error && !content.trim() ? 'İçerik gereklidir' : ''}
            placeholder="Rapor içeriğini buraya yazın..."
          />

          <FormControl fullWidth margin="dense">
            <InputLabel>Paylaşılacak Kişiler</InputLabel>
            <Select
              multiple
              value={sharedUsers}
              label="Paylaşılacak Kişiler"
              onChange={handleSharedUsersChange}
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
          {loading ? 'Kaydediliyor...' : 'Oluştur'}
        </Button>
      </DialogActions>
    </Dialog>
  );
};

export default CreateReportModal;

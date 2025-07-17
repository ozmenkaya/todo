import React, { useState } from 'react';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  Button,
  Box,
} from '@mui/material';
import type { CreateReminderRequest, Reminder } from '../types';
import { apiService } from '../services/api';

interface CreateReminderModalProps {
  open: boolean;
  onClose: () => void;
  onSuccess: (reminder: Reminder) => void;
}

const CreateReminderModal: React.FC<CreateReminderModalProps> = ({
  open,
  onClose,
  onSuccess
}) => {
  const [title, setTitle] = useState('');
  const [description, setDescription] = useState('');
  const [reminderTime, setReminderTime] = useState<Date | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const resetForm = () => {
    setTitle('');
    setDescription('');
    setReminderTime(null);
    setError(null);
  };

  const handleSubmit = async () => {
    if (!title.trim()) {
      setError('Başlık gereklidir');
      return;
    }

    if (!reminderTime) {
      setError('Hatırlatma zamanı gereklidir');
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const reminderData: CreateReminderRequest = {
        title: title.trim(),
        description: description.trim(),
        reminder_time: reminderTime.toISOString()
      };

      const response = await apiService.createReminder(reminderData);

      if (response.success && response.data) {
        onSuccess(response.data);
        onClose();
        resetForm();
      } else {
        setError(response.error || 'Hatırlatma kaydedilemedi');
      }
    } catch (error) {
      setError('Bir hata oluştu');
      console.error('Reminder save error:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleClose = () => {
    resetForm();
    onClose();
  };

  return (
    <Dialog open={open} onClose={handleClose} maxWidth="sm" fullWidth>
      <DialogTitle>
        Yeni Hatırlatma Oluştur
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
            placeholder="Hatırlatma açıklaması (opsiyonel)"
          />

          <TextField
            margin="dense"
            label="Hatırlatma Zamanı"
            type="datetime-local"
            fullWidth
            variant="outlined"
            value={reminderTime ? reminderTime.toISOString().slice(0, 16) : ''}
            onChange={(e) => setReminderTime(e.target.value ? new Date(e.target.value) : null)}
            InputLabelProps={{ shrink: true }}
            error={!!error && !reminderTime}
            helperText={error && !reminderTime ? 'Hatırlatma zamanı gereklidir' : ''}
          />

          {error && (
            <Box sx={{ color: 'error.main', mt: 1, fontSize: '0.875rem' }}>
              {error}
            </Box>
          )}
        </Box>
      </DialogContent>
      <DialogActions>
        <Button onClick={handleClose}>İptal</Button>
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

export default CreateReminderModal;

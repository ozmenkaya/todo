import React, { useState, useEffect } from 'react';
import {
  Container,
  Typography,
  Box,
  Card,
  Fab,
  CircularProgress,
  Alert,
  Button,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  ListItemSecondaryAction,
  Avatar,
  Divider,
} from '@mui/material';
import { 
  Add, 
  Description,
  Share 
} from '@mui/icons-material';
import { useNavigate } from 'react-router-dom';
import type { Report } from '../types';
import { apiService } from '../services/api';
import CreateReportModal from '../components/CreateReportModal';

const ReportsPage: React.FC = () => {
  const [reports, setReports] = useState<Report[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [createModalOpen, setCreateModalOpen] = useState(false);
  
  const navigate = useNavigate();

  useEffect(() => {
    loadReports();
  }, []);

  const loadReports = async () => {
    try {
      setLoading(true);
      setError(null);
      const response = await apiService.getReports();
      if (response.success) {
        setReports(response.data || []);
      } else {
        setError(response.error || 'Raporlar yüklenemedi');
      }
    } catch (error) {
      setError('Bir hata oluştu');
      console.error('Failed to load reports:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleReportCreated = (newReport: Report) => {
    setReports([newReport, ...reports]);
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
            Raporlar
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
            {reports.map((report, index) => (
              <React.Fragment key={report.id}>
                <ListItem sx={{ py: 2 }}>
                  <ListItemIcon>
                    <Avatar sx={{ backgroundColor: '#2196f3', width: 48, height: 48 }}>
                      <Description />
                    </Avatar>
                  </ListItemIcon>
                  
                  <ListItemText
                    primary={
                      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                        <Typography variant="subtitle1" component="span" sx={{ fontWeight: 500 }}>
                          {report.title}
                        </Typography>
                        {report.shared_with && report.shared_with.length > 0 && (
                          <Share sx={{ fontSize: 16, color: 'text.secondary' }} />
                        )}
                      </Box>
                    }
                    secondary={
                      <Box sx={{ mt: 1 }}>
                        <Typography variant="body2" color="text.secondary" sx={{ mb: 0.5 }}>
                          {report.content.length > 100 
                            ? `${report.content.substring(0, 100)}...` 
                            : report.content
                          }
                        </Typography>
                        <Typography variant="caption" color="text.secondary" sx={{ fontStyle: 'italic' }}>
                          Oluşturan: {report.creator?.first_name} {report.creator?.last_name} • 
                          {new Date(report.created_at).toLocaleDateString('tr-TR')}
                        </Typography>
                      </Box>
                    }
                  />
                  
                  <ListItemSecondaryAction>
                    <Button 
                      size="small" 
                      variant="outlined"
                      onClick={() => navigate(`/reports/${report.id}`)}
                      sx={{ 
                        minWidth: 'auto',
                        px: 2
                      }}
                    >
                      Detaylar
                    </Button>
                  </ListItemSecondaryAction>
                </ListItem>
                {index < reports.length - 1 && <Divider />}
              </React.Fragment>
            ))}
          </List>
        </Card>

        {reports.length === 0 && !loading && (
          <Box sx={{ textAlign: 'center', mt: 6, py: 4 }}>
            <Description sx={{ fontSize: 64, color: 'text.secondary', mb: 2 }} />
            <Typography variant="h6" color="text.secondary" sx={{ mb: 1 }}>
              Henüz rapor bulunmuyor
            </Typography>
            <Typography variant="body2" color="text.secondary">
              Yeni rapor oluşturmak için + butonuna tıklayın
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

        <CreateReportModal
          open={createModalOpen}
          onClose={() => setCreateModalOpen(false)}
          onSuccess={handleReportCreated}
        />
      </Box>
    </Container>
  );
};

export default ReportsPage;

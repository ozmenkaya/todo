import React from 'react';
import { Container, Typography, Box } from '@mui/material';
import { useParams } from 'react-router-dom';

const ReportDetailPage: React.FC = () => {
  const { id } = useParams<{ id: string }>();

  return (
    <Container maxWidth="lg">
      <Box sx={{ mt: 2 }}>
        <Typography variant="h4" gutterBottom>
          Rapor Detayı #{id}
        </Typography>
        <Typography variant="body1">
          Rapor detayı sayfası yapım aşamasında...
        </Typography>
      </Box>
    </Container>
  );
};

export default ReportDetailPage;

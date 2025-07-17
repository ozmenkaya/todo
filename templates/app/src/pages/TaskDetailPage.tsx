import React from 'react';
import { Container, Typography, Box } from '@mui/material';
import { useParams } from 'react-router-dom';

const TaskDetailPage: React.FC = () => {
  const { id } = useParams<{ id: string }>();

  return (
    <Container maxWidth="lg">
      <Box sx={{ mt: 2 }}>
        <Typography variant="h4" gutterBottom>
          Görev Detayı #{id}
        </Typography>
        <Typography variant="body1">
          Görev detayı sayfası yapım aşamasında...
        </Typography>
      </Box>
    </Container>
  );
};

export default TaskDetailPage;

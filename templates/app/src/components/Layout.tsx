import React, { useState } from 'react';
import {
  Box,
  Badge,
  Avatar,
  Menu,
  MenuItem,
  ListItemIcon,
  ListItemText,
  BottomNavigation,
  BottomNavigationAction,
  useTheme,
  useMediaQuery,
  Fab,
} from '@mui/material';
import {
  Dashboard,
  Assignment,
  Description,
  Schedule,
  AccountCircle,
  Logout,
} from '@mui/icons-material';
import { useNavigate, useLocation } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';

interface LayoutProps {
  children: React.ReactNode;
}

const Layout: React.FC<LayoutProps> = ({ children }) => {
  const [anchorEl, setAnchorEl] = useState<null | HTMLElement>(null);
  const navigate = useNavigate();
  const location = useLocation();
  const { state: authState, logout } = useAuth();
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('md'));

  const navigationItems = [
    { text: 'Dashboard', icon: <Dashboard />, path: '/' },
    { text: 'Görevler', icon: <Assignment />, path: '/tasks' },
    { text: 'Raporlar', icon: <Description />, path: '/reports' },
    { text: 'Hatırlatmalar', icon: <Schedule />, path: '/reminders' },
  ];

  const handleNavigationClick = (path: string) => {
    navigate(path);
  };

  const handleProfileMenuOpen = (event: React.MouseEvent<HTMLElement>) => {
    setAnchorEl(event.currentTarget);
  };

  const handleProfileMenuClose = () => {
    setAnchorEl(null);
  };

  const handleLogout = async () => {
    await logout();
    handleProfileMenuClose();
    navigate('/login');
  };

  const getCurrentPageIndex = () => {
    const currentIndex = navigationItems.findIndex(item => item.path === location.pathname);
    return currentIndex >= 0 ? currentIndex : 0;
  };

  return (
    <Box sx={{ display: 'flex', flexDirection: 'column', minHeight: '100vh', backgroundColor: '#f5f5f5' }}>
      {/* Profile Menu FAB - Top Right */}
      <Fab
        size="medium"
        sx={{
          position: 'fixed',
          top: 16,
          right: 16,
          zIndex: 1000,
          backgroundColor: 'white',
          '&:hover': {
            backgroundColor: '#f0f0f0',
          }
        }}
        onClick={handleProfileMenuOpen}
      >
        <Avatar sx={{ width: 32, height: 32 }}>
          {authState.user?.first_name?.charAt(0) || 
           authState.user?.username?.charAt(0) || 'U'}
        </Avatar>
      </Fab>

      <Menu
        id="menu-appbar"
        anchorEl={anchorEl}
        anchorOrigin={{
          vertical: 'top',
          horizontal: 'right',
        }}
        keepMounted
        transformOrigin={{
          vertical: 'top',
          horizontal: 'right',
        }}
        open={Boolean(anchorEl)}
        onClose={handleProfileMenuClose}
      >
        <MenuItem onClick={handleProfileMenuClose}>
          <ListItemIcon>
            <AccountCircle fontSize="small" />
          </ListItemIcon>
          <ListItemText>
            {authState.user?.first_name} {authState.user?.last_name}
          </ListItemText>
        </MenuItem>
        <MenuItem onClick={handleLogout}>
          <ListItemIcon>
            <Logout fontSize="small" />
          </ListItemIcon>
          <ListItemText>Çıkış Yap</ListItemText>
        </MenuItem>
      </Menu>

      {/* Main Content */}
      <Box
        component="main"
        sx={{
          flexGrow: 1,
          px: { xs: 2, sm: 3, md: 4 },
          py: { xs: 2, sm: 3 },
          pt: { xs: 4, sm: 5 }, // Top padding for profile menu
          mb: isMobile ? 7 : 0, // Bottom margin for mobile navigation
        }}
      >
        {children}
      </Box>

      {/* Mobile Bottom Navigation */}
      {isMobile && (
        <BottomNavigation
          value={getCurrentPageIndex()}
          onChange={(_event, newValue) => {
            handleNavigationClick(navigationItems[newValue].path);
          }}
          sx={{
            position: 'fixed',
            bottom: 0,
            left: 0,
            right: 0,
            zIndex: (theme) => theme.zIndex.drawer + 1,
            borderTop: 1,
            borderColor: 'divider',
            backgroundColor: 'white',
          }}
        >
          {navigationItems.map((item) => (
            <BottomNavigationAction
              key={item.text}
              label={item.text}
              icon={
                <Badge
                  badgeContent={
                    item.path === '/tasks' ? 0 :
                    item.path === '/reminders' ? 0 :
                    item.path === '/reports' ? 0 : undefined
                  }
                  color="error"
                >
                  {item.icon}
                </Badge>
              }
            />
          ))}
        </BottomNavigation>
      )}
    </Box>
  );
};

export default Layout;

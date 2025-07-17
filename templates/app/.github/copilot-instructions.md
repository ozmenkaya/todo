# Copilot Instructions

<!-- Use this file to provide workspace-specific custom instructions to Copilot. For more details, visit https://code.visualstudio.com/docs/copilot/copilot-customization#_use-a-githubcopilotinstructionsmd-file -->

## Project Overview
This is a Progressive Web App (PWA) mobile application for a company task management system built with:
- **Frontend**: React + TypeScript + Vite
- **Backend**: Existing Flask API (http://localhost:5004)
- **Styling**: Modern mobile-first responsive design
- **PWA Features**: Service worker, offline capabilities, push notifications
- **Mobile UI**: Touch-friendly interface optimized for iOS and Android

## Technical Stack
- React 18 with TypeScript
- Vite for build tooling
- PWA capabilities with Workbox
- Material-UI or Ionic for mobile components
- Axios for API communication
- React Router for navigation
- Service Worker for offline functionality

## Key Features to Implement
1. **Authentication**: Login/logout with Flask backend
2. **Task Management**: View, create, update, complete tasks
3. **Reports**: View and create company reports
4. **Notifications**: Real-time updates and push notifications
5. **Offline Mode**: Sync when connection is restored
6. **Responsive Design**: Optimized for mobile devices
7. **PWA Installation**: Add to home screen functionality

## API Integration
- Base URL: http://localhost:5004
- Authentication: Session-based with Flask
- CORS handling for cross-origin requests
- Error handling and loading states

## Code Style Guidelines
- Use functional components with hooks
- TypeScript interfaces for all data types
- Mobile-first responsive design
- Modern ES6+ syntax
- Clean component structure with separation of concerns

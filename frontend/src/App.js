import React, { useState, useEffect } from 'react';
import {
  Box,
  Container,
  AppBar,
  Toolbar,
  Typography,
  CssBaseline,
  ThemeProvider,
  createTheme,
  Alert,
  Snackbar,
  Tab,
  Tabs,
  Paper,
  Badge,
  Avatar,
} from '@mui/material';
import { Search, CloudUpload, Analytics, Business, SmartToy } from '@mui/icons-material';

import SearchBar from './components/SearchBar';
import SearchResults from './components/SearchResults';
import Statistics from './components/Statistics';
import FileUpload from './components/FileUpload';
import apiService from './services/api';

// Create enterprise theme
const theme = createTheme({
  palette: {
    mode: 'light',
    primary: {
      main: '#1565c0', // Professional blue
      dark: '#0d47a1',
      light: '#5e92f3',
    },
    secondary: {
      main: '#f57c00', // Professional orange
      dark: '#e65100',
      light: '#ffb74d',
    },
    background: {
      default: '#f8fafc',
      paper: '#ffffff',
    },
    text: {
      primary: '#1e293b',
      secondary: '#64748b',
    },
  },
  typography: {
    fontFamily: '"Inter", "Roboto", "Helvetica", "Arial", sans-serif',
    h1: { fontWeight: 700 },
    h2: { fontWeight: 600 },
    h3: { fontWeight: 600 },
    h4: { fontWeight: 600 },
    h5: { fontWeight: 600 },
    h6: { fontWeight: 600 },
    button: { textTransform: 'none', fontWeight: 500 },
  },
  shape: {
    borderRadius: 12,
  },
  shadows: [
    'none',
    '0px 1px 3px rgba(0, 0, 0, 0.05)',
    '0px 4px 6px rgba(0, 0, 0, 0.05)',
    '0px 10px 15px rgba(0, 0, 0, 0.1)',
    '0px 20px 25px rgba(0, 0, 0, 0.1)',
    '0px 25px 50px rgba(0, 0, 0, 0.25)',
    ...Array(19).fill('0px 25px 50px rgba(0, 0, 0, 0.25)'),
  ],
  components: {
    MuiCard: {
      styleOverrides: {
        root: {
          boxShadow: '0px 1px 3px rgba(0, 0, 0, 0.05)',
          '&:hover': {
            boxShadow: '0px 4px 6px rgba(0, 0, 0, 0.1)',
          },
        },
      },
    },
    MuiButton: {
      styleOverrides: {
        root: {
          borderRadius: 8,
          textTransform: 'none',
          fontWeight: 500,
        },
      },
    },
  },
});

function App() {
  const [searchResults, setSearchResults] = useState([]);
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true); // Start with loading true
  const [searchLoading, setSearchLoading] = useState(false);
  const [uploadLoading, setUploadLoading] = useState(false);
  const [snackbar, setSnackbar] = useState({ open: false, message: '', severity: 'info' });
  const [activeTab, setActiveTab] = useState('search');
  const [filterRefreshTrigger, setFilterRefreshTrigger] = useState(0);

  // Load statistics on component mount with delay to allow backend initialization
  useEffect(() => {
    // Wait 3 seconds for backend to initialize, then load stats
    const timer = setTimeout(() => {
      loadStats();
    }, 3000);
    
    return () => clearTimeout(timer);
  }, []); // eslint-disable-line react-hooks/exhaustive-deps

  const loadStats = async (retryCount = 0) => {
    setLoading(true);
    try {
      const statsData = await apiService.getStats();
      setStats(statsData);
    } catch (error) {
      // If it's a 503 error (service not ready) and we haven't retried too many times
      if (error.response?.status === 503 && retryCount < 3) {
        console.log(`Backend not ready, retrying in ${(retryCount + 1) * 2} seconds...`);
        setTimeout(() => loadStats(retryCount + 1), (retryCount + 1) * 2000);
        return;
      }
      showSnackbar('Failed to load statistics', 'error');
    } finally {
      setLoading(false);
    }
  };

  const handleSearch = async (searchParams) => {
    setSearchLoading(true);
    try {
      const response = await apiService.searchMeetings(searchParams);
      setSearchResults(response.results || []);
      showSnackbar(`Found ${response.total_results} results`, 'success');
    } catch (error) {
      showSnackbar('Search failed: ' + (error.message || 'Unknown error'), 'error');
      setSearchResults([]);
    } finally {
      setSearchLoading(false);
    }
  };

  const handleFileUpload = async (file) => {
    try {
      const result = await apiService.uploadFile(file);
      if (result.success) {
        showSnackbar(`File "${result.filename}" uploaded successfully`, 'success');
        // Reload stats after successful upload
        loadStats();
        // Refresh filter options to include new participants
        setFilterRefreshTrigger(prev => prev + 1);
      } else {
        throw new Error(result.message || 'Upload failed');
      }
      return result;
    } catch (error) {
      throw new Error(error.message || 'Upload failed');
    }
  };

  const showSnackbar = (message, severity = 'info') => {
    setSnackbar({ open: true, message, severity });
  };

  const handleCloseSnackbar = () => {
    setSnackbar({ ...snackbar, open: false });
  };

  const renderContent = () => {
    switch (activeTab) {
      case 'search':
        return (
          <Box>
            <SearchBar 
              onSearch={handleSearch} 
              loading={searchLoading} 
              refreshTrigger={filterRefreshTrigger}
            />
            <SearchResults 
              results={searchResults} 
              loading={searchLoading} 
              query={searchResults.length > 0 ? 'search query' : ''} 
            />
          </Box>
        );
      case 'upload':
        return (
          <FileUpload onUpload={handleFileUpload} loading={uploadLoading} />
        );
      case 'stats':
        return (
          <Statistics stats={stats} loading={loading} />
        );
      default:
        return null;
    }
  };

  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <Box sx={{ flexGrow: 1, minHeight: '100vh', bgcolor: 'background.default' }}>
        
        {/* Enterprise Header */}
        <AppBar 
          position="static" 
          elevation={0}
          sx={{ 
            bgcolor: 'background.paper',
            color: 'text.primary',
            borderBottom: 1,
            borderColor: 'divider'
          }}
        >
          <Toolbar sx={{ justifyContent: 'space-between' }}>
            <Box sx={{ display: 'flex', alignItems: 'center' }}>
              <Avatar sx={{ bgcolor: 'primary.main', mr: 2 }}>
                <SmartToy />
              </Avatar>
              <Box>
                <Typography variant="h6" component="div" sx={{ fontWeight: 600 }}>
                  Polyglot Meeting Assistant
                </Typography>
                <Typography variant="caption" color="text.secondary">
                  Enterprise AI-Powered Meeting Intelligence
                </Typography>
              </Box>
            </Box>
            
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
              <Badge 
                badgeContent={stats?.total_meetings || 0} 
                color="primary"
                sx={{ '& .MuiBadge-badge': { fontSize: '0.75rem' } }}
              >
                <Business color="action" />
              </Badge>
              <Typography variant="body2" color="text.secondary">
                {stats?.total_meetings || 0} Meetings
              </Typography>
            </Box>
          </Toolbar>
        </AppBar>

        {/* Loading state */}
        <Container maxWidth="xl" sx={{ py: 4 }}>
          {loading && (
            <Alert 
              severity="info" 
              sx={{ 
                mb: 3, 
                borderRadius: 2,
                '& .MuiAlert-icon': { fontSize: '1.5rem' }
              }}
            >
              🚀 Initializing AI models... This may take a moment for the best experience.
            </Alert>
          )}

          {/* Professional Tab Navigation */}
          <Paper 
            elevation={0} 
            sx={{ 
              mb: 4, 
              borderRadius: 3,
              border: 1,
              borderColor: 'divider',
              overflow: 'hidden'
            }}
          >
            <Tabs
              value={activeTab}
              onChange={(e, newValue) => setActiveTab(newValue)}
              variant="fullWidth"
              sx={{
                '& .MuiTabs-indicator': {
                  height: 3,
                  borderRadius: '3px 3px 0 0',
                },
                '& .MuiTab-root': {
                  textTransform: 'none',
                  fontWeight: 500,
                  fontSize: '1rem',
                  minHeight: 64,
                  '&.Mui-selected': {
                    fontWeight: 600,
                  },
                },
              }}
            >
              <Tab 
                value="search" 
                label="Search & Discovery" 
                icon={<Search />}
                iconPosition="start"
              />
              <Tab 
                value="upload" 
                label="Upload & Process" 
                icon={<CloudUpload />}
                iconPosition="start"
              />
              <Tab 
                value="stats" 
                label="Analytics & Insights" 
                icon={<Analytics />}
                iconPosition="start"
              />
            </Tabs>
          </Paper>

          {/* Page Content */}
          {renderContent()}
        </Container>
      </Box>

      {/* Snackbar for notifications */}
      <Snackbar
        open={snackbar.open}
        autoHideDuration={6000}
        onClose={handleCloseSnackbar}
        anchorOrigin={{ vertical: 'bottom', horizontal: 'right' }}
      >
        <Alert 
          onClose={handleCloseSnackbar} 
          severity={snackbar.severity}
          sx={{ width: '100%' }}
        >
          {snackbar.message}
        </Alert>
      </Snackbar>
    </ThemeProvider>
  );
}

export default App;

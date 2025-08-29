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
} from '@mui/material';
import { Search, CloudUpload, Analytics } from '@mui/icons-material';

import SearchBar from './components/SearchBar';
import SearchResults from './components/SearchResults';
import Statistics from './components/Statistics';
import FileUpload from './components/FileUpload';
import apiService from './services/api';

// Create theme
const theme = createTheme({
  palette: {
    primary: {
      main: '#1976d2',
    },
    secondary: {
      main: '#dc004e',
    },
  },
  typography: {
    fontFamily: '"Roboto", "Helvetica", "Arial", sans-serif',
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
            <SearchBar onSearch={handleSearch} loading={searchLoading} />
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
      
      {/* App Bar */}
      <AppBar position="static" elevation={2}>
        <Toolbar>
          <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
            🔍 Polyglot Meeting Assistant
          </Typography>
          <Typography variant="body2" sx={{ opacity: 0.8 }}>
            AI-powered semantic search
          </Typography>
        </Toolbar>
      </AppBar>

      {/* Main Content */}
      <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
        {/* Navigation Tabs */}
        <Box sx={{ mb: 4, display: 'flex', gap: 1 }}>
          <Box
            sx={{
              display: 'flex',
              alignItems: 'center',
              gap: 1,
              px: 3,
              py: 1.5,
              borderRadius: 2,
              cursor: 'pointer',
              backgroundColor: activeTab === 'search' ? 'primary.main' : 'transparent',
              color: activeTab === 'search' ? 'white' : 'text.primary',
              '&:hover': {
                backgroundColor: activeTab === 'search' ? 'primary.dark' : 'grey.100',
              },
            }}
            onClick={() => setActiveTab('search')}
          >
            <Search />
            <Typography variant="body1">Search</Typography>
          </Box>
          
          <Box
            sx={{
              display: 'flex',
              alignItems: 'center',
              gap: 1,
              px: 3,
              py: 1.5,
              borderRadius: 2,
              cursor: 'pointer',
              backgroundColor: activeTab === 'upload' ? 'primary.main' : 'transparent',
              color: activeTab === 'upload' ? 'white' : 'text.primary',
              '&:hover': {
                backgroundColor: activeTab === 'upload' ? 'primary.dark' : 'grey.100',
              },
            }}
            onClick={() => setActiveTab('upload')}
          >
            <CloudUpload />
            <Typography variant="body1">Upload</Typography>
          </Box>
          
          <Box
            sx={{
              display: 'flex',
              alignItems: 'center',
              gap: 1,
              px: 3,
              py: 1.5,
              borderRadius: 2,
              cursor: 'pointer',
              backgroundColor: activeTab === 'stats' ? 'primary.main' : 'transparent',
              color: activeTab === 'stats' ? 'white' : 'text.primary',
              '&:hover': {
                backgroundColor: activeTab === 'stats' ? 'primary.dark' : 'grey.100',
              },
            }}
            onClick={() => setActiveTab('stats')}
          >
            <Analytics />
            <Typography variant="body1">Statistics</Typography>
          </Box>
        </Box>

        {/* Page Content */}
        {renderContent()}
      </Container>

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

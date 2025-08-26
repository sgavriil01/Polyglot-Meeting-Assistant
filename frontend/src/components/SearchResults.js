import React from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Chip,
  Divider,
  Paper,
  Grid,
  IconButton,
  Tooltip,
  Skeleton,
} from '@mui/material';
import {
  Description,
  Event,
  Person,
  TrendingUp,
  ContentCopy,
  OpenInNew,
} from '@mui/icons-material';

const SearchResults = ({ results, loading = false, query = '' }) => {
  if (loading) {
    return (
      <Box>
        {[...Array(3)].map((_, index) => (
          <Card key={index} sx={{ mb: 2 }}>
            <CardContent>
              <Skeleton variant="text" width="60%" height={32} />
              <Skeleton variant="text" width="40%" height={24} />
              <Skeleton variant="text" width="100%" height={20} />
              <Skeleton variant="text" width="80%" height={20} />
            </CardContent>
          </Card>
        ))}
      </Box>
    );
  }

  if (!results || results.length === 0) {
    return (
      <Paper elevation={1} sx={{ p: 4, textAlign: 'center' }}>
        <Typography variant="h6" color="text.secondary" gutterBottom>
          No results found
        </Typography>
        <Typography variant="body2" color="text.secondary">
          {query ? `No results found for "${query}". Try a different search term.` : 'Enter a search query to get started.'}
        </Typography>
      </Paper>
    );
  }

  const getContentTypeIcon = (contentType) => {
    switch (contentType) {
      case 'transcript':
        return <Description color="primary" />;
      case 'summary':
        return <TrendingUp color="success" />;
      case 'action_item':
        return <Event color="warning" />;
      case 'decision':
        return <Person color="info" />;
      case 'timeline':
        return <Event color="secondary" />;
      default:
        return <Description color="action" />;
    }
  };

  const getContentTypeColor = (contentType) => {
    switch (contentType) {
      case 'transcript':
        return 'primary';
      case 'summary':
        return 'success';
      case 'action_item':
        return 'warning';
      case 'decision':
        return 'info';
      case 'timeline':
        return 'secondary';
      default:
        return 'default';
    }
  };

  const formatDate = (dateString) => {
    try {
      return new Date(dateString).toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
      });
    } catch {
      return dateString;
    }
  };

  const copyToClipboard = (text) => {
    navigator.clipboard.writeText(text);
  };

  return (
    <Box>
      <Box sx={{ mb: 3, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <Typography variant="h6" component="h2">
          Search Results
        </Typography>
        <Typography variant="body2" color="text.secondary">
          {results.length} result{results.length !== 1 ? 's' : ''} found
        </Typography>
      </Box>

      <Grid container spacing={2}>
        {results.map((result, index) => (
          <Grid item xs={12} key={index}>
            <Card elevation={2} sx={{ '&:hover': { elevation: 4 } }}>
              <CardContent>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', mb: 2 }}>
                  <Box sx={{ flex: 1 }}>
                    <Typography variant="h6" component="h3" gutterBottom>
                      {result.meeting_title}
                    </Typography>
                    
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
                      {getContentTypeIcon(result.content_type)}
                      <Chip
                        label={result.content_type.replace('_', ' ').toUpperCase()}
                        size="small"
                        color={getContentTypeColor(result.content_type)}
                        variant="outlined"
                      />
                    </Box>
                  </Box>
                  
                  <Box sx={{ display: 'flex', gap: 1 }}>
                    <Tooltip title="Copy snippet">
                      <IconButton
                        size="small"
                        onClick={() => copyToClipboard(result.snippet)}
                      >
                        <ContentCopy fontSize="small" />
                      </IconButton>
                    </Tooltip>
                  </Box>
                </Box>

                <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
                  <Typography variant="body2" color="text.secondary">
                    📅 {formatDate(result.meeting_date)}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    🎯 {(result.relevance_score * 100).toFixed(1)}% relevant
                  </Typography>
                </Box>

                <Divider sx={{ my: 1 }} />

                <Box
                  sx={{
                    background: 'grey.50',
                    borderLeft: 3,
                    borderColor: 'primary.main',
                    p: 2,
                    borderRadius: 1,
                  }}
                >
                  <Typography variant="body2" sx={{ lineHeight: 1.6 }}>
                    {result.snippet}
                  </Typography>
                </Box>

                {result.participants && result.participants.length > 0 && (
                  <Box sx={{ mt: 2 }}>
                    <Typography variant="caption" color="text.secondary">
                      Participants: {result.participants.join(', ')}
                    </Typography>
                  </Box>
                )}
              </CardContent>
            </Card>
          </Grid>
        ))}
      </Grid>
    </Box>
  );
};

export default SearchResults;



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
  Button,
  ButtonGroup,
} from '@mui/material';
import {
  Description,
  Event,
  Person,
  TrendingUp,
  ContentCopy,
  OpenInNew,
  FileDownload,
  PictureAsPdf,
  TableChart,
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

  // Export functions
  const exportToPDF = () => {
    // Create PDF content
    const content = `
SEARCH RESULTS REPORT
Query: "${query}"
Generated: ${new Date().toLocaleString()}
Total Results: ${results.length}

${results.map((result, index) => `
${index + 1}. ${result.meeting_title}
Date: ${formatDate(result.meeting_date)}
Type: ${result.content_type.replace('_', ' ').toUpperCase()}
Relevance: ${(result.relevance_score * 100).toFixed(1)}%
${result.participants?.length ? `Participants: ${result.participants.join(', ')}` : ''}

Content:
${result.snippet}

${'='.repeat(80)}
`).join('')}
    `;

    // Create and download PDF
    const blob = new Blob([content], { type: 'text/plain' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `search-results-${query.replace(/[^a-z0-9]/gi, '-')}-${new Date().toISOString().split('T')[0]}.txt`;
    document.body.appendChild(a);
    a.click();
    window.URL.revokeObjectURL(url);
    document.body.removeChild(a);
  };

  const exportToCSV = () => {
    const headers = ['Meeting Title', 'Date', 'Content Type', 'Relevance Score', 'Participants', 'Snippet'];
    const csvContent = [
      headers.join(','),
      ...results.map(result => [
        `"${result.meeting_title.replace(/"/g, '""')}"`,
        `"${formatDate(result.meeting_date)}"`,
        `"${result.content_type.replace('_', ' ')}"`,
        `"${(result.relevance_score * 100).toFixed(1)}%"`,
        `"${result.participants?.join('; ') || ''}"`,
        `"${result.snippet.replace(/"/g, '""').substring(0, 200)}..."`
      ].join(','))
    ].join('\n');

    const blob = new Blob([csvContent], { type: 'text/csv' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `search-results-${query.replace(/[^a-z0-9]/gi, '-')}-${new Date().toISOString().split('T')[0]}.csv`;
    document.body.appendChild(a);
    a.click();
    window.URL.revokeObjectURL(url);
    document.body.removeChild(a);
  };

  const copyAllToClipboard = () => {
    const content = results.map((result, index) => 
      `${index + 1}. ${result.meeting_title}\n` +
      `Date: ${formatDate(result.meeting_date)}\n` +
      `Type: ${result.content_type.replace('_', ' ')}\n` +
      `Relevance: ${(result.relevance_score * 100).toFixed(1)}%\n` +
      `Content: ${result.snippet}\n\n`
    ).join('');
    
    navigator.clipboard.writeText(content);
  };

  return (
    <Box>
      <Box sx={{ mb: 3, display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: 2 }}>
        <Box>
          <Typography variant="h6" component="h2">
            Search Results
          </Typography>
          <Typography variant="body2" color="text.secondary">
            {results.length} result{results.length !== 1 ? 's' : ''} found
          </Typography>
        </Box>
        
        {results.length > 0 && (
          <ButtonGroup variant="outlined" size="small">
            <Tooltip title="Download as CSV">
              <Button
                startIcon={<TableChart />}
                onClick={exportToCSV}
                sx={{ minWidth: 'auto' }}
              >
                CSV
              </Button>
            </Tooltip>
            <Tooltip title="Download as Text Report">
              <Button
                startIcon={<PictureAsPdf />}
                onClick={exportToPDF}
                sx={{ minWidth: 'auto' }}
              >
                Report
              </Button>
            </Tooltip>
            <Tooltip title="Copy all to clipboard">
              <Button
                startIcon={<ContentCopy />}
                onClick={copyAllToClipboard}
                sx={{ minWidth: 'auto' }}
              >
                Copy
              </Button>
            </Tooltip>
          </ButtonGroup>
        )}
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



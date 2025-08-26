import React from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Grid,
  Chip,
  Paper,
  Skeleton,
  Tooltip,
} from '@mui/material';
import {
  Storage,
  Description,
  Group,
  TrendingUp,
  DataUsage,
} from '@mui/icons-material';

const Statistics = ({ stats, loading = false }) => {
  if (loading) {
    return (
      <Box>
        <Typography variant="h5" component="h2" gutterBottom>
          📊 Search Index Statistics
        </Typography>
        <Paper elevation={1} sx={{ p: 3, textAlign: 'center' }}>
          <Typography variant="h6" color="text.secondary" gutterBottom>
            🚀 Starting up...
          </Typography>
          <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
            Initializing AI models and search engine. This may take a few seconds.
          </Typography>
          <Grid container spacing={2}>
            {[...Array(4)].map((_, index) => (
              <Grid item xs={12} sm={6} md={3} key={index}>
                <Card>
                  <CardContent>
                    <Skeleton variant="text" width="60%" height={24} />
                    <Skeleton variant="text" width="40%" height={32} />
                  </CardContent>
                </Card>
              </Grid>
            ))}
          </Grid>
        </Paper>
      </Box>
    );
  }

  if (!stats) {
    return (
      <Paper elevation={1} sx={{ p: 3, textAlign: 'center' }}>
        <Typography variant="h6" color="text.secondary">
          No statistics available
        </Typography>
      </Paper>
    );
  }

  const statCards = [
    {
      title: 'Total Meetings',
      value: stats.total_meetings || 0,
      icon: <Group color="primary" />,
      color: 'primary.main',
      tooltip: 'Number of meetings indexed',
    },
    {
      title: 'Total Documents',
      value: stats.total_documents || 0,
      icon: <Description color="success" />,
      color: 'success.main',
      tooltip: 'Number of document chunks indexed',
    },
    {
      title: 'Index Size',
      value: `${(stats.index_size_mb || 0).toFixed(2)} MB`,
      icon: <Storage color="warning" />,
      color: 'warning.main',
      tooltip: 'Size of the search index',
    },
    {
      title: 'Embedding Dimensions',
      value: stats.embedding_dimension || 0,
      icon: <DataUsage color="info" />,
      color: 'info.main',
      tooltip: 'Vector embedding dimensions',
    },
  ];

  const getContentTypeColor = (type) => {
    const colors = {
      transcript: 'primary',
      summary: 'success',
      action_item: 'warning',
      decision: 'info',
      timeline: 'secondary',
    };
    return colors[type] || 'default';
  };

  return (
    <Box>
      <Typography variant="h5" component="h2" gutterBottom>
        📊 Search Index Statistics
      </Typography>

      {/* Main Statistics Cards */}
      <Grid container spacing={2} sx={{ mb: 3 }}>
        {statCards.map((card, index) => (
          <Grid item xs={12} sm={6} md={3} key={index}>
            <Tooltip title={card.tooltip}>
              <Card elevation={2} sx={{ height: '100%' }}>
                <CardContent>
                  <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                    {card.icon}
                    <Typography variant="body2" color="text.secondary" sx={{ ml: 1 }}>
                      {card.title}
                    </Typography>
                  </Box>
                  <Typography
                    variant="h4"
                    component="div"
                    sx={{ color: card.color, fontWeight: 'bold' }}
                  >
                    {card.value}
                  </Typography>
                </CardContent>
              </Card>
            </Tooltip>
          </Grid>
        ))}
      </Grid>

      {/* Content Distribution */}
      {stats.content_type_distribution && (
        <Card elevation={2}>
          <CardContent>
            <Typography variant="h6" component="h3" gutterBottom>
              Content Distribution
            </Typography>
            <Grid container spacing={1}>
              {Object.entries(stats.content_type_distribution).map(([type, count]) => (
                <Grid item key={type}>
                  <Chip
                    label={`${type.replace('_', ' ').toUpperCase()}: ${count}`}
                    color={getContentTypeColor(type)}
                    variant="outlined"
                    size="small"
                  />
                </Grid>
              ))}
            </Grid>
          </CardContent>
        </Card>
      )}

      {/* Model Information */}
      {stats.model_name && (
        <Card elevation={2} sx={{ mt: 2 }}>
          <CardContent>
            <Typography variant="h6" component="h3" gutterBottom>
              AI Model Information
            </Typography>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
              <TrendingUp color="primary" />
              <Typography variant="body2">
                Model: <strong>{stats.model_name}</strong>
              </Typography>
            </Box>
          </CardContent>
        </Card>
      )}
    </Box>
  );
};

export default Statistics;



import React, { useState, useEffect } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Grid,
  Chip,
  CircularProgress,
  Paper,
  Divider,
  LinearProgress,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  Avatar,
  Skeleton,
  Alert,
} from '@mui/material';
import {
  Storage,
  Description,
  Memory,
  Search,
  SmartToy,
  TrendingUp,
  People,
  Schedule,
  Assignment,
  Language,
  Timeline,
  Insights,
  BarChart as BarChartIcon,
  PieChart as PieChartIcon,
  Group,
  AccessTime,
} from '@mui/icons-material';
import {
  LineChart,
  Line,
  AreaChart,
  Area,
  BarChart,
  Bar,
  PieChart,
  Pie,
  Cell,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from 'recharts';
import apiService from '../services/api';

const COLORS = ['#1565c0', '#f57c00', '#388e3c', '#7b1fa2', '#d32f2f', '#0097a7', '#fbc02d', '#5d4037'];

const Statistics = ({ stats, loading = false }) => {
  const [analyticsData, setAnalyticsData] = useState(null);
  const [analyticsLoading, setAnalyticsLoading] = useState(true);
  const [analyticsError, setAnalyticsError] = useState(null);

  useEffect(() => {
    loadAnalytics();
  }, []);

  const loadAnalytics = async () => {
    try {
      setAnalyticsLoading(true);
      setAnalyticsError(null);
      const data = await apiService.getAnalytics();
      setAnalyticsData(data);
    } catch (error) {
      console.error('Failed to load analytics:', error);
      setAnalyticsError('Failed to load analytics data');
    } finally {
      setAnalyticsLoading(false);
    }
  };

  if (loading || analyticsLoading) {
    return (
      <Box>
        <Typography variant="h4" component="h1" gutterBottom sx={{ fontWeight: 600, mb: 4 }}>
          📊 Analytics & Insights
        </Typography>
        
        {/* Loading skeleton for key metrics */}
        <Grid container spacing={3} sx={{ mb: 4 }}>
          {[...Array(4)].map((_, index) => (
            <Grid item xs={12} sm={6} md={3} key={index}>
              <Card elevation={2}>
                <CardContent>
                  <Skeleton variant="text" width="60%" height={24} />
                  <Skeleton variant="text" width="40%" height={48} />
                </CardContent>
              </Card>
            </Grid>
          ))}
        </Grid>

        {/* Loading skeleton for charts */}
        <Grid container spacing={3}>
          <Grid item xs={12} md={6}>
            <Card elevation={2}>
              <CardContent>
                <Skeleton variant="text" width="40%" height={32} />
                <Skeleton variant="rectangular" width="100%" height={300} />
              </CardContent>
            </Card>
          </Grid>
          <Grid item xs={12} md={6}>
            <Card elevation={2}>
              <CardContent>
                <Skeleton variant="text" width="40%" height={32} />
                <Skeleton variant="rectangular" width="100%" height={300} />
              </CardContent>
            </Card>
          </Grid>
        </Grid>

        <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', mt: 4 }}>
          <CircularProgress size={24} sx={{ mr: 2 }} />
          <Typography variant="body2" color="text.secondary">
            Loading analytics dashboard...
          </Typography>
        </Box>
      </Box>
    );
  }

  if (analyticsError) {
    return (
      <Box>
        <Typography variant="h4" component="h1" gutterBottom sx={{ fontWeight: 600, mb: 4 }}>
          📊 Analytics & Insights
        </Typography>
        <Alert severity="error" sx={{ mb: 3 }}>
          {analyticsError}
        </Alert>
        <Paper elevation={1} sx={{ p: 4, textAlign: 'center' }}>
          <Typography variant="h6" color="text.secondary" gutterBottom>
            No analytics data available
          </Typography>
          <Typography variant="body2" color="text.secondary">
            Upload some meetings to see analytics and insights.
          </Typography>
        </Paper>
      </Box>
    );
  }

  if (!analyticsData || analyticsData.total_meetings === 0) {
    return (
      <Box>
        <Typography variant="h4" component="h1" gutterBottom sx={{ fontWeight: 600, mb: 4 }}>
          📊 Analytics & Insights
        </Typography>
        <Paper elevation={1} sx={{ p: 4, textAlign: 'center' }}>
          <Insights sx={{ fontSize: 64, color: 'text.secondary', mb: 2 }} />
          <Typography variant="h6" color="text.secondary" gutterBottom>
            No meetings to analyze yet
          </Typography>
          <Typography variant="body2" color="text.secondary">
            Upload your first meeting to start seeing analytics and insights.
          </Typography>
        </Paper>
      </Box>
    );
  }

  // Key metrics data with better styling
  const keyMetrics = [
    {
      title: 'Total Meetings',
      value: analyticsData.total_meetings,
      icon: <Group />,
      gradient: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
      color: '#667eea',
      subtitle: 'Meetings processed',
    },
    {
      title: 'Action Items',
      value: analyticsData.action_items_stats?.total_action_items || 0,
      icon: <Assignment />,
      gradient: 'linear-gradient(135deg, #f093fb 0%, #f5576c 100%)',
      color: '#f5576c',
      subtitle: `${analyticsData.action_items_stats?.avg_per_meeting?.toFixed(1) || 0} per meeting`,
    },
    {
      title: 'Participants',
      value: Object.keys(analyticsData.participant_activity || {}).length,
      icon: <People />,
      gradient: 'linear-gradient(135deg, #4facfe 0%, #00f2fe 100%)',
      color: '#4facfe',
      subtitle: 'Unique participants',
    },
    {
      title: 'Avg Duration',
      value: analyticsData.average_meeting_length ? `${analyticsData.average_meeting_length}m` : 'N/A',
      icon: <AccessTime />,
      gradient: 'linear-gradient(135deg, #43e97b 0%, #38f9d7 100%)',
      color: '#43e97b',
      subtitle: 'Per meeting',
    },
  ];

  // Prepare content distribution chart data
  const contentChartData = Object.entries(analyticsData.content_distribution || {}).map(([type, count]) => ({
    name: type.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase()),
    value: count,
    count: count,
  }));

  // Prepare participant activity chart data
  const participantChartData = Object.entries(analyticsData.participant_activity || {})
    .slice(0, 10)
    .map(([name, count]) => ({
      name: name.length > 12 ? name.substring(0, 12) + '...' : name,
      meetings: count,
      fullName: name,
    }));

  // Prepare language distribution data
  const languageChartData = Object.entries(analyticsData.language_distribution || {}).map(([lang, count]) => ({
    name: lang === 'unknown' ? 'Unknown' : lang.toUpperCase(),
    value: count,
    count: count,
  }));

  return (
    <Box>
      <Typography variant="h4" component="h1" gutterBottom sx={{ fontWeight: 600, mb: 4 }}>
        📊 Analytics & Insights
      </Typography>

      {/* Key Metrics */}
      <Grid container spacing={3} sx={{ mb: 4 }}>
        {keyMetrics.map((metric, index) => (
          <Grid item xs={12} sm={6} md={3} key={index}>
            <Card 
              elevation={0} 
              sx={{ 
                height: '100%', 
                borderRadius: 3,
                background: metric.gradient,
                color: 'white',
                position: 'relative',
                overflow: 'hidden',
                '&::before': {
                  content: '""',
                  position: 'absolute',
                  top: 0,
                  left: 0,
                  right: 0,
                  bottom: 0,
                  background: 'rgba(255, 255, 255, 0.1)',
                  backdropFilter: 'blur(10px)',
                },
                '&:hover': {
                  transform: 'translateY(-4px)',
                  transition: 'transform 0.3s ease',
                  boxShadow: '0 12px 24px rgba(0,0,0,0.15)',
                }
              }}
            >
              <CardContent sx={{ textAlign: 'center', position: 'relative', zIndex: 1, p: 3 }}>
                <Box 
                  sx={{ 
                    mb: 2, 
                    display: 'flex', 
                    justifyContent: 'center',
                    '& svg': { 
                      fontSize: 40, 
                      filter: 'drop-shadow(0 2px 4px rgba(0,0,0,0.2))' 
                    }
                  }}
                >
                  {metric.icon}
                </Box>
                <Typography 
                  variant="h2" 
                  component="div" 
                  sx={{ 
                    fontWeight: 800, 
                    mb: 1, 
                    textShadow: '0 2px 4px rgba(0,0,0,0.3)',
                    lineHeight: 1
                  }}
                >
                  {metric.value}
                </Typography>
                <Typography 
                  variant="h6" 
                  gutterBottom 
                  sx={{ 
                    fontWeight: 600, 
                    textShadow: '0 1px 2px rgba(0,0,0,0.2)' 
                  }}
                >
                  {metric.title}
                </Typography>
                <Typography 
                  variant="body2" 
                  sx={{ 
                    opacity: 0.9, 
                    textShadow: '0 1px 2px rgba(0,0,0,0.2)' 
                  }}
                >
                  {metric.subtitle}
                </Typography>
              </CardContent>
            </Card>
          </Grid>
        ))}
      </Grid>

      <Grid container spacing={3} sx={{ mb: 4 }}>
        {/* Monthly Activity Chart */}
        <Grid item xs={12} lg={8}>
          <Card 
            elevation={0} 
            sx={{ 
              height: 450, 
              borderRadius: 3,
              border: '1px solid',
              borderColor: 'divider',
              background: 'linear-gradient(145deg, #ffffff 0%, #f8fafc 100%)',
              boxShadow: '0 4px 12px rgba(0,0,0,0.05)',
            }}
          >
            <CardContent sx={{ p: 3, height: '100%' }}>
              <Box sx={{ 
                display: 'flex', 
                alignItems: 'center', 
                mb: 3,
                pb: 2,
                borderBottom: '2px solid',
                borderColor: 'primary.main'
              }}>
                <Avatar sx={{ bgcolor: 'primary.main', mr: 2, width: 40, height: 40 }}>
                  <Timeline />
                </Avatar>
                <Box>
                  <Typography variant="h5" component="h3" sx={{ fontWeight: 700, color: 'text.primary' }}>
                    Meeting Activity Trend
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Monthly meeting volume over time
                  </Typography>
                </Box>
              </Box>
              <ResponsiveContainer width="100%" height={350}>
                <AreaChart data={analyticsData.monthly_activity}>
                  <defs>
                    <linearGradient id="colorMeetings" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor="#667eea" stopOpacity={0.8}/>
                      <stop offset="95%" stopColor="#667eea" stopOpacity={0.1}/>
                    </linearGradient>
                  </defs>
                  <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
                  <XAxis 
                    dataKey="month" 
                    tick={{ fill: '#64748b', fontSize: 12 }}
                    axisLine={{ stroke: '#e2e8f0' }}
                  />
                  <YAxis 
                    tick={{ fill: '#64748b', fontSize: 12 }}
                    axisLine={{ stroke: '#e2e8f0' }}
                  />
                  <Tooltip 
                    formatter={(value, name) => [value, 'Meetings']}
                    labelStyle={{ color: '#1e293b', fontWeight: 600 }}
                    contentStyle={{
                      backgroundColor: 'white',
                      border: '1px solid #e2e8f0',
                      borderRadius: '8px',
                      boxShadow: '0 4px 12px rgba(0,0,0,0.1)'
                    }}
                  />
                  <Area 
                    type="monotone" 
                    dataKey="meetings" 
                    stroke="#667eea" 
                    fillOpacity={1} 
                    fill="url(#colorMeetings)" 
                    strokeWidth={3}
                    dot={{ fill: '#667eea', strokeWidth: 2, r: 6 }}
                    activeDot={{ r: 8, stroke: '#667eea', strokeWidth: 2, fill: 'white' }}
                  />
                </AreaChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>
        </Grid>

        {/* Content Distribution */}
        <Grid item xs={12} lg={4}>
          <Card 
            elevation={0} 
            sx={{ 
              height: 450, 
              borderRadius: 3,
              border: '1px solid',
              borderColor: 'divider',
              background: 'linear-gradient(145deg, #ffffff 0%, #f8fafc 100%)',
              boxShadow: '0 4px 12px rgba(0,0,0,0.05)',
            }}
          >
            <CardContent sx={{ p: 3, height: '100%' }}>
              <Box sx={{ 
                display: 'flex', 
                alignItems: 'center', 
                mb: 3,
                pb: 2,
                borderBottom: '2px solid',
                borderColor: 'secondary.main'
              }}>
                <Avatar sx={{ bgcolor: 'secondary.main', mr: 2, width: 40, height: 40 }}>
                  <PieChartIcon />
                </Avatar>
                <Box>
                  <Typography variant="h5" component="h3" sx={{ fontWeight: 700, color: 'text.primary' }}>
                    Content Distribution
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Breakdown by content type
                  </Typography>
                </Box>
              </Box>
              {contentChartData.length > 0 ? (
                <ResponsiveContainer width="100%" height={350}>
                  <PieChart>
                    <Pie
                      data={contentChartData}
                      cx="50%"
                      cy="50%"
                      outerRadius={100}
                      innerRadius={40}
                      dataKey="value"
                      strokeWidth={3}
                      stroke="#ffffff"
                    >
                      {contentChartData.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                      ))}
                    </Pie>
                    <Tooltip 
                      formatter={(value, name) => [value, 'Items']}
                      contentStyle={{
                        backgroundColor: 'white',
                        border: '1px solid #e2e8f0',
                        borderRadius: '8px',
                        boxShadow: '0 4px 12px rgba(0,0,0,0.1)'
                      }}
                    />
                    <Legend 
                      verticalAlign="bottom" 
                      height={36}
                      iconType="circle"
                      wrapperStyle={{ paddingTop: '20px', fontSize: '12px' }}
                    />
                  </PieChart>
                </ResponsiveContainer>
              ) : (
                <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'center', height: 350 }}>
                  <Typography variant="body2" color="text.secondary">
                    No content data available
                  </Typography>
                </Box>
              )}
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      <Grid container spacing={3}>
        {/* Participant Activity */}
        <Grid item xs={12} lg={6}>
          <Card 
            elevation={0} 
            sx={{ 
              borderRadius: 3,
              border: '1px solid',
              borderColor: 'divider',
              background: 'linear-gradient(145deg, #ffffff 0%, #f8fafc 100%)',
              boxShadow: '0 4px 12px rgba(0,0,0,0.05)',
            }}
          >
            <CardContent sx={{ p: 3 }}>
              <Box sx={{ 
                display: 'flex', 
                alignItems: 'center', 
                mb: 3,
                pb: 2,
                borderBottom: '2px solid',
                borderColor: 'success.main'
              }}>
                <Avatar sx={{ bgcolor: 'success.main', mr: 2, width: 40, height: 40 }}>
                  <People />
                </Avatar>
                <Box>
                  <Typography variant="h5" component="h3" sx={{ fontWeight: 700, color: 'text.primary' }}>
                    Top Participants
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Most active meeting participants
                  </Typography>
                </Box>
              </Box>
              {participantChartData.length > 0 ? (
                <ResponsiveContainer width="100%" height={350}>
                  <BarChart data={participantChartData} layout="horizontal" margin={{ left: 20, right: 20 }}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
                    <XAxis 
                      type="number" 
                      tick={{ fill: '#64748b', fontSize: 12 }}
                      axisLine={{ stroke: '#e2e8f0' }}
                    />
                    <YAxis 
                      dataKey="name" 
                      type="category" 
                      width={100} 
                      tick={{ fill: '#64748b', fontSize: 11 }}
                      axisLine={{ stroke: '#e2e8f0' }}
                    />
                    <Tooltip 
                      formatter={(value, name, props) => [value, 'Meetings']}
                      labelFormatter={(value, payload) => payload?.[0]?.payload?.fullName || value}
                      contentStyle={{
                        backgroundColor: 'white',
                        border: '1px solid #e2e8f0',
                        borderRadius: '8px',
                        boxShadow: '0 4px 12px rgba(0,0,0,0.1)'
                      }}
                    />
                    <Bar 
                      dataKey="meetings" 
                      fill="#43e97b" 
                      radius={[0, 8, 8, 0]}
                      stroke="#38f9d7"
                      strokeWidth={1}
                    />
                  </BarChart>
                </ResponsiveContainer>
              ) : (
                <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'center', height: 350 }}>
                  <Typography variant="body2" color="text.secondary">
                    No participant data available
                  </Typography>
                </Box>
              )}
            </CardContent>
          </Card>
        </Grid>

        {/* Recent Activity */}
        <Grid item xs={12} lg={6}>
          <Card 
            elevation={0} 
            sx={{ 
              borderRadius: 3,
              border: '1px solid',
              borderColor: 'divider',
              background: 'linear-gradient(145deg, #ffffff 0%, #f8fafc 100%)',
              boxShadow: '0 4px 12px rgba(0,0,0,0.05)',
            }}
          >
            <CardContent sx={{ p: 3 }}>
              <Box sx={{ 
                display: 'flex', 
                alignItems: 'center', 
                mb: 3,
                pb: 2,
                borderBottom: '2px solid',
                borderColor: 'info.main'
              }}>
                <Avatar sx={{ bgcolor: 'info.main', mr: 2, width: 40, height: 40 }}>
                  <Schedule />
                </Avatar>
                <Box>
                  <Typography variant="h5" component="h3" sx={{ fontWeight: 700, color: 'text.primary' }}>
                    Recent Activity
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Latest meeting uploads
                  </Typography>
                </Box>
              </Box>
              <List dense sx={{ maxHeight: 350, overflow: 'auto' }}>
                {analyticsData.recent_activity?.slice(0, 8).map((activity, index) => (
                  <ListItem 
                    key={index} 
                    sx={{ 
                      px: 0, 
                      py: 1.5,
                      borderRadius: 2,
                      mb: 1,
                      '&:hover': {
                        bgcolor: 'rgba(0,0,0,0.02)',
                      }
                    }}
                  >
                    <ListItemIcon>
                      <Avatar 
                        sx={{ 
                          bgcolor: `hsl(${(index * 137.5) % 360}, 70%, 50%)`, 
                          width: 40, 
                          height: 40,
                          boxShadow: '0 2px 8px rgba(0,0,0,0.1)'
                        }}
                      >
                        <Description sx={{ fontSize: 20 }} />
                      </Avatar>
                    </ListItemIcon>
                    <ListItemText
                      primary={
                        <Typography variant="body1" sx={{ fontWeight: 600, color: 'text.primary', mb: 0.5 }}>
                          {activity.title}
                        </Typography>
                      }
                      secondary={
                        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, flexWrap: 'wrap' }}>
                          <Chip 
                            label={activity.date} 
                            size="small" 
                            variant="outlined"
                            sx={{ fontSize: '0.7rem', height: 20 }}
                          />
                          <Chip 
                            label={`${activity.participants} participants`} 
                            size="small" 
                            color="primary"
                            sx={{ fontSize: '0.7rem', height: 20 }}
                          />
                          <Chip 
                            label={activity.language?.toUpperCase() || 'UNKNOWN'} 
                            size="small" 
                            color="secondary"
                            sx={{ fontSize: '0.7rem', height: 20 }}
                          />
                        </Box>
                      }
                    />
                  </ListItem>
                ))}
                {(!analyticsData.recent_activity || analyticsData.recent_activity.length === 0) && (
                  <Box sx={{ textAlign: 'center', py: 4 }}>
                    <Typography variant="body2" color="text.secondary">
                      No recent activity
                    </Typography>
                  </Box>
                )}
              </List>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Language Distribution */}
      {languageChartData.length > 0 && (
        <Grid container spacing={3} sx={{ mt: 1 }}>
          <Grid item xs={12}>
            <Card 
              elevation={0} 
              sx={{ 
                borderRadius: 3,
                border: '1px solid',
                borderColor: 'divider',
                background: 'linear-gradient(145deg, #ffffff 0%, #f8fafc 100%)',
                boxShadow: '0 4px 12px rgba(0,0,0,0.05)',
              }}
            >
              <CardContent sx={{ p: 3 }}>
                <Box sx={{ 
                  display: 'flex', 
                  alignItems: 'center', 
                  mb: 3,
                  pb: 2,
                  borderBottom: '2px solid',
                  borderColor: 'warning.main'
                }}>
                  <Avatar sx={{ bgcolor: 'warning.main', mr: 2, width: 40, height: 40 }}>
                    <Language />
                  </Avatar>
                  <Box>
                    <Typography variant="h5" component="h3" sx={{ fontWeight: 700, color: 'text.primary' }}>
                      Language Distribution
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      Languages detected in meetings
                    </Typography>
                  </Box>
                </Box>
                <Grid container spacing={2}>
                  {languageChartData.map((lang, index) => (
                    <Grid item key={lang.name}>
                      <Box
                        sx={{
                          display: 'flex',
                          alignItems: 'center',
                          gap: 1,
                          p: 2,
                          borderRadius: 2,
                          border: '1px solid',
                          borderColor: 'divider',
                          bgcolor: 'background.paper',
                          minWidth: 120,
                          '&:hover': {
                            boxShadow: '0 2px 8px rgba(0,0,0,0.1)',
                            transform: 'translateY(-2px)',
                            transition: 'all 0.2s ease',
                          }
                        }}
                      >
                        <Box
                          sx={{
                            width: 12,
                            height: 12,
                            borderRadius: '50%',
                            bgcolor: COLORS[index % COLORS.length],
                          }}
                        />
                        <Box>
                          <Typography variant="body2" sx={{ fontWeight: 600 }}>
                            {lang.name}
                          </Typography>
                          <Typography variant="caption" color="text.secondary">
                            {lang.count} meeting{lang.count !== 1 ? 's' : ''}
                          </Typography>
                        </Box>
                      </Box>
                    </Grid>
                  ))}
                </Grid>
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      )}
    </Box>
  );
};

export default Statistics;
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


const COLORS = ['#1565c0', '#f57c00', '#388e3c', '#7b1fa2', '#d32f2f', '#0097a7', '#fbc02d', '#5d4037'];

const Statistics = ({ stats, loading = false }) => {
  const [analyticsData, setAnalyticsData] = useState(null);
  const [analyticsLoading, setAnalyticsLoading] = useState(true);
  const [analyticsError, setAnalyticsError] = useState(null);

  useEffect(() => {
    // Use the enhanced analytics data from props if available
    if (stats?.enhanced_analytics) {
      setAnalyticsData(stats.enhanced_analytics);
      setAnalyticsLoading(false);
    }
  }, [stats]);

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
    <Box sx={{ width: '100%' }}>
      <Typography variant="h5" component="h2" gutterBottom sx={{ mb: 3, fontWeight: 600 }}>
        📊 Enterprise Analytics Dashboard
      </Typography>

      {/* Hero Metrics Row - Full Width */}
      <Box sx={{ 
        display: 'flex', 
        gap: 3, 
        mb: 4,
        width: '100%'
      }}>
        {keyMetrics.map((metric, index) => (
          <Box key={index} sx={{ 
            flex: '1 1 25%',
            minWidth: 0
          }}>
            <Card elevation={2} sx={{ 
              height: '100%', 
              borderRadius: 3,
              border: '1px solid #e0e0e0',
              '&:hover': {
                boxShadow: '0 4px 15px rgba(0,0,0,0.1)',
                transform: 'translateY(-1px)',
                transition: 'all 0.2s ease'
              }
            }}>
              <CardContent sx={{ textAlign: 'center', p: 3 }}>
                <Box sx={{ mb: 2 }}>
                  {React.cloneElement(metric.icon, { 
                    sx: { fontSize: 36, color: metric.color } 
                  })}
                </Box>
                <Typography variant="h3" component="div" sx={{ color: metric.color, fontWeight: 700, mb: 1 }}>
                  {metric.value}
                </Typography>
                <Typography variant="h6" color="text.primary" gutterBottom sx={{ fontWeight: 600 }}>
                  {metric.title}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  {metric.subtitle}
                </Typography>
              </CardContent>
            </Card>
          </Box>
        ))}
      </Box>

      {/* Main Charts Row - Perfect 50/50 Layout */}
      <Box sx={{ 
        display: 'flex', 
        gap: 3, 
        mb: 4,
        width: '100%'
      }}>
        {/* Meeting Activity Timeline - Left 50% */}
        <Box sx={{ 
          flex: '1 1 50%',
          minWidth: 0
        }}>
          <Card elevation={2} sx={{ 
            height: 500, 
            borderRadius: 3,
            border: '1px solid #e0e0e0',
            '&:hover': {
              boxShadow: '0 8px 25px rgba(0,0,0,0.15)',
              transform: 'translateY(-2px)',
              transition: 'all 0.3s ease'
            }
          }}>
            <CardContent sx={{ p: 3, height: '100%' }}>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 3 }}>
                <Timeline sx={{ mr: 2, color: 'primary.main', fontSize: 28 }} />
                <Box>
                  <Typography variant="h6" component="h3" sx={{ fontWeight: 600, color: '#1e293b' }}>
                    Meeting Activity Timeline
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Track meeting volume trends
                  </Typography>
                </Box>
              </Box>
              <Box sx={{ height: 400, width: '100%' }}>
                <ResponsiveContainer width="100%" height="100%">
                  <AreaChart data={analyticsData.monthly_activity} margin={{ top: 20, right: 20, left: 10, bottom: 20 }}>
                    <defs>
                      <linearGradient id="colorMeetings" x1="0" y1="0" x2="0" y2="1">
                        <stop offset="5%" stopColor="#1565c0" stopOpacity={0.3}/>
                        <stop offset="95%" stopColor="#1565c0" stopOpacity={0}/>
                      </linearGradient>
                    </defs>
                    <CartesianGrid strokeDasharray="3 3" stroke="#e0e0e0" />
                    <XAxis 
                      dataKey="month" 
                      tick={{ fontSize: 12, fill: '#666' }}
                      axisLine={{ stroke: '#ccc' }}
                    />
                    <YAxis 
                      tick={{ fontSize: 12, fill: '#666' }}
                      axisLine={{ stroke: '#ccc' }}
                    />
                    <Tooltip 
                      formatter={(value, name) => [value, 'Meetings']}
                      labelStyle={{ color: '#1e293b' }}
                      contentStyle={{
                        backgroundColor: 'white',
                        border: '1px solid #ccc',
                        borderRadius: '8px',
                        boxShadow: '0 4px 12px rgba(0,0,0,0.1)'
                      }}
                    />
                    <Area 
                      type="monotone" 
                      dataKey="meetings" 
                      stroke="#1565c0" 
                      fillOpacity={1} 
                      fill="url(#colorMeetings)" 
                      strokeWidth={3}
                    />
                  </AreaChart>
                </ResponsiveContainer>
              </Box>
            </CardContent>
          </Card>
        </Box>

        {/* Top Participants - Right 50% */}
        <Box sx={{ 
          flex: '1 1 50%',
          minWidth: 0
        }}>
          <Card elevation={2} sx={{ 
            height: 500, 
            borderRadius: 3,
            border: '1px solid #e0e0e0',
            '&:hover': {
              boxShadow: '0 8px 25px rgba(0,0,0,0.15)',
              transform: 'translateY(-2px)',
              transition: 'all 0.3s ease'
            }
          }}>
            <CardContent sx={{ p: 3, height: '100%' }}>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 3 }}>
                <People sx={{ mr: 2, color: 'success.main', fontSize: 28 }} />
                <Box>
                  <Typography variant="h6" component="h3" sx={{ fontWeight: 600, color: '#1e293b' }}>
                    Top Participants
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Most active meeting participants
                  </Typography>
                </Box>
              </Box>
              {participantChartData.length > 0 ? (
                <Box sx={{ height: 400, width: '100%' }}>
                  <ResponsiveContainer width="100%" height="100%">
                    <BarChart 
                      data={participantChartData} 
                      layout="horizontal" 
                      margin={{ left: 80, right: 20, top: 20, bottom: 20 }}
                    >
                      <CartesianGrid strokeDasharray="3 3" stroke="#e0e0e0" />
                      <XAxis 
                        type="number" 
                        tick={{ fontSize: 12, fill: '#666' }}
                        axisLine={{ stroke: '#ccc' }}
                      />
                      <YAxis 
                        dataKey="name" 
                        type="category" 
                        width={80} 
                        tick={{ fontSize: 11, fill: '#666' }}
                        axisLine={{ stroke: '#ccc' }}
                      />
                      <Tooltip 
                        formatter={(value, name, props) => [value, 'Meetings']}
                        labelFormatter={(value, payload) => payload?.[0]?.payload?.fullName || value}
                        contentStyle={{
                          backgroundColor: 'white',
                          border: '1px solid #ccc',
                          borderRadius: '8px',
                          boxShadow: '0 4px 12px rgba(0,0,0,0.1)'
                        }}
                      />
                      <Bar 
                        dataKey="meetings" 
                        fill="#1565c0" 
                        radius={[0, 4, 4, 0]}
                        stroke="#0d47a1"
                        strokeWidth={1}
                      />
                    </BarChart>
                  </ResponsiveContainer>
                </Box>
              ) : (
                <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'center', height: 400 }}>
                  <Typography variant="body2" color="text.secondary">
                    No participant data available
                  </Typography>
                </Box>
              )}
            </CardContent>
          </Card>
        </Box>
      </Box>

      {/* Secondary Charts Row - 50/50 Layout */}
      <Box sx={{ 
        display: 'flex', 
        gap: 3, 
        mb: 4,
        width: '100%'
      }}>
        {/* Content Distribution - Left 50% */}
        <Box sx={{ 
          flex: '1 1 50%',
          minWidth: 0
        }}>
          <Card elevation={2} sx={{ 
            height: 450, 
            borderRadius: 3,
            border: '1px solid #e0e0e0',
            '&:hover': {
              boxShadow: '0 8px 25px rgba(0,0,0,0.15)',
              transform: 'translateY(-2px)',
              transition: 'all 0.3s ease'
            }
          }}>
            <CardContent sx={{ p: 3, height: '100%' }}>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 3 }}>
                <PieChartIcon sx={{ mr: 2, color: 'secondary.main', fontSize: 28 }} />
                <Box>
                  <Typography variant="h6" component="h3" sx={{ fontWeight: 600, color: '#1e293b' }}>
                    Content Distribution
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Breakdown of meeting content types
                  </Typography>
                </Box>
              </Box>
              {contentChartData.length > 0 ? (
                <Box sx={{ height: 350, width: '100%' }}>
                  <ResponsiveContainer width="100%" height="100%">
                    <PieChart>
                      <Pie
                        data={contentChartData}
                        cx="50%"
                        cy="50%"
                        outerRadius={100}
                        fill="#8884d8"
                        dataKey="value"
                        label={({ name, value }) => `${name}: ${value}`}
                      >
                        {contentChartData.map((entry, index) => (
                          <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                        ))}
                      </Pie>
                      <Tooltip 
                        contentStyle={{
                          backgroundColor: 'white',
                          border: '1px solid #ccc',
                          borderRadius: '8px',
                          boxShadow: '0 4px 12px rgba(0,0,0,0.1)'
                        }}
                      />
                    </PieChart>
                  </ResponsiveContainer>
                </Box>
              ) : (
                <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'center', height: 350 }}>
                  <Typography variant="body2" color="text.secondary">
                    No content data available
                  </Typography>
                </Box>
              )}
            </CardContent>
          </Card>
        </Box>

        {/* Recent Activity - Right 50% */}
        <Box sx={{ 
          flex: '1 1 50%',
          minWidth: 0
        }}>
          <Card elevation={2} sx={{ 
            height: 450, 
            borderRadius: 3,
            border: '1px solid #e0e0e0',
            '&:hover': {
              boxShadow: '0 8px 25px rgba(0,0,0,0.15)',
              transform: 'translateY(-2px)',
              transition: 'all 0.3s ease'
            }
          }}>
            <CardContent sx={{ p: 3, height: '100%' }}>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 3 }}>
                <Schedule sx={{ mr: 2, color: 'info.main', fontSize: 28 }} />
                <Box>
                  <Typography variant="h6" component="h3" sx={{ fontWeight: 600, color: '#1e293b' }}>
                    Recent Activity
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Latest meeting uploads
                  </Typography>
                </Box>
              </Box>
              <Box sx={{ height: 350, overflow: 'auto' }}>
                <List dense>
                  {analyticsData.recent_activity?.slice(0, 10).map((activity, index) => (
                    <ListItem key={index} sx={{ py: 1, px: 0 }}>
                      <ListItemIcon>
                        <Avatar sx={{ bgcolor: 'primary.main', width: 32, height: 32 }}>
                          <Description sx={{ fontSize: 16 }} />
                        </Avatar>
                      </ListItemIcon>
                      <ListItemText
                        primary={activity.title}
                        secondary={`${activity.date} • ${activity.participants} participants • ${activity.language?.toUpperCase()}`}
                        primaryTypographyProps={{ variant: 'body2' }}
                        secondaryTypographyProps={{ variant: 'caption' }}
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
              </Box>
            </CardContent>
          </Card>
        </Box>
      </Box>

      {/* Language Distribution - Full Width */}
      {languageChartData.length > 0 && (
        <Box sx={{ width: '100%' }}>
          <Card elevation={2} sx={{ 
            borderRadius: 3,
            border: '1px solid #e0e0e0',
            '&:hover': {
              boxShadow: '0 4px 15px rgba(0,0,0,0.1)',
              transform: 'translateY(-1px)',
              transition: 'all 0.2s ease'
            }
          }}>
            <CardContent sx={{ p: 3 }}>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 3 }}>
                <Language sx={{ mr: 2, color: 'warning.main', fontSize: 28 }} />
                <Box>
                  <Typography variant="h6" component="h3" sx={{ fontWeight: 600, color: '#1e293b' }}>
                    Language Distribution
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Languages detected in meetings
                  </Typography>
                </Box>
              </Box>
              <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 2 }}>
                {languageChartData.map((lang, index) => (
                  <Chip
                    key={lang.name}
                    label={`${lang.name}: ${lang.count}`}
                    variant="outlined"
                    color="primary"
                    size="medium"
                  />
                ))}
              </Box>
            </CardContent>
          </Card>
        </Box>
      )}
    </Box>
  );
};

export default Statistics;
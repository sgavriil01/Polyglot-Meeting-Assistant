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
  Speed,
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
  ScatterChart,
  Scatter,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from 'recharts';


const COLORS = ['#1565c0', '#f57c00', '#388e3c', '#7b1fa2', '#d32f2f', '#0097a7', '#fbc02d', '#5d4037'];

// Language code mapping for better display names
const LANGUAGE_NAMES = {
  'en': 'English',
  'es': 'Spanish', 
  'fr': 'French',
  'de': 'German',
  'it': 'Italian',
  'pt': 'Portuguese',
  'ru': 'Russian',
  'zh': 'Chinese',
  'ja': 'Japanese',
  'ko': 'Korean',
  'ar': 'Arabic',
  'hi': 'Hindi',
  'nl': 'Dutch',
  'pl': 'Polish',
  'sv': 'Swedish',
  'da': 'Danish',
  'no': 'Norwegian',
  'fi': 'Finnish',
  'tr': 'Turkish',
  'cs': 'Czech',
  'hu': 'Hungarian',
  'ro': 'Romanian',
  'bg': 'Bulgarian',
  'hr': 'Croatian',
  'sk': 'Slovak',
  'sl': 'Slovenian',
  'et': 'Estonian',
  'lv': 'Latvian',
  'lt': 'Lithuanian',
  'uk': 'Ukrainian',
  'be': 'Belarusian',
  'mk': 'Macedonian',
  'sq': 'Albanian',
  'mt': 'Maltese',
  'ga': 'Irish',
  'cy': 'Welsh',
  'eu': 'Basque',
  'ca': 'Catalan',
  'gl': 'Galician',
  'unknown': 'Unknown',
  'uncertain': 'Uncertain'
};

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
    .filter(([name, count]) => name && name.trim() && count > 0)  // Filter out empty/invalid entries
    .sort((a, b) => b[1] - a[1])  // Sort by count descending
    .slice(0, 8)  // Limit to top 8 for better visualization
    .map(([name, count]) => ({
      name: name.length > 15 ? name.substring(0, 15) + '...' : name,
      meetings: count,
    }));

  // Prepare language distribution data
  const languageChartData = Object.entries(analyticsData.language_distribution || {}).map(([lang, count]) => ({
    name: LANGUAGE_NAMES[lang] || lang.toUpperCase(),
    code: lang,
    value: count,
    count: count,
  }));

  return (
    <Box sx={{ width: '100%' }}>
      <Typography variant="h5" component="h2" gutterBottom sx={{ mb: 3, fontWeight: 600 }}>
        📊 Enterprise Analytics Dashboard
      </Typography>

      {/* Main Charts Row */}
      <Box sx={{ 
        display: 'flex', 
        gap: 3, 
        mb: 4,
        width: '100%'
      }}>
        {/* Processing Efficiency Dashboard */}
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
                <Speed sx={{ mr: 2, color: 'primary.main', fontSize: 28 }} />
                <Box>
                  <Typography variant="h6" component="h3" sx={{ fontWeight: 600, color: '#1e293b' }}>
                    Session Overview
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Current processing session metrics
                  </Typography>
                </Box>
              </Box>
              
              <Grid container spacing={2} sx={{ height: 'calc(100% - 80px)' }}>
                {/* Top Row - Main Metrics */}
                <Grid item xs={6}>
                  <Card sx={{ 
                    background: '#667eea',
                    color: 'white',
                    height: '120px',
                    borderRadius: 2,
                    boxShadow: '0 4px 12px rgba(102, 126, 234, 0.3)',
                    transition: 'transform 0.2s ease-in-out, box-shadow 0.2s ease-in-out',
                    '&:hover': {
                      transform: 'translateY(-2px)',
                      boxShadow: '0 8px 20px rgba(102, 126, 234, 0.4)',
                    }
                  }}>
                    <CardContent sx={{ 
                      textAlign: 'center',
                      p: 2,
                      height: '100%',
                      display: 'flex',
                      flexDirection: 'column',
                      justifyContent: 'center'
                    }}>
                      <Typography variant="h2" sx={{ fontWeight: 'bold', color: 'white', mb: 1 }}>
                        {analyticsData.total_meetings}
                      </Typography>
                      <Typography variant="body2" sx={{ color: 'rgba(255,255,255,0.9)', fontWeight: 600 }}>
                        Total Meetings
                      </Typography>
                      <Typography variant="caption" sx={{ color: 'rgba(255,255,255,0.7)' }}>
                        Files processed
                      </Typography>
                    </CardContent>
                  </Card>
                </Grid>

                <Grid item xs={6}>
                  <Card sx={{ 
                    background: '#f5576c',
                    color: 'white',
                    height: '120px',
                    borderRadius: 2,
                    boxShadow: '0 4px 12px rgba(245, 87, 108, 0.3)',
                    transition: 'transform 0.2s ease-in-out, box-shadow 0.2s ease-in-out',
                    '&:hover': {
                      transform: 'translateY(-2px)',
                      boxShadow: '0 8px 20px rgba(245, 87, 108, 0.4)',
                    }
                  }}>
                    <CardContent sx={{ 
                      textAlign: 'center',
                      p: 2,
                      height: '100%',
                      display: 'flex',
                      flexDirection: 'column',
                      justifyContent: 'center'
                    }}>
                      <Typography variant="h2" sx={{ fontWeight: 'bold', color: 'white', mb: 1 }}>
                        {analyticsData.action_items_stats?.total_action_items || 0}
                      </Typography>
                      <Typography variant="body2" sx={{ color: 'rgba(255,255,255,0.9)', fontWeight: 600 }}>
                        Action Items
                      </Typography>
                      <Typography variant="caption" sx={{ color: 'rgba(255,255,255,0.7)' }}>
                        {analyticsData.action_items_stats?.avg_per_meeting?.toFixed(1) || 0} per meeting
                      </Typography>
                    </CardContent>
                  </Card>
                </Grid>

                {/* Second Row - Additional Metrics */}
                <Grid item xs={6}>
                  <Card sx={{ 
                    background: '#4facfe',
                    color: 'white',
                    height: '120px',
                    borderRadius: 2,
                    boxShadow: '0 4px 12px rgba(79, 172, 254, 0.3)',
                    transition: 'transform 0.2s ease-in-out, box-shadow 0.2s ease-in-out',
                    '&:hover': {
                      transform: 'translateY(-2px)',
                      boxShadow: '0 8px 20px rgba(79, 172, 254, 0.4)',
                    }
                  }}>
                    <CardContent sx={{ 
                      textAlign: 'center',
                      p: 2,
                      height: '100%',
                      display: 'flex',
                      flexDirection: 'column',
                      justifyContent: 'center'
                    }}>
                      <Typography variant="h2" sx={{ fontWeight: 'bold', color: 'white', mb: 1 }}>
                        {Object.keys(analyticsData.participant_activity || {}).length}
                      </Typography>
                      <Typography variant="body2" sx={{ color: 'rgba(255,255,255,0.9)', fontWeight: 600 }}>
                        Participants
                      </Typography>
                      <Typography variant="caption" sx={{ color: 'rgba(255,255,255,0.7)' }}>
                        Unique speakers
                      </Typography>
                    </CardContent>
                  </Card>
                </Grid>

                <Grid item xs={6}>
                  <Card sx={{ 
                    background: '#43e97b',
                    color: 'white',
                    height: '120px',
                    borderRadius: 2,
                    boxShadow: '0 4px 12px rgba(67, 233, 123, 0.3)',
                    transition: 'transform 0.2s ease-in-out, box-shadow 0.2s ease-in-out',
                    '&:hover': {
                      transform: 'translateY(-2px)',
                      boxShadow: '0 8px 20px rgba(67, 233, 123, 0.4)',
                    }
                  }}>
                    <CardContent sx={{ 
                      textAlign: 'center',
                      p: 2,
                      height: '100%',
                      display: 'flex',
                      flexDirection: 'column',
                      justifyContent: 'center'
                    }}>
                      <Typography variant="h2" sx={{ fontWeight: 'bold', color: 'white', mb: 1 }}>
                        {Object.keys(analyticsData.language_distribution || {}).length}
                      </Typography>
                      <Typography variant="body2" sx={{ color: 'rgba(255,255,255,0.9)', fontWeight: 600 }}>
                        Languages
                      </Typography>
                      <Typography variant="caption" sx={{ color: 'rgba(255,255,255,0.7)' }}>
                        Detected
                      </Typography>
                    </CardContent>
                  </Card>
                </Grid>

                {/* Content Analysis Summary */}
                <Grid item xs={12}>
                  <Box sx={{ mt: 2 }}>
                    <Typography variant="subtitle2" color="text.primary" sx={{ mb: 2, fontWeight: 600 }}>
                      Content Breakdown
                    </Typography>
                    <Grid container spacing={1}>
                      {Object.entries(analyticsData.content_distribution || {}).map(([type, count], index) => (
                        <Grid item xs={6} sm={4} md={2.4} key={type}>
                          <Box sx={{ 
                            textAlign: 'center',
                            p: 1.5,
                            borderRadius: 1,
                            border: '1px solid #e0e0e0',
                            bgcolor: 'grey.50'
                          }}>
                            <Typography variant="h6" sx={{ fontWeight: 'bold', color: COLORS[index % COLORS.length] }}>
                              {count}
                            </Typography>
                            <Typography variant="caption" color="text.secondary" sx={{ textTransform: 'capitalize' }}>
                              {type.replace('_', ' ')}
                            </Typography>
                          </Box>
                        </Grid>
                      ))}
                    </Grid>
                  </Box>
                </Grid>
              </Grid>
            </CardContent>
          </Card>
        </Box>

        {/* Top Participants */}
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
                      margin={{ left: 20, right: 20, top: 20, bottom: 80 }}
                    >
                      <CartesianGrid 
                        strokeDasharray="2 2" 
                        stroke="#e0e0e0" 
                        strokeWidth={0.5}
                        horizontal={true}
                        vertical={false}
                      />
                      <XAxis 
                        dataKey="name" 
                        tick={{ fontSize: 11, fill: '#666', angle: -45, textAnchor: 'end' }}
                        axisLine={{ stroke: '#ccc', strokeWidth: 1 }}
                        tickLine={{ stroke: '#ccc', strokeWidth: 1 }}
                        interval={0}
                        height={70}
                      />
                      <YAxis 
                        tick={{ fontSize: 12, fill: '#666' }}
                        axisLine={{ stroke: '#ccc', strokeWidth: 1 }}
                        tickLine={{ stroke: '#ccc', strokeWidth: 1 }}
                        label={{ value: 'Mentions', angle: -90, position: 'insideLeft', style: { textAnchor: 'middle', fill: '#666', fontSize: '12px' } }}
                      />
                      <Tooltip 
                        formatter={(value, name, props) => [`${value} mentions`, props.payload.fullName]}
                        labelFormatter={(value, payload) => {
                          const data = participantChartData.find(p => p.name === value);
                          return data?.fullName || value;
                        }}
                        contentStyle={{
                          backgroundColor: 'rgba(255, 255, 255, 0.95)',
                          border: '2px solid #4facfe',
                          borderRadius: '8px',
                          boxShadow: '0 4px 12px rgba(0,0,0,0.1)',
                          fontSize: '13px',
                          padding: '8px 12px'
                        }}
                        cursor={{ fill: 'rgba(79, 172, 254, 0.05)' }}
                      />
                      <Bar 
                        dataKey="meetings" 
                        fill="#4facfe"
                        stroke="#2196f3"
                        strokeWidth={1}
                        radius={[4, 4, 0, 0]}
                      />
                    </BarChart>
                  </ResponsiveContainer>
                </Box>
              ) : (
                <Box sx={{ 
                  display: 'flex', 
                  alignItems: 'center', 
                  justifyContent: 'center', 
                  height: 400,
                  flexDirection: 'column',
                  gap: 2
                }}>
                  <People sx={{ fontSize: 64, color: 'text.disabled' }} />
                  <Typography variant="h6" color="text.secondary" align="center">
                    No participant data available
                  </Typography>
                  <Typography variant="body2" color="text.secondary" align="center">
                    Upload meetings with participant information to see activity charts
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
                        secondary={`${activity.date} • ${activity.participants} participants • ${LANGUAGE_NAMES[activity.language] || activity.language?.toUpperCase() || 'Unknown'}`}
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
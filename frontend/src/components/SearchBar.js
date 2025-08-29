import React, { useState, useEffect } from 'react';
import {
  Box,
  TextField,
  Button,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Slider,
  Typography,
  Paper,
  IconButton,
  Tooltip,
  Chip,
  OutlinedInput,
  Autocomplete,
} from '@mui/material';
import { Search, Clear, FilterList, DateRange, People } from '@mui/icons-material';
import apiService from '../services/api';

const SearchBar = ({ onSearch, loading = false, refreshTrigger = 0 }) => {
  const [query, setQuery] = useState('');
  const [contentType, setContentType] = useState('all');
  const [topK, setTopK] = useState(10);
  const [showFilters, setShowFilters] = useState(false);
  
  // Advanced filter states
  const [dateFrom, setDateFrom] = useState('');
  const [dateTo, setDateTo] = useState('');
  const [selectedParticipants, setSelectedParticipants] = useState([]);
  const [minRelevance, setMinRelevance] = useState(0);
  
  // Filter options from API
  const [availableParticipants, setAvailableParticipants] = useState([]);
  const [dateRange, setDateRange] = useState({ earliest: '', latest: '' });
  const [filtersLoading, setFiltersLoading] = useState(true);

  // Load filter options when component mounts
  useEffect(() => {
    const loadFilterOptions = async () => {
      try {
        setFiltersLoading(true);
        const filters = await apiService.getSearchFilters();
        setAvailableParticipants(filters.participants || []);
        setDateRange(filters.date_range || { earliest: '', latest: '' });
      } catch (error) {
        console.error('Failed to load filter options:', error);
        // Set empty defaults on error
        setAvailableParticipants([]);
        setDateRange({ earliest: '', latest: '' });
      } finally {
        setFiltersLoading(false);
      }
    };
    
    loadFilterOptions();
  }, [refreshTrigger]);

  const handleSearch = () => {
    if (query.trim()) {
      const searchParams = {
        query: query.trim(),
        topK,
        contentTypes: contentType === 'all' ? null : [contentType],
        dateFrom: dateFrom || null,
        dateTo: dateTo || null,
        participants: selectedParticipants.length > 0 ? selectedParticipants : null,
        minRelevance: minRelevance > 0 ? minRelevance / 100 : null, // Convert percentage to decimal
      };
      onSearch(searchParams);
    }
  };

  const handleClear = () => {
    setQuery('');
    setContentType('all');
    setTopK(10);
    setDateFrom('');
    setDateTo('');
    setSelectedParticipants([]);
    setMinRelevance(0);
  };

  const handleKeyPress = (event) => {
    if (event.key === 'Enter') {
      handleSearch();
    }
  };

  return (
    <Paper elevation={2} sx={{ p: 3, mb: 3 }}>
      <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
        {/* Main Search Input */}
        <Box sx={{ display: 'flex', gap: 2, alignItems: 'center' }}>
          <TextField
            fullWidth
            variant="outlined"
            placeholder="Search for anything in your meetings..."
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            onKeyPress={handleKeyPress}
            disabled={loading}
            InputProps={{
              startAdornment: <Search sx={{ mr: 1, color: 'text.secondary' }} />,
            }}
          />
          <Button
            variant="contained"
            onClick={handleSearch}
            disabled={!query.trim() || loading}
            sx={{ minWidth: 120 }}
          >
            {loading ? 'Searching...' : 'Search'}
          </Button>
          <Tooltip title="Clear search">
            <IconButton onClick={handleClear} disabled={!query.trim()}>
              <Clear />
            </IconButton>
          </Tooltip>
          <Tooltip title="Show filters">
            <IconButton onClick={() => setShowFilters(!showFilters)}>
              <FilterList />
            </IconButton>
          </Tooltip>
        </Box>

        {/* Advanced Filters */}
        {showFilters && (
          <Box sx={{ pt: 2, borderTop: 1, borderColor: 'divider' }}>
            {/* First row of filters */}
            <Box sx={{ display: 'flex', gap: 2, alignItems: 'center', mb: 2, flexWrap: 'wrap' }}>
              <FormControl sx={{ minWidth: 180 }}>
                <InputLabel>Content Type</InputLabel>
                <Select
                  value={contentType}
                  label="Content Type"
                  onChange={(e) => setContentType(e.target.value)}
                >
                  <MenuItem value="all">All Content</MenuItem>
                  <MenuItem value="transcript">Transcripts</MenuItem>
                  <MenuItem value="summary">Summaries</MenuItem>
                  <MenuItem value="action_item">Action Items</MenuItem>
                  <MenuItem value="decision">Decisions</MenuItem>
                  <MenuItem value="timeline">Timelines</MenuItem>
                </Select>
              </FormControl>

              <TextField
                type="date"
                label="From Date"
                value={dateFrom}
                onChange={(e) => setDateFrom(e.target.value)}
                InputLabelProps={{ shrink: true }}
                sx={{ minWidth: 160 }}
              />

              <TextField
                type="date"
                label="To Date"
                value={dateTo}
                onChange={(e) => setDateTo(e.target.value)}
                InputLabelProps={{ shrink: true }}
                sx={{ minWidth: 160 }}
              />

              <Autocomplete
                multiple
                options={availableParticipants}
                value={selectedParticipants}
                onChange={(e, newValue) => setSelectedParticipants(newValue)}
                loading={filtersLoading}
                disabled={filtersLoading}
                renderInput={(params) => (
                  <TextField
                    {...params}
                    label="Participants"
                    placeholder={
                      filtersLoading 
                        ? "Loading participants..." 
                        : availableParticipants.length === 0 
                          ? "No participants found - upload meetings first"
                          : "Select participants..."
                    }
                  />
                )}
                renderTags={(tagValue, getTagProps) =>
                  tagValue.map((option, index) => (
                    <Chip
                      label={option}
                      {...getTagProps({ index })}
                      size="small"
                      icon={<People />}
                    />
                  ))
                }
                noOptionsText={
                  filtersLoading 
                    ? "Loading participants..." 
                    : "No participants found - upload meetings to see participants here"
                }
                sx={{ minWidth: 250 }}
              />
            </Box>

            {/* Second row of filters */}
            <Box sx={{ display: 'flex', gap: 4, alignItems: 'center', flexWrap: 'wrap' }}>
              <Box sx={{ minWidth: 200 }}>
                <Typography gutterBottom>Results Count: {topK}</Typography>
                <Slider
                  value={topK}
                  onChange={(e, newValue) => setTopK(newValue)}
                  min={1}
                  max={50}
                  marks={[
                    { value: 1, label: '1' },
                    { value: 25, label: '25' },
                    { value: 50, label: '50' },
                  ]}
                  valueLabelDisplay="auto"
                />
              </Box>

              <Box sx={{ minWidth: 200 }}>
                <Typography gutterBottom>Min Relevance: {minRelevance}%</Typography>
                <Slider
                  value={minRelevance}
                  onChange={(e, newValue) => setMinRelevance(newValue)}
                  min={0}
                  max={100}
                  marks={[
                    { value: 0, label: '0%' },
                    { value: 50, label: '50%' },
                    { value: 100, label: '100%' },
                  ]}
                  valueLabelDisplay="auto"
                />
              </Box>
            </Box>

            {/* Active filters display */}
            {(dateFrom || dateTo || selectedParticipants.length > 0 || minRelevance > 0) && (
              <Box sx={{ mt: 2, display: 'flex', gap: 1, flexWrap: 'wrap', alignItems: 'center' }}>
                <Typography variant="caption" color="text.secondary">Active filters:</Typography>
                {dateFrom && (
                  <Chip
                    label={`From: ${dateFrom}`}
                    size="small"
                    onDelete={() => setDateFrom('')}
                    icon={<DateRange />}
                  />
                )}
                {dateTo && (
                  <Chip
                    label={`To: ${dateTo}`}
                    size="small"
                    onDelete={() => setDateTo('')}
                    icon={<DateRange />}
                  />
                )}
                {selectedParticipants.map((participant) => (
                  <Chip
                    key={participant}
                    label={participant}
                    size="small"
                    onDelete={() => setSelectedParticipants(prev => prev.filter(p => p !== participant))}
                    icon={<People />}
                  />
                ))}
                {minRelevance > 0 && (
                  <Chip
                    label={`Min ${minRelevance}% relevance`}
                    size="small"
                    onDelete={() => setMinRelevance(0)}
                  />
                )}
              </Box>
            )}
          </Box>
        )}
      </Box>
    </Paper>
  );
};

export default SearchBar;



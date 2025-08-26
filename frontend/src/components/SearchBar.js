import React, { useState } from 'react';
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
} from '@mui/material';
import { Search, Clear, FilterList } from '@mui/icons-material';

const SearchBar = ({ onSearch, loading = false }) => {
  const [query, setQuery] = useState('');
  const [contentType, setContentType] = useState('all');
  const [topK, setTopK] = useState(10);
  const [showFilters, setShowFilters] = useState(false);

  const handleSearch = () => {
    if (query.trim()) {
      const searchParams = {
        query: query.trim(),
        topK,
        contentTypes: contentType === 'all' ? null : [contentType],
      };
      onSearch(searchParams);
    }
  };

  const handleClear = () => {
    setQuery('');
    setContentType('all');
    setTopK(10);
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
          <Box sx={{ display: 'flex', gap: 2, alignItems: 'center', pt: 2, borderTop: 1, borderColor: 'divider' }}>
            <FormControl sx={{ minWidth: 200 }}>
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
          </Box>
        )}
      </Box>
    </Paper>
  );
};

export default SearchBar;



import React, { useState, useCallback } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Button,
  LinearProgress,
  Alert,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  IconButton,
  Paper,
} from '@mui/material';
import {
  CloudUpload,
  Description,
  AudioFile,

  CheckCircle,
  Error,
  Delete,
} from '@mui/icons-material';

const FileUpload = ({ onUpload, loading = false }) => {
  const [files, setFiles] = useState([]);
  const [uploadStatus, setUploadStatus] = useState({});
  const [dragActive, setDragActive] = useState(false);

  const handleDrag = useCallback((e) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setDragActive(true);
    } else if (e.type === 'dragleave') {
      setDragActive(false);
    }
  }, []);

  const handleDrop = useCallback((e) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);

    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      const newFiles = Array.from(e.dataTransfer.files);
      setFiles(prev => [...prev, ...newFiles]);
    }
  }, []);

  const handleFileSelect = (event) => {
    const selectedFiles = Array.from(event.target.files);
    setFiles(prev => [...prev, ...selectedFiles]);
  };

  const removeFile = (index) => {
    setFiles(prev => prev.filter((_, i) => i !== index));
    setUploadStatus(prev => {
      const newStatus = { ...prev };
      delete newStatus[index];
      return newStatus;
    });
  };

  const uploadFiles = async () => {
    if (files.length === 0) return;

    for (let i = 0; i < files.length; i++) {
      const file = files[i];
      setUploadStatus(prev => ({
        ...prev,
        [i]: { status: 'uploading', message: 'Uploading file...', progress: 0 }
      }));

      try {
        // Simulate progress updates
        const progressInterval = setInterval(() => {
          setUploadStatus(prev => ({
            ...prev,
            [i]: { 
              ...prev[i], 
              progress: Math.min(prev[i].progress + 10, 90),
              message: prev[i].progress < 30 ? 'Uploading file...' : 
                       prev[i].progress < 60 ? 'Processing with AI...' :
                       prev[i].progress < 90 ? 'Generating insights...' : 'Finalizing...'
            }
          }));
        }, 200);

        const result = await onUpload(file);
        
        clearInterval(progressInterval);
        
        setUploadStatus(prev => ({
          ...prev,
          [i]: { status: 'success', message: result.message, progress: 100 }
        }));
      } catch (error) {
        setUploadStatus(prev => ({
          ...prev,
          [i]: { status: 'error', message: error.message || 'Upload failed', progress: 0 }
        }));
      }
    }
  };

  const getFileIcon = (file) => {
    const type = file.type;
    if (type.startsWith('audio/')) return <AudioFile color="primary" />;
    return <Description color="action" />;
  };

  const getFileTypeColor = (file) => {
    const type = file.type;
    if (type.startsWith('audio/')) return 'primary';
    return 'default';
  };

  const formatFileSize = (bytes) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  const isUploading = Object.values(uploadStatus).some(status => status.status === 'uploading');

  return (
    <Card elevation={2}>
      <CardContent>
        <Typography variant="h6" component="h3" gutterBottom>
          📁 Upload Meeting Files
        </Typography>

        {/* Drag & Drop Area */}
        <Paper
          elevation={dragActive ? 8 : 1}
          sx={{
            border: 2,
            borderColor: dragActive ? 'primary.main' : 'grey.300',
            borderStyle: 'dashed',
            borderRadius: 2,
            p: 4,
            textAlign: 'center',
            backgroundColor: dragActive ? 'primary.50' : 'background.paper',
            transition: 'all 0.2s ease',
            cursor: 'pointer',
          }}
          onDragEnter={handleDrag}
          onDragLeave={handleDrag}
          onDragOver={handleDrag}
          onDrop={handleDrop}
          onClick={() => document.getElementById('file-input').click()}
        >
          <CloudUpload sx={{ fontSize: 48, color: 'primary.main', mb: 2 }} />
          <Typography variant="h6" gutterBottom>
            Drag & drop files here
          </Typography>
          <Typography variant="body2" color="text.secondary" gutterBottom>
            or click to browse
          </Typography>
          <Typography variant="caption" color="text.secondary">
            Supports: Text files (.txt, .md), Audio files (.mp3, .wav, .m4a, .ogg, .flac) in 100+ languages
          </Typography>
          
          <input
            id="file-input"
            type="file"
            multiple
            accept=".txt,.md,.mp3,.wav,.m4a,.ogg,.flac"
            onChange={handleFileSelect}
            style={{ display: 'none' }}
          />
        </Paper>

        {/* File List */}
        {files.length > 0 && (
          <Box sx={{ mt: 3 }}>
            <Typography variant="subtitle1" gutterBottom>
              Selected Files ({files.length})
            </Typography>
            
            <List>
              {files.map((file, index) => {
                const status = uploadStatus[index];
                return (
                  <ListItem
                    key={index}
                    sx={{
                      border: 1,
                      borderColor: 'grey.200',
                      borderRadius: 1,
                      mb: 1,
                    }}
                  >
                    <ListItemIcon>
                      {getFileIcon(file)}
                    </ListItemIcon>
                    
                    <ListItemText
                      primary={file.name}
                      secondary={`${formatFileSize(file.size)} • ${file.type}`}
                    />
                    
                    {status && (
                      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, minWidth: 200 }}>
                        {status.status === 'uploading' && (
                          <Box sx={{ width: 120 }}>
                            <LinearProgress 
                              variant="determinate" 
                              value={status.progress || 0} 
                              sx={{ height: 6, borderRadius: 3 }}
                            />
                          </Box>
                        )}
                        {status.status === 'success' && <CheckCircle color="success" />}
                        {status.status === 'error' && <Error color="error" />}
                        <Typography variant="caption" color="text.secondary" sx={{ minWidth: 120 }}>
                          {status.message}
                        </Typography>
                      </Box>
                    )}
                    
                    <IconButton
                      onClick={() => removeFile(index)}
                      disabled={status?.status === 'uploading'}
                    >
                      <Delete />
                    </IconButton>
                  </ListItem>
                );
              })}
            </List>

            {/* Upload Button */}
            <Box sx={{ mt: 2, display: 'flex', gap: 2 }}>
              <Button
                variant="contained"
                onClick={uploadFiles}
                disabled={loading || isUploading || files.length === 0}
                startIcon={<CloudUpload />}
              >
                {loading || isUploading ? 'Uploading...' : 'Upload Files'}
              </Button>
              
              <Button
                variant="outlined"
                onClick={() => {
                  setFiles([]);
                  setUploadStatus({});
                }}
                disabled={loading || isUploading}
              >
                Clear All
              </Button>
            </Box>
          </Box>
        )}

        {/* Status Messages */}
        {Object.values(uploadStatus).map((status, index) => (
          status.status === 'error' && (
            <Alert key={index} severity="error" sx={{ mt: 2 }}>
              {status.message}
            </Alert>
          )
        ))}
      </CardContent>
    </Card>
  );
};

export default FileUpload;



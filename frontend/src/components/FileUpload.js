import React, { useState, useCallback, useEffect } from 'react';
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

const FileUpload = ({ 
  onUpload, 
  loading = false, 
  onUploadStateChange,
  globalUploadStatus = {},
  uploadFiles = [],
  onAddUploadFile,
  onUpdateUploadProgress,
  onRemoveUploadFile,
  onClearCompletedUploads
}) => {
  const [files, setFiles] = useState([]);
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
    const file = files[index];
    setFiles(prev => prev.filter((_, i) => i !== index));
    
    // Also remove from global state if it exists
    const uploadItem = uploadFiles.find(item => item.file.name === file.name && item.file.size === file.size);
    if (uploadItem && onRemoveUploadFile) {
      onRemoveUploadFile(uploadItem.id);
    }
  };

  const handleUploadFiles = async () => {
    if (files.length === 0) return;

    for (let i = 0; i < files.length; i++) {
      const file = files[i];
      const isAudioFile = file.type.startsWith('audio/');
      const uploadId = `${file.name}-${file.size}-${Date.now()}-${i}`;
      let simulationActive = true;
      
      // Add file to global upload tracking
      if (onAddUploadFile) {
        onAddUploadFile(file, uploadId);
      }

      try {
        let currentProgress = 0;
        
        const updateProgress = (progress, message) => {
          if (onUpdateUploadProgress) {
            onUpdateUploadProgress(uploadId, 'uploading', message, Math.min(progress, 95));
          }
        };

        // Start the actual upload first to get real progress
        const uploadPromise = onUpload(file, (progressData) => {
          if (progressData.type === 'upload' && simulationActive) {
            currentProgress = progressData.progress;
            updateProgress(currentProgress, progressData.message);
          }
        });

        // Wait a moment for upload to start, then continue with processing simulation
        setTimeout(() => {
          if (simulationActive && currentProgress >= 20) {
            if (isAudioFile) {
              updateProgress(30, 'Processing audio file...');
              
              const transcriptionInterval = setInterval(() => {
                if (!simulationActive) {
                  clearInterval(transcriptionInterval);
                  return;
                }
                currentProgress += 3;
                if (currentProgress <= 60) {
                  updateProgress(currentProgress, 'Transcribing audio with AI...');
                } else {
                  clearInterval(transcriptionInterval);
                  currentProgress = 65;
                  updateProgress(currentProgress, 'Detecting language...');
                  
                  setTimeout(() => {
                    if (simulationActive) {
                      currentProgress = 70;
                      updateProgress(currentProgress, 'Analyzing content...');
                      
                      setTimeout(() => {
                        if (simulationActive) {
                          currentProgress = 80;
                          updateProgress(currentProgress, 'Generating summary...');
                          
                          setTimeout(() => {
                            if (simulationActive) {
                              currentProgress = 90;
                              updateProgress(currentProgress, 'Extracting insights...');
                            }
                          }, 1000);
                        }
                      }, 1500);
                    }
                  }, 1000);
                }
              }, 800);
            } else {
              updateProgress(30, 'Reading text file...');
              
              setTimeout(() => {
                if (simulationActive) {
                  currentProgress = 50;
                  updateProgress(currentProgress, 'Detecting language...');
                  
                  setTimeout(() => {
                    if (simulationActive) {
                      currentProgress = 70;
                      updateProgress(currentProgress, 'Analyzing content...');
                      
                      setTimeout(() => {
                        if (simulationActive) {
                          currentProgress = 85;
                          updateProgress(currentProgress, 'Generating summary...');
                          
                          setTimeout(() => {
                            if (simulationActive) {
                              currentProgress = 90;
                              updateProgress(currentProgress, 'Extracting insights...');
                            }
                          }, 1000);
                        }
                      }, 1000);
                    }
                  }, 1000);
                }
              }, 500);
            }
          }
        }, 1000);

        const result = await uploadPromise;
        simulationActive = false;
        
        // Mark as completed in global state
        if (onUpdateUploadProgress) {
          onUpdateUploadProgress(uploadId, 'success', result.message || 'File processed successfully!', 100);
        }
        
      } catch (error) {
        simulationActive = false;
        if (onUpdateUploadProgress) {
          onUpdateUploadProgress(uploadId, 'error', error.message || 'Upload failed', 0);
        }
      }
    }

    // Clear the local files after initiating uploads
    setFiles([]);
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

  const isUploading = Object.values(globalUploadStatus).some(status => status.status === 'uploading');

  // Notify parent component when upload state changes
  useEffect(() => {
    if (onUploadStateChange) {
      onUploadStateChange(isUploading);
    }
  }, [isUploading, onUploadStateChange]);

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
            <br />
            <strong>Processing includes:</strong> Transcription, Language Detection, Summarization, Action Items, Key Decisions
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

        {/* File List - Show both local files and global upload status */}
        {(files.length > 0 || uploadFiles.length > 0) && (
          <Box sx={{ mt: 3 }}>
            <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
              <Typography variant="subtitle1">
                Files ({files.length} selected, {uploadFiles.length} uploading)
              </Typography>
              {uploadFiles.length > 0 && (
                <Button 
                  variant="outlined" 
                  size="small" 
                  onClick={onClearCompletedUploads}
                  disabled={isUploading}
                >
                  Clear Completed
                </Button>
              )}
            </Box>
            
            <List>
              {/* Show local files that haven't been uploaded yet */}
              {files.map((file, index) => (
                <ListItem
                  key={`local-${index}`}
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
                  
                  <IconButton
                    onClick={() => removeFile(index)}
                    disabled={isUploading}
                  >
                    <Delete />
                  </IconButton>
                </ListItem>
              ))}

              {/* Show files being uploaded with progress */}
              {uploadFiles.map((uploadItem) => {
                const status = globalUploadStatus[uploadItem.id];
                const file = uploadItem.file;
                
                return (
                  <ListItem
                    key={uploadItem.id}
                    sx={{
                      border: 1,
                      borderColor: status?.status === 'error' ? 'error.main' : 
                                   status?.status === 'success' ? 'success.main' : 'primary.main',
                      borderRadius: 1,
                      mb: 1,
                      bgcolor: status?.status === 'error' ? 'error.50' : 
                               status?.status === 'success' ? 'success.50' : 'primary.50',
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
                      onClick={() => onRemoveUploadFile && onRemoveUploadFile(uploadItem.id)}
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
                onClick={handleUploadFiles}
                disabled={loading || isUploading || files.length === 0}
                startIcon={<CloudUpload />}
              >
                {loading || isUploading ? 'Uploading...' : 'Upload Files'}
              </Button>
              
              <Button
                variant="outlined"
                onClick={() => {
                  setFiles([]);
                }}
                disabled={loading || isUploading}
              >
                Clear Selected
              </Button>
            </Box>
          </Box>
        )}

        {/* Status Messages */}
        {Object.values(globalUploadStatus).map((status, index) => (
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



# Troubleshooting Guide

Common issues and their solutions when running Polyglot Meeting Assistant.

## 🔧 Installation Issues

### "Permission denied" when running start.sh
**Problem**: Script doesn't have execute permissions.

**Solution**:
```bash
chmod +x start.sh
./start.sh
```

### Python/Node.js version issues
**Problem**: Incompatible versions installed.

**Check versions**:
```bash
python3 --version  # Should be 3.11+
node --version     # Should be 18+
npm --version      # Should be 8+
```

**Solutions**:
- **Python**: Use `pyenv` or download from [python.org](https://python.org)
- **Node.js**: Use `nvm` or download from [nodejs.org](https://nodejs.org)

### Virtual environment creation fails
**Problem**: `python3 -m venv venv` fails.

**Solution**:
```bash
# Install venv module (Ubuntu/Debian)
sudo apt-get install python3-venv

# Or use virtualenv
pip install virtualenv
virtualenv venv
```

## 🌐 Network & Port Issues

### Port already in use
**Problem**: Ports 3000 or 8000 are occupied.

**Find and kill processes**:
```bash
# Backend (port 8000)
lsof -ti:8000 | xargs kill -9

# Frontend (port 3000)  
lsof -ti:3000 | xargs kill -9

# Alternative: Find process ID
lsof -i :8000
kill -9 <PID>
```

**Use different ports**:
```bash
# Backend
PORT=8001 python backend/src/api.py

# Frontend
PORT=3001 npm start
```

### CORS errors in browser
**Problem**: Cross-origin request blocked.

**Check**:
1. Backend is running on port 8000
2. Frontend is running on port 3000
3. No proxy or firewall blocking requests

**Solution**: Backend should automatically allow localhost origins.

## 🎙️ Audio Processing Issues

### ffmpeg not found
**Problem**: Audio transcription fails with ffmpeg error.

**Install ffmpeg**:
```bash
# Ubuntu/Debian
sudo apt update && sudo apt install ffmpeg

# macOS (with Homebrew)
brew install ffmpeg

# Windows (with Chocolatey)
choco install ffmpeg
```

**Verify installation**:
```bash
ffmpeg -version
```

### Audio transcription fails
**Problem**: Uploaded audio files don't get transcribed.

**Debug steps**:
1. **Check file format**: Ensure file is MP3, WAV, M4A, or OGG
2. **Check file size**: Large files may timeout (check backend logs)
3. **Check audio quality**: Very poor quality may fail transcription
4. **Check backend logs**: Look for specific error messages

**Convert audio format**:
```bash
# Convert to supported format
ffmpeg -i input.mov -acodec mp3 output.mp3
```

### Large file uploads fail
**Problem**: Files over certain size fail to upload.

**Solutions**:
1. **Compress audio**:
   ```bash
   ffmpeg -i input.wav -b:a 128k output.mp3
   ```

2. **Split large files**:
   ```bash
   ffmpeg -i input.wav -f segment -segment_time 600 -c copy output%03d.wav
   ```

## 🔍 Search Issues

### Search returns no results
**Problem**: Queries don't return expected results.

**Debug checklist**:
1. **Files uploaded?**: Check if files were successfully processed
2. **Processing complete?**: Large files may still be processing
3. **Check backend logs**: Look for indexing errors
4. **Try simpler queries**: Start with basic keywords

**Clear search index** (if corrupted):
```bash
rm -rf backend/data/search_index/*
# Re-upload files to rebuild index
```

### Search is very slow
**Problem**: Queries take a long time to return results.

**Solutions**:
1. **Reduce search scope**: Use more specific queries
2. **Check system resources**: Ensure adequate RAM/CPU
3. **Restart services**: Sometimes helps with memory issues

## 🗄️ Database & Storage Issues

### Session data lost
**Problem**: Uploaded files disappear after restart.

**Check**:
- Files in `backend/uploads/` directory
- Session data in `backend/data/sessions/`

**Solution**: Ensure proper file permissions and storage paths.

### Disk space issues
**Problem**: Running out of storage space.

**Clean up**:
```bash
# Remove old uploads (be careful!)
find backend/uploads/ -type f -mtime +30 -delete

# Clear search index to rebuild
rm -rf backend/data/search_index/*
```

## 🐛 Development Issues

### Dependencies won't install
**Problem**: `pip install` or `npm install` fails.

**Python dependencies**:
```bash
# Update pip
python3 -m pip install --upgrade pip

# Use verbose mode to see errors
pip install -r requirements.txt -v

# Install individually if needed
pip install fastapi uvicorn
```

**Node.js dependencies**:
```bash
# Clear npm cache
npm cache clean --force

# Delete node_modules and reinstall
rm -rf node_modules package-lock.json
npm install
```

### Hot reload not working
**Problem**: Changes don't appear automatically.

**Solutions**:
- **Backend**: Make sure using `--reload` flag
- **Frontend**: Restart `npm start`
- **Clear browser cache**: Hard refresh (Ctrl+Shift+R)

### Import errors in Python
**Problem**: Module not found errors.

**Check PYTHONPATH**:
```bash
export PYTHONPATH="${PYTHONPATH}:$(pwd)/backend/src"
# Or
PYTHONPATH=backend/src python backend/src/api.py
```

## 🔒 Permission Issues

### File permission denied
**Problem**: Can't read/write files.

**Fix permissions**:
```bash
# Backend uploads directory
chmod -R 755 backend/uploads/
chmod -R 755 backend/data/

# Make scripts executable
chmod +x start.sh
```

### Docker permission issues
**Problem**: Docker commands fail with permission errors.

**Solutions**:
```bash
# Add user to docker group (Linux)
sudo usermod -aG docker $USER
# Log out and back in

# Or use sudo
sudo docker-compose up
```

## 🔧 Performance Issues

### High memory usage
**Problem**: Application uses too much RAM.

**Solutions**:
1. **Use smaller Whisper model**:
   ```python
   # In backend/src/models/asr.py
   model = whisper.load_model("tiny")  # Instead of "base" or "large"
   ```

2. **Limit concurrent uploads**: Process files one at a time

3. **Restart services periodically**: Clear memory leaks

### Slow transcription
**Problem**: Audio transcription takes very long.

**Optimize**:
1. **Use smaller Whisper model**: "tiny" or "base" instead of "large"
2. **Use GPU acceleration**: If CUDA available
3. **Pre-process audio**: Convert to optimal format first

## 🆘 Getting Help

### Enable Debug Logging
```bash
# Backend
DEBUG=true python backend/src/api.py

# Frontend  
REACT_APP_DEBUG=true npm start
```

### Check Log Files
- **Backend logs**: Console output when running API
- **Frontend logs**: Browser developer console (F12)
- **Network logs**: Browser Network tab for API calls

### Gather Debug Information
When reporting issues, include:

1. **Operating system and version**
2. **Python version** (`python3 --version`)
3. **Node.js version** (`node --version`)
4. **Error messages** (full stack traces)
5. **Steps to reproduce** the issue
6. **Expected vs actual behavior**

### Create GitHub Issue
Visit: [https://github.com/sgavriil01/polyglot-meeting-assistant/issues](https://github.com/sgavriil01/polyglot-meeting-assistant/issues)

Include debug information and follow the issue template.

---

**Still having issues?** Check the [Contributing Guide](../CONTRIBUTING.md) for more development help or create an issue on GitHub.

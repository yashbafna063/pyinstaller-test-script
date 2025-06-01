# PyQt Auto-Update Demo - Setup and Deployment Guide

This demo shows how to create a PyQt application with auto-update functionality and package it as an executable using PyInstaller.

## Project Structure

```
pyqt-autoupdate-demo/
├── main.py              # Main application file
├── build.py             # Build script
├── requirements.txt     # Python dependencies
├── README.md           # This file
├── dist/               # Built executables (created after build)
└── build/              # Build artifacts (created after build)
```

## Setup Instructions

### 1. Install Dependencies

```bash
# Create virtual environment (recommended)
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configure Update Server

Before building, update the `UPDATE_SERVER` constant in `main.py`:

```python
UPDATE_SERVER = "https://api.github.com/repos/yourusername/yourrepo/releases/latest"
```

Replace `yourusername/yourrepo` with your actual GitHub repository.

### 3. Build the Application

Run the build script:

```bash
python build.py
```

Choose build method:
- **Option 1 (Recommended)**: Uses a custom spec file for better control
- **Option 2**: Simple one-command build

The executable will be created in the `dist/` folder.

## Build Options Explained

### Spec File Method (Recommended)
- Creates a custom `.spec` file for fine-tuned control
- Excludes unnecessary packages to reduce file size
- Includes all required hidden imports
- Better for complex applications

### Simple Method
- Single PyInstaller command
- Good for quick testing
- May include unnecessary dependencies

## Auto-Update System

### How It Works

1. **Version Check**: App checks GitHub releases API on startup
2. **Download**: If newer version found, downloads the new executable
3. **Install**: Replaces current executable and restarts

### Setting Up GitHub Releases

1. **Create Repository**: Push your code to GitHub
2. **Create Release**: Go to Releases → Create a new release
3. **Version Tag**: Use semantic versioning (e.g., `v1.0.1`)
4. **Upload Asset**: Upload your built executable
5. **Publish**: Make the release public

### Release Asset Naming Convention

The update system looks for platform-specific files:
- **Windows**: Files ending with `.exe`
- **macOS**: Files containing `mac` in the name
- **Linux**: Files containing `linux` in the name

Example:
- `PyQtAutoUpdateDemo-v1.0.1-windows.exe`
- `PyQtAutoUpdateDemo-v1.0.1-macos.dmg`
- `PyQtAutoUpdateDemo-v1.0.1-linux.AppImage`

## Testing the Application

### 1. Test Locally
```bash
# Run from source
python main.py

# Test built executable
./dist/PyQtAutoUpdateDemo  # Linux/macOS
./dist/PyQtAutoUpdateDemo.exe  # Windows
```

### 2. Test Auto-Update

1. Build and run version 1.0.0
2. Create GitHub release with version 1.0.1
3. Upload new executable as release asset
4. Run the app and click "Check for Updates"

## Troubleshooting

### Common PyInstaller Issues

**Missing Modules Error**:
```bash
# Add hidden imports to spec file or build command
--hidden-import module_name
```

**Large File Size**:
```bash
# Exclude unnecessary packages
--exclude-module matplotlib
--exclude-module numpy
```

**Console Window Appears**:
```bash
# Use --windowed flag or set console=False in spec
--windowed
```

### Update System Issues

**SSL Certificate Errors**:
- Ensure `requests` and `certifi` are properly bundled
- May need to include SSL certificates manually

**Permission Errors**:
- On Windows, may need administrator privileges
- Consider using an installer instead of direct file replacement

**Network Issues**:
- Add timeout and retry logic
- Handle offline scenarios gracefully

## Advanced Features

### Code Signing (Production)

For production applications, sign your executables:

**Windows**:
```bash
signtool sign /f certificate.pfx /p password /t http://timestamp.url executable.exe
```

**macOS**:
```bash
codesign --sign "Developer ID Application: Your Name" --timestamp app.app
```

### Custom Updater

For more sophisticated updates, consider:
- Delta updates (only download changes)
- Background updates
- Rollback capability
- Progress indicators
- Update scheduling

### Packaging Alternatives

**Electron + Python**: Package Python as a backend service
**Docker**: Containerized deployment
**Web App**: Convert to web application with auto-refresh

## Deployment Checklist

- [ ] Update version number in `main.py`
- [ ] Configure correct GitHub repository URL
- [ ] Build and test executable locally
- [ ] Create GitHub release with proper version tag
- [ ] Upload platform-specific executables
- [ ] Test auto-update functionality
- [ ] Document release notes
- [ ] Notify users of new version

## Security Considerations

- Verify download integrity with checksums
- Use HTTPS for all update communications
- Validate version strings to prevent injection
- Consider code signing for production releases
- Implement update authentication if needed

## Performance Tips

- Cache version check results
- Use background threads for updates
- Compress executables with UPX
- Minimize startup time with lazy imports
- Profile the application to identify bottlenecks

This demo provides a solid foundation for building auto-updating PyQt applications. Customize it according to your specific needs and requirements.
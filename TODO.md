# CLI Issues Resolution

## ✅ Completed Issues

### 1. `dry_run` vs `skip_processing` Redundancy
- **FIXED**: Removed `skip_processing` parameter from Photo AI CLI method
- **CHANGE**: All `skip_processing` calls now use `self._options.dry_run` instead
- **RESULT**: Unified dry run behavior across the entire CLI

### 2. `autopilot_preset` Parameter Naming
- **FIXED**: Renamed `autopilot_preset` to `preset` in CLI method signature
- **FIXED**: Updated default value to `"auto"` in PhotoAIParams dataclass
- **RESULT**: Cleaner, more intuitive parameter name

### 3. `override_autopilot` Parameter Evaluation
- **KEPT**: This parameter is necessary for Photo AI functionality
- **PURPOSE**: Controls when to add the `--override` flag to Photo AI CLI commands
- **LOGIC**: Automatically activates when manual enhancement parameters are provided, but can also be explicitly set

### 4. Photo AI Preference Options
- **ADDED**: All 23 Photo AI autopilot preference options exposed as CLI parameters:
  - **Face Recovery**: `face_strength`, `face_detection`, `face_parts`
  - **Denoise**: `denoise_model`, `denoise_levels`, `denoise_strength`, `denoise_raw_*`
  - **Sharpen**: `sharpen_model`, `sharpen_levels`, `sharpen_strength`
  - **Upscaling**: `upscaling_model`, `upscaling_factor`, `upscaling_type`, `deblur_strength`, `denoise_upscale_strength`
  - **Lighting**: `lighting_strength`, `raw_exposure_strength`, `adjust_color`
  - **Color**: `temperature_value`, `opacity_value`
  - **Output**: `resolution_unit`, `default_resolution`
  - **Processing**: `overwrite_files`, `recurse_directories`, `append_filters`

## 🔧 Architecture Improvements

### 5. Shared CLI Parameters Architecture
- **FIXED**: Remote execution parameters moved back to `__init__` method (shared across all commands)
- **ADDED**: `remote_folder` parameter for specifying remote working directory
- **GLOBAL PARAMETERS**: `remote_host`, `remote_user`, `ssh_key`, `ssh_port`, `connection_timeout`, `remote_folder`
- **RATIONALE**: These parameters are shared across all commands and should be configured once

### 6. Remote File Path Coordination System
- **IDENTIFIED**: Critical gap in remote execution architecture
- **PROBLEM**: Local paths vs remote paths - how to coordinate file transfers and path translation
- **EXISTING INFRASTRUCTURE**: RemoteExecutor already has `upload_file()` and `download_file()` methods

## 🚧 Remaining Work: Remote File Transfer Architecture

### Current Issue
When executing Topaz tools remotely:
```bash
# User runs locally with local paths
topyaz photo /local/path/input.jpg --remote_host=server.com

# But Topaz tool on remote server expects remote paths
# /local/path/input.jpg doesn't exist on remote server!
```

### Required Solution Architecture
1. **File Upload Phase**:
   - Upload local input files to `remote_folder` on remote server
   - Generate unique remote paths to avoid conflicts

2. **Path Translation Phase**:
   - Convert local input/output paths to remote equivalents
   - Build Topaz commands using remote paths

3. **Remote Execution Phase**:
   - Execute Topaz tool with remote paths
   - Tool processes files on remote server

4. **File Download Phase**:
   - Download processed files back to local output paths
   - Clean up temporary remote files

### Implementation Plan

```python
class RemoteFileManager:
    \"\"\"Handles file transfers and path coordination for remote execution.\"\"\"
    
    def __init__(self, remote_executor: RemoteExecutor, remote_folder: str):
        self.executor = remote_executor
        self.remote_folder = remote_folder
        self.session_id = uuid.uuid4().hex[:8]
        
    def upload_input_files(self, local_paths: list[Path]) -> dict[Path, str]:
        \"\"\"Upload files and return local->remote path mapping.\"\"\"
        
    def download_output_files(self, remote_outputs: list[str], local_output_dir: Path):
        \"\"\"Download processed files to local paths.\"\"\"
        
    def translate_paths(self, command: list[str], path_mapping: dict) -> list[str]:
        \"\"\"Replace local paths in command with remote paths.\"\"\"
        
    def cleanup_remote_files(self):
        \"\"\"Clean up temporary files on remote server.\"\"\"
```

### Integration Points
- **Products** (Photo AI, Video AI, Gigapixel AI): Need to use RemoteFileManager when using RemoteExecutor
- **CLI Commands**: Should be transparent to user - just specify remote options
- **File Handling**: Automatic upload/download with progress indicators

## Current CLI Status
✅ All original issues resolved
✅ Photo AI has comprehensive preference control  
✅ Shared parameters properly architected
✅ Remote execution infrastructure exists
⚠️ **CRITICAL**: Remote file transfer coordination needs implementation

## Next Steps
1. **Implement RemoteFileManager class**
2. **Integrate with Product classes** (modify base MacOSTopazProduct)
3. **Add progress indicators** for file transfers
4. **Add cleanup mechanisms** for failed transfers
5. **Test end-to-end remote processing workflows**

This architectural improvement will make remote execution fully functional and production-ready.
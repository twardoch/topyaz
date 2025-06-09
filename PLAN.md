# Remote File Coordination Implementation Plan for topyaz

## Executive Summary

**topyaz** has a robust SSH remote execution foundation but lacks the critical file coordination layer needed for practical remote processing. Users can specify `--remote_host` but commands fail because local file paths don't exist on remote servers.

**Core Issue**: When executing `topyaz photo /local/input.jpg --remote_host=server.com`, the command attempts to process `/local/input.jpg` on the remote server where this path doesn't exist.

**Solution**: Implement a transparent file coordination system that handles upload, path translation, execution, and download automatically.

## Current Architecture Analysis

### Strengths
- **Solid SSH Foundation**: `RemoteExecutor` class with connection pooling
- **Complete Parameter System**: All Topaz product parameters properly exposed
- **Clean Abstraction**: Products inherit from `MacOSTopazProduct` base class
- **Proper Error Handling**: Authentication, connection, and execution errors handled
- **Type Safety**: Full type hints with dataclasses for all configurations

### The Missing Piece
The `RemoteExecutor.execute()` method receives command lists with local paths and executes them directly on remote servers. No path translation or file coordination occurs.

```python
# Current flow (BROKEN):
command = ["tpai", "/Users/adam/input.jpg", "-o", "/Users/adam/output.jpg"]
remote_executor.execute(command)  # Fails - paths don't exist on remote server

# Required flow:
# 1. Upload /Users/adam/input.jpg → /tmp/topyaz_session/input.jpg
# 2. Translate command: ["tpai", "/tmp/topyaz_session/input.jpg", "-o", "/tmp/topyaz_session/output.jpg"] 
# 3. Execute translated command on remote server
# 4. Download /tmp/topyaz_session/output.jpg → /Users/adam/output.jpg
```

## Implementation Strategy

### Phase 1: Core File Coordination (2-3 days)

#### 1.1 Create RemoteFileCoordinator Class

```python
# src/topyaz/execution/coordination.py
from dataclasses import dataclass
from pathlib import Path
import uuid
import time

@dataclass
class RemoteSession:
    """Represents a remote processing session with file mappings."""
    session_id: str
    remote_base_dir: str
    local_to_remote: dict[str, str]  # Local path → Remote path
    remote_to_local: dict[str, str]  # Remote path → Local path
    created_at: float = field(default_factory=time.time)

class RemoteFileCoordinator:
    """Coordinates file transfers and path translation for remote execution."""
    
    def __init__(self, remote_executor: RemoteExecutor, base_dir: str = "/tmp/topyaz"):
        self.executor = remote_executor
        self.base_dir = base_dir
        
    def execute_with_files(self, command: list[str]) -> tuple[int, str, str]:
        """Execute command with automatic file coordination."""
        session = self._create_session()
        try:
            # 1. Detect files in command
            input_files, output_files = self._detect_files(command)
            
            # 2. Upload input files
            for local_path in input_files:
                remote_path = f"{session.remote_base_dir}/{Path(local_path).name}"
                self.executor.upload_file(local_path, remote_path)
                session.local_to_remote[local_path] = remote_path
                session.remote_to_local[remote_path] = local_path
            
            # 3. Map output files (no upload needed)
            for local_path in output_files:
                remote_path = f"{session.remote_base_dir}/{Path(local_path).name}"
                session.local_to_remote[local_path] = remote_path
                session.remote_to_local[remote_path] = local_path
            
            # 4. Translate command paths
            translated_command = self._translate_command(command, session.local_to_remote)
            
            # 5. Execute on remote
            exit_code, stdout, stderr = self.executor.execute(translated_command)
            
            # 6. Download output files if successful
            if exit_code == 0:
                for local_path in output_files:
                    remote_path = session.local_to_remote[local_path]
                    self.executor.download_file(remote_path, local_path)
            
            return exit_code, stdout, stderr
            
        finally:
            self._cleanup_session(session)
    
    def _create_session(self) -> RemoteSession:
        """Create unique remote session directory."""
        session_id = f"topyaz_{int(time.time())}_{uuid.uuid4().hex[:8]}"
        remote_dir = f"{self.base_dir}/sessions/{session_id}"
        
        # Create session directory on remote
        self.executor.execute(["mkdir", "-p", remote_dir])
        
        return RemoteSession(
            session_id=session_id,
            remote_base_dir=remote_dir,
            local_to_remote={},
            remote_to_local={}
        )
```

#### 1.2 Path Detection Logic

```python
def _detect_files(self, command: list[str]) -> tuple[list[str], list[str]]:
    """Detect input and output files in command arguments."""
    input_files = []
    output_files = []
    
    for i, arg in enumerate(command):
        if self._is_file_path(arg):
            prev_arg = command[i-1] if i > 0 else ""
            
            # Output file detection
            if prev_arg in ["-o", "--output"]:
                output_files.append(arg)
            # Input file detection (positional or after input flags)
            elif prev_arg in ["-i", "--input"] or (not prev_arg.startswith("-") and Path(arg).exists()):
                input_files.append(arg)
    
    return input_files, output_files

def _is_file_path(self, arg: str) -> bool:
    """Check if argument looks like a file path."""
    # Simple heuristic: has file extension or exists as path
    return ("." in arg and "/" in arg) or Path(arg).exists()
```

#### 1.3 Integration with Product Classes

Modify `MacOSTopazProduct.process()` to use file coordination:

```python
# src/topyaz/products/base.py
def process(self, input_path: Path | str, output_path: Path | str | None = None, **kwargs) -> ProcessingResult:
    # ... existing validation code ...
    
    command = self.build_command(input_path, final_output_path, **kwargs)
    
    # NEW: Use file coordination for remote execution
    if isinstance(self.executor, RemoteExecutor):
        from topyaz.execution.coordination import RemoteFileCoordinator
        coordinator = RemoteFileCoordinator(
            self.executor, 
            self._options.remote_folder or "/tmp/topyaz"
        )
        exit_code, stdout, stderr = coordinator.execute_with_files(command)
    else:
        # Local execution unchanged
        exit_code, stdout, stderr = self.executor.execute(command, timeout=self._options.timeout)
    
    # ... rest of processing unchanged ...
```

### Phase 2: Robustness & Error Recovery (1-2 days)

#### 2.1 Enhanced Error Handling

```python
class RemoteFileCoordinator:
    def execute_with_files(self, command: list[str]) -> tuple[int, str, str]:
        session = self._create_session()
        try:
            # Upload with retry logic
            for local_path in input_files:
                remote_path = f"{session.remote_base_dir}/{Path(local_path).name}"
                self._upload_with_retry(local_path, remote_path, max_retries=3)
                
            # ... execution ...
            
            # Download with integrity checks
            if exit_code == 0:
                for local_path in output_files:
                    remote_path = session.local_to_remote[local_path]
                    self._download_with_verification(remote_path, local_path)
            
        except Exception as e:
            logger.error(f"Remote coordination failed: {e}")
            return 1, "", str(e)
        finally:
            self._cleanup_session(session)
```

#### 2.2 File Transfer with Progress

```python
def _upload_with_retry(self, local_path: str, remote_path: str, max_retries: int = 3) -> None:
    """Upload file with retry logic and progress."""
    for attempt in range(max_retries):
        try:
            # Use rsync if available for better performance
            if self._has_rsync():
                self._rsync_upload(local_path, remote_path)
            else:
                self.executor.upload_file(local_path, remote_path)
            
            # Verify transfer integrity
            if self._verify_transfer(local_path, remote_path):
                return
                
        except Exception as e:
            if attempt == max_retries - 1:
                raise
            time.sleep(2 ** attempt)  # Exponential backoff

def _verify_transfer(self, local_path: str, remote_path: str) -> bool:
    """Verify file transfer integrity using checksums."""
    import hashlib
    
    # Local checksum
    with open(local_path, 'rb') as f:
        local_hash = hashlib.sha256(f.read()).hexdigest()
    
    # Remote checksum
    exit_code, stdout, _ = self.executor.execute(["sha256sum", remote_path])
    if exit_code != 0:
        return False
    
    remote_hash = stdout.strip().split()[0]
    return local_hash == remote_hash
```

### Phase 3: Advanced Features (1-2 days)

#### 3.1 Intelligent Caching

```python
class RemoteFileCoordinator:
    def __init__(self, remote_executor: RemoteExecutor, base_dir: str = "/tmp/topyaz"):
        self.executor = remote_executor
        self.base_dir = base_dir
        self.cache_dir = f"{base_dir}/cache"
        
    def _get_cached_path(self, local_path: str) -> str | None:
        """Check if file already exists in cache."""
        file_hash = self._calculate_hash(local_path)
        cached_path = f"{self.cache_dir}/{file_hash}/{Path(local_path).name}"
        
        # Check if cached file exists
        exit_code, _, _ = self.executor.execute(["test", "-f", cached_path])
        return cached_path if exit_code == 0 else None
```

#### 3.2 Parallel Transfers

```python
import asyncio
from concurrent.futures import ThreadPoolExecutor

class RemoteFileCoordinator:
    async def _upload_files_parallel(self, file_pairs: list[tuple[str, str]]) -> None:
        """Upload multiple files in parallel."""
        with ThreadPoolExecutor(max_workers=4) as executor:
            tasks = [
                asyncio.get_event_loop().run_in_executor(
                    executor, self._upload_with_retry, local, remote
                )
                for local, remote in file_pairs
            ]
            await asyncio.gather(*tasks)
```

## Testing Strategy

### Unit Tests
```python
# tests/test_remote_coordination.py
class TestRemoteFileCoordinator:
    def test_file_detection(self):
        command = ["tpai", "input.jpg", "-o", "output.jpg"]
        coordinator = RemoteFileCoordinator(mock_executor)
        inputs, outputs = coordinator._detect_files(command)
        assert inputs == ["input.jpg"]
        assert outputs == ["output.jpg"]
    
    def test_path_translation(self):
        command = ["tpai", "input.jpg", "-o", "output.jpg"]
        mapping = {"input.jpg": "/remote/input.jpg", "output.jpg": "/remote/output.jpg"}
        translated = coordinator._translate_command(command, mapping)
        assert translated == ["tpai", "/remote/input.jpg", "-o", "/remote/output.jpg"]
```

### Integration Tests
```python
def test_end_to_end_photo_processing(mock_ssh_server):
    """Test complete workflow with mock SSH server."""
    # Setup test files
    test_input = create_test_image("test.jpg")
    
    # Execute remote processing
    result = topyaz.photo(
        test_input,
        remote_host="localhost",
        remote_user="test"
    )
    
    assert result.success
    assert result.output_path.exists()
```

## Implementation Timeline

### Week 1: Core Implementation
- [x] Day 1-2: Implement `RemoteFileCoordinator` with basic file detection
- [x] Day 3: Add path translation and session management  
- [x] Day 4-5: Integrate with product classes and test basic workflow

### Week 2: Robustness
- [ ] Day 1-2: Add error handling, retry logic, and cleanup guarantees
- [ ] Day 3: Implement transfer verification and progress reporting
- [ ] Day 4-5: Comprehensive testing and edge case handling

### Week 3: Polish
- [ ] Day 1-2: Add caching and parallel transfer optimizations
- [ ] Day 3: Performance testing and bandwidth management
- [ ] Day 4-5: Documentation and production deployment preparation

## Success Criteria

**Minimum Viable Product (End of Week 1)**:
```bash
# These commands should work reliably:
topyaz photo input.jpg --remote_host=server.com
topyaz giga image.png --scale 4 --remote_host=server.com --remote_user=admin
```

**Production Ready (End of Week 3)**:
- Handles network interruptions gracefully
- Automatic cleanup on all failure modes  
- Transfer verification with integrity checks
- Progress reporting for large files
- Caching for repeated processing
- 90%+ test coverage

## Risk Mitigation

**Network Failures**: Implement exponential backoff with configurable retry limits
**Partial Transfers**: Use atomic operations (upload to `.tmp`, then rename)
**Session Cleanup**: Always-execute cleanup with signal handling for crashes
**Security**: Validate all paths to prevent directory traversal attacks
**Performance**: Use rsync when available, parallel transfers for multiple files

This plan leverages topyaz's excellent existing architecture while solving the critical path coordination problem with a focused, incremental approach that can be deployed and tested step-by-step.
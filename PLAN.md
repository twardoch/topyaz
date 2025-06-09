# topyaz Refactoring Plan

**Status: ✅ COMPLETED - All 4 Phases Successfully Executed**

- ✅ **Phase 1: Simplification and Fluff Removal** - COMPLETED
- ✅ **Phase 2: Consolidate Product Processing Logic** - COMPLETED 
- ✅ **Phase 3: Isolate Photo AI Preferences** - COMPLETED
- ✅ **Phase 4: Enhance Robustness and Final Cleanup** - COMPLETED

**Results:**
- Removed obsolete monolithic file (1750+ lines)
- Simplified logging subsystem 
- Removed complex progress reporting
- Implemented Template Method pattern for product processing
- Centralized file type validation
- Enhanced preferences context manager
- Cleaned up CLI interface

**Estimated Complexity Reduction: 35-40%** ✅ ACHIEVED

---

# Topyaz Refactoring Plan: Simplification and Cognitive Load Reduction

## Overview

This plan refactors the topyaz codebase to remove unnecessary complexity ("fluff") while preserving core functionality. The goal is to create a lean, focused tool that processes files efficiently with minimal cognitive overhead.

## Phase 1: Simplification and Fluff Removal

### Step 1.1: Remove Obsolete Monolithic File ✅ CRITICAL

**Files to Delete:**
- `src/topyaz/topyaz.py` (1750+ lines of old monolithic code)
- `tests/test_package.py` (tests the old structure)

**Actions:**
1. Delete `src/topyaz/topyaz.py` entirely
2. Delete `tests/test_package.py` entirely
3. Update `src/topyaz/__init__.py` to remove any imports from `topyaz.topyaz`
4. Verify no other files import from the deleted module

**Validation:**
- Run `python -m pytest` to ensure no import errors
- Check that CLI still works: `python -m topyaz --help`

### Step 1.2: Simplify Logging Subsystem ✅ HIGH PRIORITY

**File: `src/topyaz/utils/logging.py`**

**Current Problem:** Complex LoggingManager class with multiple formatters, handlers, file rotation
**Solution:** Replace with simple setup function

**Actions:**
1. Replace entire content of `src/topyaz/utils/logging.py` with:

```python
#!/usr/bin/env python3
# this_file: src/topyaz/utils/logging.py
"""
Simplified logging setup for topyaz.
"""

import sys
from loguru import logger


def setup_logging(verbose: bool = True) -> None:
    """
    Configure logging for topyaz.
    
    Args:
        verbose: If True, use DEBUG level, otherwise INFO
    """
    logger.remove()
    log_level = "DEBUG" if verbose else "INFO"
    log_format = (
        "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
        "<level>{level: <8}</level> | "
        "<cyan>{name}:{function}:{line}</cyan> - <level>{message}</level>"
    )
    logger.add(sys.stderr, format=log_format, level=log_level, colorize=True)
    logger.info(f"Logging configured at {log_level} level.")


# Re-export logger for convenience
__all__ = ["logger", "setup_logging"]
```

**File: `src/topyaz/utils/__init__.py`**
2. Update imports to remove LoggingManager and ProgressLogger:

```python
from topyaz.utils.logging import logger, setup_logging
from topyaz.utils.validation import compare_media_files, enhance_processing_result, validate_output_file

__all__ = [
    "compare_media_files",
    "enhance_processing_result", 
    "logger",
    "setup_logging",
    "validate_output_file",
]
```

**File: `src/topyaz/cli.py`**
3. Replace LoggingManager usage:
   - Remove import: `from topyaz.utils.logging import LoggingManager`
   - Add import: `from topyaz.utils.logging import setup_logging`
   - In `TopyazCLI.__init__`, replace:
     ```python
     # Remove this:
     self.logging_manager = LoggingManager()
     self.logging_manager.setup(verbose=verbose)
     
     # Add this:
     setup_logging(verbose=verbose)
     ```

### Step 1.3: Remove Complex Progress Reporting ✅ HIGH PRIORITY

**File to Delete:**
- `src/topyaz/execution/progress.py` (entire file)

**File: `src/topyaz/execution/__init__.py`**
1. Remove progress-related imports:
```python
from topyaz.execution.base import CommandExecutor, ExecutorContext
from topyaz.execution.local import LocalExecutor
from topyaz.execution.remote import RemoteConnectionPool, RemoteExecutor, get_remote_executor, return_remote_executor

__all__ = [
    # Base interfaces
    "CommandExecutor",
    "ExecutorContext", 
    # Local execution
    "LocalExecutor",
    # Remote execution
    "RemoteConnectionPool",
    "RemoteExecutor",
    "get_remote_executor",
    "return_remote_executor",
]
```

**File: `src/topyaz/execution/base.py`**
2. Remove progress classes and simplify:
   - Delete `ProgressCallback` class entirely
   - Delete `ProgressAwareExecutor` class entirely
   - In `CommandExecutor`, remove `supports_progress()` method
   - Keep only `CommandExecutor` and `ExecutorContext` classes

**File: `src/topyaz/execution/local.py`**
3. Simplify LocalExecutor:
   - Change inheritance: `class LocalExecutor(CommandExecutor):` (not ProgressAwareExecutor)
   - Delete `execute_with_progress` method entirely
   - Delete `_extract_progress` method entirely  
   - Delete `SimpleProgressCallback` class entirely
   - Delete `QuietProgressCallback` class entirely
   - Keep only the basic `execute` method

**File: `src/topyaz/execution/remote.py`**
4. Simplify RemoteExecutor:
   - Change inheritance: `class RemoteExecutor(CommandExecutor):` (not ProgressAwareExecutor)
   - Delete `execute_with_progress` method entirely
   - Keep only the basic `execute` method

## Phase 2: Consolidate Product Processing Logic

### Step 2.1: Implement Template Method in TopazProduct ✅ MEDIUM PRIORITY

**Problem:** Duplication in `process` methods across gigapixel.py and photo_ai.py
**Solution:** Move common logic to base class using Template Method pattern

**File: `src/topyaz/products/base.py`**

1. Add new abstract method to `TopazProduct`:
```python
@abstractmethod
def _find_output_file(self, temp_dir: Path, input_path: Path) -> Path:
    """
    Find the generated output file within a temporary directory.
    This must be implemented by subclasses that use the temp dir workflow.
    
    Args:
        temp_dir: Temporary directory where output was generated
        input_path: Original input file path
        
    Returns:
        Path to the generated output file
        
    Raises:
        ProcessingError: If output file cannot be found
    """
    pass
```

2. Replace the abstract `process` method with a concrete template method:
```python
def process(self, input_path: Path | str, output_path: Path | str | None = None, **kwargs) -> ProcessingResult:
    """
    Template method for processing files. Uses temporary directory workflow.
    Override this method only if you need different behavior (like VideoAI).
    """
    # Convert to Path objects
    input_path = Path(input_path)
    if output_path:
        output_path = Path(output_path)

    # Validate inputs
    self.validate_input_path(input_path)
    self.validate_params(**kwargs)

    # Determine final output path  
    if output_path:
        final_output_path = self.path_validator.validate_output_path(output_path)
    else:
        output_dir = input_path.parent
        suffix = self._get_output_suffix()
        stem = input_path.stem
        extension = input_path.suffix
        output_filename = f"{stem}{suffix}{extension}"
        final_output_path = output_dir / output_filename

    # Ensure executable is available
    self.get_executable_path()

    # Create temporary directory for processing
    with tempfile.TemporaryDirectory(prefix=f"topyaz_{self.product_type.value}_") as temp_dir:
        temp_output_dir = Path(temp_dir)

        # Build command with temp directory
        command = self.build_command(input_path, temp_output_dir, **kwargs)

        try:
            logger.info(f"Processing {input_path} with {self.product_name}")

            if self.options.dry_run:
                logger.info(f"DRY RUN: Would execute: {' '.join(command)}")
                return ProcessingResult(
                    success=True,
                    input_path=input_path,
                    output_path=final_output_path,
                    command=command,
                    stdout="DRY RUN - no output",
                    stderr="",
                    execution_time=0.0,
                    file_size_before=0,
                    file_size_after=0,
                )

            import time
            start_time = time.time()
            file_size_before = input_path.stat().st_size if input_path.is_file() else 0

            # Execute the command
            exit_code, stdout, stderr = self.executor.execute(command, timeout=self.options.timeout)
            execution_time = time.time() - start_time

            # Check if processing was successful
            if exit_code != 0:
                error_msg = f"{self.product_name} processing failed (exit code {exit_code})"
                if stderr:
                    error_msg += f": {stderr}"
                return ProcessingResult(
                    success=False,
                    input_path=input_path,
                    output_path=final_output_path,
                    command=command,
                    stdout=stdout,
                    stderr=stderr,
                    execution_time=execution_time,
                    file_size_before=file_size_before,
                    file_size_after=0,
                    error_message=error_msg,
                )

            # Find the generated file using subclass-specific logic
            temp_output_file = self._find_output_file(temp_output_dir, input_path)

            # Ensure output directory exists and move file to final location
            final_output_path.parent.mkdir(parents=True, exist_ok=True)
            shutil.move(str(temp_output_file), str(final_output_path))

            # Get file size after processing
            file_size_after = final_output_path.stat().st_size if final_output_path.exists() else 0

            # Parse output for additional information
            parsed_info = self.parse_output(stdout, stderr)

            logger.info(f"Successfully processed {input_path} -> {final_output_path} in {execution_time:.2f}s")

            result = ProcessingResult(
                success=True,
                input_path=input_path,
                output_path=final_output_path,
                command=command,
                stdout=stdout,
                stderr=stderr,
                execution_time=execution_time,
                file_size_before=file_size_before,
                file_size_after=file_size_after,
                additional_info=parsed_info,
            )

            return result

        except Exception as e:
            logger.error(f"Error processing {input_path} with {self.product_name}: {e}")
            return ProcessingResult(
                success=False,
                input_path=input_path,
                output_path=final_output_path,
                command=command,
                stdout="",
                stderr=str(e),
                execution_time=0.0,
                file_size_before=0,
                file_size_after=0,
                error_message=str(e),
            )
```

**File: `src/topyaz/products/gigapixel.py`**

3. Update GigapixelAI class:
   - Delete the entire `process` method (base class will handle it)
   - Change `build_command` parameter: `temp_output_dir: Path` instead of `output_path: Path`
   - Add `_find_output_file` implementation:
   
```python
def _find_output_file(self, temp_dir: Path, input_path: Path) -> Path:
    """Find Gigapixel AI output file in temporary directory."""
    # Look for image files in temp directory
    image_files = list(temp_dir.glob("*"))
    image_files = [f for f in image_files if f.suffix.lower() in [".jpg", ".jpeg", ".png", ".tiff", ".tif"]]
    
    if not image_files:
        error_msg = f"No output files found in temporary directory {temp_dir}"
        logger.error(error_msg)
        raise ProcessingError(error_msg)
    
    # Use the first (and likely only) generated image file
    return image_files[0]
```

**File: `src/topyaz/products/photo_ai.py`**

4. Update PhotoAI class:
   - Delete the `_process_standard` method (base class handles this now)
   - Change `build_command` parameter: `temp_output_dir: Path` instead of `output_path: Path`  
   - Add `_find_output_file` implementation:

```python
def _find_output_file(self, temp_dir: Path, input_path: Path) -> Path:
    """Find Photo AI output file in temporary directory."""
    stem = input_path.stem
    ext = input_path.suffix
    
    # Look for exact filename first
    exact_file = temp_dir / input_path.name
    if exact_file.exists():
        return exact_file
    
    # Look for files with suffix pattern (stem-1.ext, stem-2.ext, etc)
    pattern = f"{stem}*{ext}"
    matching_files = list(temp_dir.glob(pattern))
    
    if matching_files:
        # Get the most recently modified file
        return max(matching_files, key=lambda f: f.stat().st_mtime)
    
    error_msg = f"No output files found in temporary directory {temp_dir}"
    logger.error(error_msg)
    raise ProcessingError(error_msg)
```

**File: `src/topyaz/products/video_ai.py`**

5. VideoAI keeps its current `process` method (no temp directory needed):
   - Add comment explaining why it overrides the base method
   - No changes to existing implementation needed

## Phase 3: Isolate and Refine Photo AI Preferences

### Step 3.1: Improve Preferences Context Manager ✅ LOW PRIORITY

**File: `src/topyaz/system/preferences.py`**

1. Update `PreferenceHandler` to be a proper context manager:

```python
def __enter__(self):
    """Context manager entry - create backup."""
    self._backup_id_for_context = self.backup()
    return self

def __exit__(self, exc_type, exc_val, exc_tb):
    """Context manager exit - restore from backup."""
    if hasattr(self, '_backup_id_for_context'):
        self.restore(self._backup_id_for_context)
    self.cleanup_all_backups()
```

**File: `src/topyaz/products/photo_ai.py`**

2. Simplify preferences usage in `_process_with_preferences`:

```python
def _process_with_preferences(self, input_path: Path, final_output_path: Path, **kwargs) -> ProcessingResult:
    """Process with preferences manipulation for enhanced autopilot control."""
    try:
        from topyaz.system.photo_ai_prefs import PhotoAIPreferences
        
        autopilot_settings = self._build_autopilot_settings(**kwargs)
        
        # Use preferences as context manager
        with PhotoAIPreferences() as prefs:
            prefs.update_autopilot_settings(autopilot_settings)
            logger.info("Applied enhanced autopilot settings")
            
            # Call the base class process method (after Phase 2 changes)
            return super().process(input_path, final_output_path, **kwargs)
            
    except ImportError:
        logger.warning("Preferences system not available - using standard processing")
        return super().process(input_path, final_output_path, **kwargs)
    except Exception as e:
        logger.error(f"Error in preferences manipulation: {e}")
        return super().process(input_path, final_output_path, **kwargs)
```

## Phase 4: Enhance Robustness and Final Cleanup

### Step 4.1: Strengthen Input Validation ✅ LOW PRIORITY

**File: `src/topyaz/system/paths.py`**

1. Enhance `PathValidator.validate_input_path` method:

```python
def validate_input_path(self, path: str | Path, must_exist: bool = True, file_type: Product | None = None) -> Path:
    """Validate and normalize input path with file type checking."""
    # ... existing path validation code ...
    
    # Validate file extension if checking a file
    if path_obj.is_file() and file_type:
        ext = path_obj.suffix.lower()
        
        if file_type == Product.VIDEO_AI:
            supported_extensions = self.VIDEO_EXTENSIONS
        else:
            supported_extensions = self.IMAGE_EXTENSIONS.get(file_type, set())

        if ext not in supported_extensions:
            msg = f"Unsupported file type '{ext}' for {file_type.value}. Supported: {', '.join(sorted(supported_extensions))}"
            raise ValidationError(msg)
    
    return path_obj
```

**File: `src/topyaz/products/base.py`**

2. Simplify `validate_input_path` method:

```python
def validate_input_path(self, input_path: Path) -> None:
    """Validate input path for this product."""
    self.path_validator.validate_input_path(input_path, file_type=self.product_type)
```

3. Remove `supported_formats` property from all product subclasses (centralized in PathValidator now)

### Step 4.2: Clean Up CLI Interface ✅ LOW PRIORITY

**File: `src/topyaz/cli.py`**

1. Remove diagnostic methods (move to future `topyaz diagnose` command):
   - Delete `system_info()` method
   - Delete `validate_environment()` method  
   - Delete `get_optimal_batch_size()` method
   - Delete `version_info()` method

2. Keep only core processing methods:
   - `gp()` - Gigapixel processing
   - `video()` - Video AI processing
   - `photo()` - Photo AI processing

3. Simplify initialization by removing system managers:
   - Remove `self.env_validator`
   - Remove `self.gpu_manager` 
   - Remove `self.memory_manager`
   - Keep only `self.config`, `self.executor`, and product instances

## Implementation Order and Testing

### Phase 1 Implementation Order:
1. Step 1.1 (Remove obsolete files) - CRITICAL
2. Step 1.2 (Simplify logging) - HIGH
3. Step 1.3 (Remove progress) - HIGH

### Phase 2 Implementation Order:
1. Step 2.1 (Template method) - MEDIUM

### Phase 3 Implementation Order:
1. Step 3.1 (Preferences context) - LOW

### Phase 4 Implementation Order:
1. Step 4.1 (Input validation) - LOW
2. Step 4.2 (CLI cleanup) - LOW

### Testing Strategy:
After each phase:
1. Run `python -m pytest tests/`
2. Test CLI commands: `python -m topyaz gp --help`, `python -m topyaz video --help`, `python -m topyaz photo --help`
3. Test dry run: `python -m topyaz gp testdata/man.jpg --dry-run`
4. Verify imports work: `python -c "import topyaz; print('OK')"`

### Validation Criteria:
- All tests pass
- CLI commands work as before
- Core functionality preserved
- Code is simpler and more focused
- Cognitive load reduced
- Shared code properly centralized

### Files to Update Summary:

**Delete:**
- `src/topyaz/topyaz.py`
- `tests/test_package.py` 
- `src/topyaz/execution/progress.py`

**Major Updates:**
- `src/topyaz/utils/logging.py` (complete rewrite)
- `src/topyaz/execution/base.py` (remove progress classes)
- `src/topyaz/execution/local.py` (simplify)
- `src/topyaz/execution/remote.py` (simplify)
- `src/topyaz/products/base.py` (add template method)
- `src/topyaz/products/gigapixel.py` (remove process method)
- `src/topyaz/products/photo_ai.py` (remove process method)
- `src/topyaz/cli.py` (remove logging manager, remove diagnostic methods)

**Minor Updates:**
- `src/topyaz/utils/__init__.py` (update imports)
- `src/topyaz/execution/__init__.py` (update imports)  
- `src/topyaz/system/preferences.py` (context manager)
- `src/topyaz/system/paths.py` (validation)

This plan removes approximately 30-40% of the current complexity while preserving all core functionality.


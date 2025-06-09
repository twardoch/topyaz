
# Plan for refactoring 

## Preliminary analysis

### **High-Level Refactoring Goals**

1.  **Simplify & De-clutter:** Remove non-essential "fluff" like complex logging, progress bars, and detailed system monitoring to focus on the core task of processing files.
2.  **Consolidate & Reduce Duplication:** Centralize common logic from the individual `products` modules into the `products/base.py` abstract class using the Template Method pattern.
3.  **Isolate Complex Subsystems:** Decouple the complex macOS `.plist` manipulation for Photo AI into a dedicated, self-contained component to improve clarity and testability.
4.  **Enhance Clarity & Robustness:** Improve input validation and error handling to make the application more resilient and predictable.

---

### **Phase 1: Simplification and Fluff Removal**

This phase focuses on removing components that add complexity without being essential to the core processing workflow.

#### **Step 1.1: Remove Obsolete Monolithic File**
The file `src/topyaz/topyaz.py` is the old monolithic version and is no longer used by the modular architecture. It must be removed.

*   **Action:** Delete the file `src/topyaz/topyaz.py`.
*   **Action:** Delete the test file `tests/test_package.py`, as it primarily tests the old monolithic structure and imports. A new, focused test suite will be built around the modular components.

#### **Step 1.2: Simplify Logging Subsystem**
The current logging in `src/topyaz/utils/logging.py` is overly complex with multiple formatters and a manager class. This will be simplified to a single setup function.

*   **In `src/topyaz/utils/logging.py`:**
    1.  Remove the `LoggingManager` and `ProgressLogger` classes.
    2.  Replace the entire file content with a simplified version:

        ```python
        # src/topyaz/utils/logging.py
        import sys
        from loguru import logger

        def setup_logging(verbose: bool = True):
            """
            Configure logging for topyaz.
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

*   **In `src/topyaz/cli.py`:**
    1.  Remove the import: `from topyaz.utils.logging import LoggingManager`.
    2.  Add the new import: `from topyaz.utils.logging import setup_logging`.
    3.  In the `TopyazCLI.__init__` method, replace the `self.logging_manager` block:
        *   **Remove:**
            ```python
            self.logging_manager = LoggingManager()
            self.logging_manager.setup(verbose=verbose)
            ```
        *   **Add:**
            ```python
            setup_logging(verbose=verbose)
            ```

#### **Step 1.3: Remove Complex Progress Reporting**
The real-time progress parsing and rich progress bars add significant complexity. We will simplify this to just stream the command's raw output when in verbose mode.

*   **Action:** Delete the file `src/topyaz/execution/progress.py`.
*   **In `src/topyaz/execution/base.py`:**
    1.  Remove the `ProgressCallback` and `ProgressAwareExecutor` classes.
    2.  The `CommandExecutor` class should be the only executor base class. Remove the `supports_progress` method from it.
*   **In `src/topyaz/execution/local.py`:**
    1.  The `LocalExecutor` should inherit directly from `CommandExecutor`, not `ProgressAwareExecutor`.
    2.  Remove the `execute_with_progress` method and its helper `_extract_progress`.
    3.  Remove the `SimpleProgressCallback` and `QuietProgressCallback` classes.
*   **In `src/topyaz/products/base.py`:**
    1.  Modify the `TopazProduct.process` method. It should call `self.executor.execute(...)` directly. The logic for progress reporting will be removed. The `stdout` and `stderr` from the execution result will be logged for debugging.

---

### **Phase 2: Consolidate Product Processing Logic**

This phase will centralize the file processing workflow (temp directory creation, execution, file moving) into the base product class.

#### **Step 2.1: Implement Template Method in `TopazProduct`**
The `process` methods in `gigapixel.py` and `photo_ai.py` are very similar. This logic will be moved to `products/base.py`.

*   **In `src/topyaz/products/base.py` (`TopazProduct` class):**
    1.  Make the existing `process` method non-abstract and implement the full workflow logic there. It will be the "template method."
    2.  This new `process` method will handle:
        *   Input and parameter validation.
        *   Creating a temporary directory for output.
        *   Calling `self.build_command(...)` to get the command.
        *   Executing the command.
        *   Calling a *new* abstract method `_find_output_file(self, temp_dir: Path, input_path: Path) -> Path` to locate the generated file in the temporary directory.
        *   Moving the found file to its final destination.
        *   Returning a `ProcessingResult`.
    3.  Define the new abstract method:
        ```python
        from abc import abstractmethod
        from pathlib import Path

        @abstractmethod
        def _find_output_file(self, temp_dir: Path, input_path: Path) -> Path:
            """
            Find the generated output file within a temporary directory.
            This must be implemented by subclasses that use the temp dir workflow.
            """
            pass
        ```

*   **In `src/topyaz/products/gigapixel.py` (`GigapixelAI` class):**
    1.  Remove the `process` method entirely. The base class implementation will be used.
    2.  Implement the `_find_output_file` method. This method will contain the logic to glob the temp directory for the expected output file (e.g., `*.jpg`, `*.png`).
    3.  The `build_command` method needs a slight adjustment: its `output_path` parameter should now be named `temp_output_dir` to reflect that it's writing to a temporary location.

*   **In `src/topyaz/products/photo_ai.py` (`PhotoAI` class):**
    1.  Follow the same steps as for `GigapixelAI`: remove `process`, implement `_find_output_file`, and adjust `build_command`.
    2.  The `_find_output_file` implementation will contain the logic to find filenames like `original-stem-tpai.ext`.

*   **In `src/topyaz/products/video_ai.py` (`VideoAI` class):**
    1.  `VideoAI` does not use a temporary directory; it writes directly to the final output file.
    2.  Therefore, `VideoAI` will **override** the base `process` method with its current, direct-writing implementation. It will not need to implement `_find_output_file`.

---

### **Phase 3: Isolate and Refine Photo AI Preferences**

The logic for manipulating Photo AI's `.plist` file is a major source of complexity and should be isolated.

#### **Step 3.1: Create a Dedicated Preferences Context Manager**
This will encapsulate the backup/update/restore workflow.

*   **Action:** No new file is needed, the existing `src/topyaz/system/photo_ai_prefs.py` is well-placed. The key is to refine its *usage*.
*   **In `src/topyaz/system/preferences.py` (`PreferenceHandler` class):**
    1.  Ensure the `__enter__` and `__exit__` methods are robust. `__enter__` should perform the backup and `__exit__` should perform the restore. This makes it a true context manager.
        ```python
        # In src/topyaz/system/preferences.py
        
        def __enter__(self):
            """Context manager entry."""
            self._backup_id_for_context = self.backup() # Store the backup_id
            return self
        
        def __exit__(self, exc_type, exc_val, exc_tb):
            """Context manager exit - restore from backup."""
            if hasattr(self, '_backup_id_for_context'):
                self.restore(self._backup_id_for_context)
            self.cleanup_all_backups()
        ```

*   **In `src/topyaz/products/photo_ai.py` (`PhotoAI` class):**
    1.  Refactor the `process` method (which, after Phase 2, is now `_process_with_preferences`).
    2.  The logic for checking `if autopilot_params:` and then calling the preferences handler should be clean and use a `with` statement.

        ```python
        # In src/topyaz/products/photo_ai.py
        
        def _process_with_preferences(self, input_path: Path, final_output_path: Path, **kwargs) -> ProcessingResult:
            """Processes image using the preferences context manager."""
            from topyaz.system.photo_ai_prefs import PhotoAIPreferences, PhotoAIAutopilotSettings
            
            try:
                # Build settings from kwargs
                autopilot_settings = self._build_autopilot_settings(**kwargs)

                # Use the handler as a context manager
                with PhotoAIPreferences() as prefs:
                    prefs.update_autopilot_settings(autopilot_settings)
                    logger.info("Temporarily applied enhanced autopilot settings.")
                    
                    # The actual processing happens here
                    result = self._process_standard(input_path, final_output_path, **kwargs)

                # The __exit__ method of PhotoAIPreferences will automatically restore settings
                logger.info("Original Photo AI preferences have been restored.")
                return result

            except ImportError:
                logger.warning("Photo AI preferences system not available, falling back to standard processing.")
                return self._process_standard(input_path, final_output_path, **kwargs)
            except Exception as e:
                logger.error(f"Error during preferences-based processing: {e}")
                # Fallback to standard processing to ensure functionality
                return self._process_standard(input_path, final_output_path, **kwargs)
        ```
    This change makes the workflow explicit and guarantees restoration even if processing fails.

---

### **Phase 4: Enhance Robustness and Final Cleanup**

This phase focuses on improving validation and ensuring the CLI is clean and robust.

#### **Step 4.1: Strengthen Input Validation**
Move file extension validation to the centralized `PathValidator` to ensure it's checked early and consistently.

*   **In `src/topyaz/system/paths.py` (`PathValidator` class):**
    1.  The `validate_input_path` method already has a `file_type: Product | None = None` parameter. Ensure this is used effectively.
    2.  The implementation should be:
        ```python
        # In src/topyaz/system/paths.py
        if path_obj.is_file() and file_type:
            ext = path_obj.suffix.lower()
            supported_extensions = self.IMAGE_EXTENSIONS.get(file_type, set())
            if file_type == Product.VIDEO_AI:
                supported_extensions = self.VIDEO_EXTENSIONS

            if ext not in supported_extensions:
                msg = f"Unsupported file type '{ext}' for {file_type.value}."
                raise ValidationError(msg)
        ```
*   **In `src/topyaz/products/base.py` (`TopazProduct` class):**
    1.  The `validate_input_path` method can now be simplified to just call `self.path_validator.validate_input_path(input_path, file_type=self.product_type)`.
    2.  Remove the `supported_formats` property from the subclasses, as this logic is now centralized in `PathValidator`.

#### **Step 4.2: Final Review of CLI**
Ensure the main `cli.py` is clean and delegates responsibility correctly.

*   **In `src/topyaz/cli.py`:**
    1.  The `__init__` is already well-structured by grouping options into `ProcessingOptions` and `RemoteOptions`. This is good, no major change needed here.
    2.  The product-specific methods (`gp`, `video`, `photo`) correctly gather parameters and pass them to the product's `process` method. This delegation is the correct pattern.
    3.  **Action:** Remove the `system_info`, `validate_environment`, and `get_optimal_batch_size` methods. These are diagnostic/optimization features, not core processing, and add to the "fluff." This aligns with the goal of a lean, focused tool. If desired, they can be added back later under a separate `topyaz diagnose` command.

## Task: 

Based on the above analysis, analyze the codebase of `topyaz`. 

Prepare a refactoring plan that will: 

- remove fluff: keep only code that's relevant to the core functionality, remove "decorational" code like custom fancy logging etc. 
- reduce the cognitive load
- itemize the code so that the functions, classes, modules are focused on a single task, and are well-structured
- ensure that the actual core functionality remains and does not break
- ensure that the code fails gracefully on files that don't comply
- ensure that the code that can be shared is shared

Make the plan very very specific, like a detailed spec for a junior dev who will actually perform the refactoring. 

Write the plan into `PLAN.md`
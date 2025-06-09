# Refactoring Plan for Topyaz

This document outlines a detailed plan for refactoring the `topyaz` codebase to improve modularity, reduce complexity, and enhance maintainability. The plan is based on the analysis of the codebase and the requirements specified in `TODO.md`.

## 1. Goal

The primary goal of this refactoring is to create a cleaner, more organized, and easier-to-maintain codebase. This will be achieved by:

*   Restructuring the `products` module.
*   Simplifying the `cli.py` module.
*   Improving code documentation.
*   Unifying shared code.
*   Reducing cognitive load by creating smaller, more focused modules.

## 2. Refactoring Steps

### 2.1. Step 1: Restructure the `products` directory

The current `products` directory contains all product-specific logic in flat files, which are getting large and complex. We will restructure this as follows:

1.  Create new directories for each product:
    *   `src/topyaz/products/gigapixel/`
    *   `src/topyaz/products/photo_ai/`
    *   `src/topyaz/products/video_ai/`
2.  Move the existing product files into their respective new directories and rename them to `api.py`:
    *   `src/topyaz/products/gigapixel.py` -> `src/topyaz/products/gigapixel/api.py`
    *   `src/topyaz/products/photo_ai.py` -> `src/topyaz/products/photo_ai/api.py`
    *   `src/topyaz/products/video_ai.py` -> `src/topyaz/products/video_ai/api.py`
3.  The `api.py` file will contain the main product class (e.g., `GigapixelAI`).
4.  Create `__init__.py` in each new product directory to expose the main class.
    *   `src/topyaz/products/gigapixel/__init__.py` will contain `from .api import GigapixelAI`
5.  Break down the logic within each `api.py` into smaller, more focused modules within the product's directory. For example, for `photo_ai`:
    *   `src/topyaz/products/photo_ai/api.py`: The main `PhotoAI` class.
    *   `src/topyaz/products/photo_ai/batch.py`: Logic for handling batch processing, including the 450-image limit.
    *   `src/topyaz/products/photo_ai/params.py`: Validation and building of Photo AI parameters.
    *   `src/topyaz/products/photo_ai/preferences.py`: Logic for handling Photo AI preferences (currently in `system/photo_ai_prefs.py`).
6.  Update `src/topyaz/products/__init__.py` to import from the new sub-packages.
7.  `products/base.py` will remain as it is, providing the base class for all products.

### 2.2. Step 2: Simplify `cli.py`

The `cli.py` module currently contains too much logic for handling parameters. It should be a thin wrapper that calls the product-specific code.

1.  The CLI methods (`giga`, `video`, `photo`) in `TopyazCLI` will be simplified.
2.  Instead of accepting dozens of parameters, they will accept `input_path`, `output_path` and a generic `**kwargs`.
3.  The `kwargs` will be passed directly to the `process` method of the corresponding product class.
4.  All parameter validation and command building logic will be handled within the respective product modules, not in `cli.py`.

**Example of simplified `giga` method in `cli.py`:**

```python
def giga(self, input_path: str, output: str | None = None, **kwargs) -> bool:
    try:
        logger.info(f"Processing {input_path} with Gigapixel AI")
        result = self._gigapixel.process(
            input_path=input_path,
            output_path=output,
            **kwargs,
        )
        # ... (error handling)
    except Exception as e:
        logger.error(f"Gigapixel AI processing failed: {e}")
        return False
```

### 2.3. Step 3: Unify and Centralize Shared Code

We will identify and centralize shared code to avoid duplication.

1.  **Path Handling:** The `PathValidator` in `system/paths.py` is well-designed. We will ensure all path operations use this class.
2.  **Parameter Validation:** Each product module will have its own parameter validation logic, but we will look for opportunities to create shared validation utilities in `topyaz/utils/validation.py`. For example, a function to validate a value is within a given range.
3.  **Command Building:** The `build_command` method in each product class will be responsible for creating the command list. We will ensure that common patterns are abstracted if possible.

### 2.4. Step 4: Improve Documentation

Documentation is crucial for maintainability. We will improve it at all levels.

1.  **Docstrings:** Every module, class, function, and method will have a clear and concise docstring explaining its purpose, arguments, and return values, following PEP 257.
2.  **`Used in:` sections:** We will continue the practice of adding `- Used in:` sections to docstrings to document dependencies between modules.
3.  **`README.md`:** The `README.md` will be updated to reflect the new project structure and provide clear usage examples for the CLI.
4.  **`PLAN.md`:** This document will serve as the living specification for the refactoring process.

### 2.5. Step 5: Improve Windows Handling

The current codebase has some stubs for Windows paths. We will improve this by:

1.  Testing path resolution on Windows.
2.  Ensuring that all hardcoded paths are replaced with platform-aware logic (e.g., using `pathlib` and `platform.system()`).
3.  Adding Windows-specific search paths for all Topaz products in their respective `get_search_paths` methods.

### 2.6. Step 6: Reduce Cognitive Load

The main goal is to make the code easier to understand. This will be achieved by:

*   Creating smaller files with a single responsibility.
*   Using clear and descriptive names for variables, functions, and classes.
*   Favoring flat structures over nested ones.
*   Adding comments to explain complex or non-obvious code.

## 3. Post-Refactoring Steps

After the refactoring is complete, we will perform the following steps:

1.  **Testing:** Run the existing test suite (`tests/test_refactoring.py`) and add new tests to cover the refactored code.
2.  **Linting and Formatting:** Run `ruff` and other tools to ensure code quality and consistency.
3.  **Review:** Perform a final review of the refactored codebase to ensure all goals have been met.
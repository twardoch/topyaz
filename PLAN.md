# topyaz Development Plan

This document outlines the development roadmap for the topyaz CLI wrapper for Topaz Labs products.

## Remote Execution Challenges and Limitations

### The Problem

Topaz Photo AI, despite offering a `--cli` flag, is fundamentally a GUI application that requires an active desktop session to function. This creates significant challenges for remote execution scenarios, which was one of the key goals of the topyaz project.

### Root Cause Analysis

#### Why Remote Execution Fails

1. **GUI Framework Initialization**
   - Photo AI's `tpai` binary is a shell script that ultimately calls the main "Topaz Photo AI" executable
   - This executable initializes Qt frameworks and macOS AppKit/CoreGraphics libraries during startup
   - These frameworks require connection to the WindowServer (macOS's display server)
   - Without an active desktop session, there is no WindowServer to connect to

2. **macOS Security Model**
   - macOS requires GUI applications to run within a user's graphical login session
   - SSH sessions are not graphical login sessions - they're terminal sessions
   - When Photo AI tries to access WindowServer from an SSH session, macOS denies access
   - The OS then sends SIGKILL (signal 9) to terminate the process, resulting in exit code 137

3. **Evidence from Our Tests**
   - Local execution: Works because it runs within the user's active desktop session
   - Remote execution: Fails with "Killed: 9" message in stderr
   - The wrapper script's `./tpai --help` test fails immediately, confirming the binary cannot initialize
   - Even with all headless environment variables set, the core executable still requires GUI access

4. **Technical Details**
   - Error message: `./tpai: line 4: 31093 Killed: 9               "../../MacOS/Topaz Photo AI" ${@} --cli`
   - This shows the actual GUI executable ("Topaz Photo AI") is being killed by the OS
   - The kill happens during initialization, before any image processing begins
   - No amount of environment manipulation can bypass macOS's WindowServer requirement

### Attempted Solutions

1. **launchctl submit** (asynchronous job submission)
   - **Approach**: Use macOS's launchctl to submit jobs to launchd
   - **Result**: Command returned immediately without waiting for completion; async nature made it unsuitable

2. **Environment Variable Manipulation**
   - **Approach**: Set headless environment variables (QT_QPA_PLATFORM=offscreen, DISPLAY=:99, CI=true, etc.)
   - **Result**: Photo AI still attempted GUI initialization and was killed by the OS

3. **GNU Screen for Pseudo-Terminal**
   - **Approach**: Use screen to create a detached session with pseudo-terminal
   - **Result**: Commands hung indefinitely in wait loops; added too much complexity

4. **Direct Execution with Enhanced Error Handling**
   - **Approach**: Run directly with comprehensive environment setup and error detection
   - **Result**: Successfully detects the limitation and provides clear error messages

### Current Status
The remote execution functionality now:
-  Properly detects when Photo AI cannot run without GUI
-  Provides clear error messages explaining the limitation
-  Avoids hanging or silent failures
-  Works correctly for local execution

### Implications
- Photo AI cannot be used for remote batch processing without an active desktop session
- Users needing remote processing should consider:
  - Using Gigapixel AI (which may have better headless support with Pro license)
  - Setting up VNC or remote desktop access on the remote machine
  - Running Photo AI only on local machines with active GUI sessions

This is a fundamental limitation of the Photo AI software itself, not the topyaz wrapper.

## Implementation Progress

### Completed Features
- [x] Basic CLI structure with Python Fire
- [x] Local execution for Photo AI
- [x] Remote SSH connection setup
- [x] File coordination system for remote execution
- [x] Preference backup/restore for Photo AI
- [x] Error handling and recovery
- [x] Virtual display detection and setup attempts
- [x] Clear error messaging for GUI requirements

### Known Issues
- [ ] Photo AI requires active GUI session even in CLI mode
- [ ] Remote execution not possible without desktop session
- [ ] Video AI and Gigapixel AI remote execution untested

### Future Development
- [ ] Test Gigapixel AI remote execution (may work better with Pro license)
- [ ] Test Video AI remote execution capabilities
- [ ] Implement batch processing with progress tracking
- [ ] Add configuration file support
- [ ] Create comprehensive test suite
- [ ] Document workarounds for remote execution needs
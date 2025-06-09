python -m topyaz photo --remote_host othello.local testdata/poster.jpg --verbose

2025-06-10 00:37:25 | INFO     | topyaz.utils.logging:setup_logging:27 - Logging configured at DEBUG level.
2025-06-10 00:37:25 | INFO     | topyaz.cli:__init__:93 - Initializing topyaz wrapper
2025-06-10 00:37:25 | DEBUG    | topyaz.cli:__init__:111 - Auto-detected remote user: adam
2025-06-10 00:37:25 | DEBUG    | topyaz.core.config:_load_config:143 - Config file not found: /Users/adam/.topyaz/_config.yaml
2025-06-10 00:37:25 | INFO     | topyaz.cli:__init__:139 - Using remote execution with virtual display: adam@othello.local
2025-06-10 00:37:25 | INFO     | topyaz.cli:__init__:155 - topyaz wrapper initialized successfully
2025-06-10 00:37:25 | INFO     | topyaz.cli:photo:496 - Processing testdata/poster.jpg with Photo AI
2025-06-10 00:37:25 | INFO     | topyaz.system.preferences:backup:187 - Created preference backup: 6ecec074-4ef6-463b-a179-50333be71f97
2025-06-10 00:37:25 | INFO     | topyaz.system.preferences:backup:187 - Created preference backup: 118a454e-2377-48c9-b544-7afd210836a9
2025-06-10 00:37:25 | DEBUG    | topyaz.system.preferences:read_preferences:110 - Successfully read preferences from /Users/adam/Library/Preferences/com.topazlabs.Topaz Photo AI.plist
2025-06-10 00:37:25 | DEBUG    | topyaz.system.photo_ai_prefs:validate_preferences:169 - Preferences validation passed
2025-06-10 00:37:25 | DEBUG    | topyaz.system.preferences:write_preferences:144 - Successfully wrote preferences to /Users/adam/Library/Preferences/com.topazlabs.Topaz Photo AI.plist
2025-06-10 00:37:25 | INFO     | topyaz.system.photo_ai_prefs:update_autopilot_settings:321 - Updated Photo AI autopilot settings
2025-06-10 00:37:25 | INFO     | topyaz.products.photo_ai:_process_with_preferences:650 - Applied enhanced autopilot settings to Photo AI preferences
2025-06-10 00:37:25 | DEBUG    | topyaz.system.paths:validate_input_path:136 - Validated input path: /Users/adam/Developer/vcs/github.twardoch/pub/topyaz/testdata/poster.jpg
2025-06-10 00:37:25 | DEBUG    | topyaz.system.photo_ai_prefs:validate_setting_values:427 - Setting values validation passed
2025-06-10 00:37:25 | DEBUG    | topyaz.products.base:find_executable:172 - Found Topaz Photo AI at: /Applications/Topaz Photo AI.app/Contents/Resources/bin/tpai
2025-06-10 00:37:25 | INFO     | topyaz.products.base:process:360 - Processing testdata/poster.jpg with Topaz Photo AI
2025-06-10 00:37:25 | DEBUG    | topyaz.execution.fabric_remote:_create_connection:401 - Creating Enhanced Fabric connection to adam@othello.local:22
2025-06-10 00:37:25 | DEBUG    | topyaz.execution.fabric_remote:_create_connection:412 - Enhanced Fabric SSH connection established
2025-06-10 00:37:25 | DEBUG    | topyaz.execution.fabric_remote:execute:345 - Executing remotely via Enhanced Fabric: mkdir -p /tmp/topyaz/sessions/topyaz_1749508645_ce054ab9/inputs /tmp/topyaz/sessions/topyaz_1749508645_ce054ab9/outputs
2025-06-10 00:37:25 | DEBUG    | topyaz.execution.fabric_remote:execute:359 - Remote command completed in 0.04s with exit status: 0
2025-06-10 00:37:25 | DEBUG    | topyaz.execution.coordination:_create_session:133 - Created remote session directory: /tmp/topyaz/sessions/topyaz_1749508645_ce054ab9
2025-06-10 00:37:25 | DEBUG    | topyaz.execution.coordination:execute_with_files:79 - Starting remote session topyaz_1749508645_ce054ab9
2025-06-10 00:37:25 | DEBUG    | topyaz.execution.fabric_remote:execute:345 - Executing remotely via Enhanced Fabric: uname -s
2025-06-10 00:37:25 | DEBUG    | topyaz.execution.fabric_remote:execute:359 - Remote command completed in 0.04s with exit status: 0
2025-06-10 00:37:25 | DEBUG    | topyaz.execution.fabric_remote:execute:366 - Remote STDOUT: Darwin

2025-06-10 00:37:25 | DEBUG    | topyaz.execution.fabric_remote:execute:345 - Executing remotely via Enhanced Fabric: free -m
2025-06-10 00:37:25 | DEBUG    | topyaz.execution.fabric_remote:execute:359 - Remote command completed in 0.02s with exit status: 127
2025-06-10 00:37:25 | DEBUG    | topyaz.execution.fabric_remote:execute:372 - Remote STDERR: bash: line 1: free: command not found

2025-06-10 00:37:25 | DEBUG    | topyaz.execution.fabric_remote:execute:345 - Executing remotely via Enhanced Fabric: sysctl -n hw.memsize
2025-06-10 00:37:25 | DEBUG    | topyaz.execution.fabric_remote:execute:359 - Remote command completed in 0.03s with exit status: 0
2025-06-10 00:37:25 | DEBUG    | topyaz.execution.fabric_remote:execute:366 - Remote STDOUT: 25769803776

2025-06-10 00:37:25 | DEBUG    | topyaz.execution.fabric_remote:execute:345 - Executing remotely via Enhanced Fabric: df -h /tmp
2025-06-10 00:37:25 | DEBUG    | topyaz.execution.fabric_remote:execute:359 - Remote command completed in 0.06s with exit status: 0
2025-06-10 00:37:25 | DEBUG    | topyaz.execution.fabric_remote:execute:366 - Remote STDOUT: Filesystem      Size    Used   Avail Capacity iused ifree %iused  Mounted on
/dev/disk3s5   1.8Ti   1.7Ti    99Gi    95%    5.5M  1.0G    1%   /System/Volumes/Data

2025-06-10 00:37:25 | DEBUG    | topyaz.execution.coordination:_get_remote_system_info:849 - Remote system info: {'os': 'Darwin', 'memory_gb': 24.0, 'available_space': '99Gi'}
2025-06-10 00:37:25 | DEBUG    | topyaz.execution.coordination:execute_with_files:86 - Detected 2 input files, 1 output files
2025-06-10 00:37:25 | DEBUG    | topyaz.execution.fabric_remote:is_gui_application:69 - Detected GUI application (topaz_photo_ai): tpai
2025-06-10 00:37:26 | DEBUG    | topyaz.execution.fabric_remote:check_display_capabilities:133 - Remote display capabilities: {'has_xvfb': False, 'has_xquartz': True, 'has_display': False, 'has_launchctl': True, 'display_var': None}
2025-06-10 00:37:26 | INFO     | topyaz.execution.fabric_remote:setup_virtual_display_command:160 - Setting up virtual display using strategy: macos_launchctl
2025-06-10 00:37:26 | DEBUG    | topyaz.execution.fabric_remote:execute:345 - Executing remotely via Enhanced Fabric: bash -c 'export DISPLAY=:99; export QT_QPA_PLATFORM=offscreen; export NSUnbufferedIO=YES; export CI=true; export HEADLESS=true; export NO_GUI=true; export TERM=xterm-256color; export DYLD_LIBRARY_PATH=/System/Library/Frameworks/ApplicationServices.framework/Versions/A/Frameworks/CoreGraphics.framework/Versions/A:$DYLD_LIBRARY_PATH; export NSUIElement=1; export LSUIElement=1; test -f /tmp/topyaz/cache/c5e75d08eba906ad65ba4f76a1b245a4278507966a886367c642d8dfee153e44/tpai -a -f '"'"'/tmp/topyaz/cache/c5e75d08eba906ad65ba4f76a1b245a4278507966a886367c642d8dfee153e44/Topaz Photo AI'"'"' 2>&1 || echo '"'"'Command failed with exit code: '"'"'$?'
2025-06-10 00:37:26 | DEBUG    | topyaz.execution.fabric_remote:execute:359 - Remote command completed in 0.03s with exit status: 0
2025-06-10 00:37:26 | DEBUG    | topyaz.execution.fabric_remote:execute:345 - Executing remotely via Enhanced Fabric: test -d /tmp/topyaz/cache/c5e75d08eba906ad65ba4f76a1b245a4278507966a886367c642d8dfee153e44/Frameworks
2025-06-10 00:37:26 | DEBUG    | topyaz.execution.fabric_remote:execute:359 - Remote command completed in 0.03s with exit status: 0
2025-06-10 00:37:26 | DEBUG    | topyaz.execution.fabric_remote:is_gui_application:69 - Detected GUI application (topaz_photo_ai): tpai
2025-06-10 00:37:26 | INFO     | topyaz.execution.fabric_remote:setup_virtual_display_command:160 - Setting up virtual display using strategy: macos_launchctl
2025-06-10 00:37:26 | DEBUG    | topyaz.execution.fabric_remote:execute:345 - Executing remotely via Enhanced Fabric: bash -c 'export DISPLAY=:99; export QT_QPA_PLATFORM=offscreen; export NSUnbufferedIO=YES; export CI=true; export HEADLESS=true; export NO_GUI=true; export TERM=xterm-256color; export DYLD_LIBRARY_PATH=/System/Library/Frameworks/ApplicationServices.framework/Versions/A/Frameworks/CoreGraphics.framework/Versions/A:$DYLD_LIBRARY_PATH; export NSUIElement=1; export LSUIElement=1; chmod +x /tmp/topyaz/cache/c5e75d08eba906ad65ba4f76a1b245a4278507966a886367c642d8dfee153e44/tpai '"'"'/tmp/topyaz/cache/c5e75d08eba906ad65ba4f76a1b245a4278507966a886367c642d8dfee153e44/Topaz Photo AI'"'"' 2>&1 || echo '"'"'Command failed with exit code: '"'"'$?'
2025-06-10 00:37:26 | DEBUG    | topyaz.execution.fabric_remote:execute:359 - Remote command completed in 0.04s with exit status: 0
2025-06-10 00:37:26 | DEBUG    | topyaz.execution.fabric_remote:is_gui_application:69 - Detected GUI application (topaz_photo_ai): tpai
2025-06-10 00:37:26 | INFO     | topyaz.execution.fabric_remote:setup_virtual_display_command:160 - Setting up virtual display using strategy: macos_launchctl
2025-06-10 00:37:26 | DEBUG    | topyaz.execution.fabric_remote:execute:345 - Executing remotely via Enhanced Fabric: bash -c 'export DISPLAY=:99; export QT_QPA_PLATFORM=offscreen; export NSUnbufferedIO=YES; export CI=true; export HEADLESS=true; export NO_GUI=true; export TERM=xterm-256color; export DYLD_LIBRARY_PATH=/System/Library/Frameworks/ApplicationServices.framework/Versions/A/Frameworks/CoreGraphics.framework/Versions/A:$DYLD_LIBRARY_PATH; export NSUIElement=1; export LSUIElement=1; test -f /tmp/topyaz/cache/c5e75d08eba906ad65ba4f76a1b245a4278507966a886367c642d8dfee153e44/tpai_wrapper 2>&1 || echo '"'"'Command failed with exit code: '"'"'$?'
2025-06-10 00:37:26 | DEBUG    | topyaz.execution.fabric_remote:execute:359 - Remote command completed in 0.04s with exit status: 0
2025-06-10 00:37:26 | DEBUG    | topyaz.execution.fabric_remote:execute:345 - Executing remotely via Enhanced Fabric: test -f /tmp/topyaz/cache/c5e75d08eba906ad65ba4f76a1b245a4278507966a886367c642d8dfee153e44/wrapper_v2.1
2025-06-10 00:37:26 | DEBUG    | topyaz.execution.fabric_remote:execute:359 - Remote command completed in 0.02s with exit status: 0
2025-06-10 00:37:26 | DEBUG    | topyaz.execution.fabric_remote:is_gui_application:69 - Detected GUI application (topaz_photo_ai): tpai
2025-06-10 00:37:26 | INFO     | topyaz.execution.fabric_remote:setup_virtual_display_command:160 - Setting up virtual display using strategy: macos_launchctl
2025-06-10 00:37:26 | DEBUG    | topyaz.execution.fabric_remote:execute:345 - Executing remotely via Enhanced Fabric: bash -c 'export DISPLAY=:99; export QT_QPA_PLATFORM=offscreen; export NSUnbufferedIO=YES; export CI=true; export HEADLESS=true; export NO_GUI=true; export TERM=xterm-256color; export DYLD_LIBRARY_PATH=/System/Library/Frameworks/ApplicationServices.framework/Versions/A/Frameworks/CoreGraphics.framework/Versions/A:$DYLD_LIBRARY_PATH; export NSUIElement=1; export LSUIElement=1; chmod +x /tmp/topyaz/cache/c5e75d08eba906ad65ba4f76a1b245a4278507966a886367c642d8dfee153e44/tpai_wrapper 2>&1 || echo '"'"'Command failed with exit code: '"'"'$?'
2025-06-10 00:37:26 | DEBUG    | topyaz.execution.fabric_remote:execute:359 - Remote command completed in 0.04s with exit status: 0
2025-06-10 00:37:26 | DEBUG    | topyaz.execution.coordination:_upload_macos_app_bundle:565 - Using cached Photo AI bundle: /tmp/topyaz/cache/c5e75d08eba906ad65ba4f76a1b245a4278507966a886367c642d8dfee153e44/tpai_wrapper
2025-06-10 00:37:26 | DEBUG    | topyaz.execution.fabric_remote:execute:345 - Executing remotely via Enhanced Fabric: test -f /tmp/topyaz/cache/fc01b12d747d330e17608c8d42f60eed03e746b7fdb5499ad2995b32f4667c9d/poster.jpg
2025-06-10 00:37:26 | DEBUG    | topyaz.execution.fabric_remote:execute:359 - Remote command completed in 0.02s with exit status: 0
2025-06-10 00:37:26 | DEBUG    | topyaz.execution.coordination:_upload_input_file:213 - Using cached file: /tmp/topyaz/cache/fc01b12d747d330e17608c8d42f60eed03e746b7fdb5499ad2995b32f4667c9d/poster.jpg
2025-06-10 00:37:26 | DEBUG    | topyaz.execution.coordination:execute_with_files:102 - Translated command: /tmp/topyaz/cache/c5e75d08eba906ad65ba4f76a1b245a4278507966a886367c642d8dfee153e44/tpai_wrapper --cli /tmp/topyaz/cache/fc01b12d747d330e17608c8d42f60eed03e746b7fdb5499ad2995b32f4667c9d/poster.jpg -o /tmp/topyaz/sessions/topyaz_1749508645_ce054ab9/outputs/topyaz__photo_ai_fdi4jv35 --verbose
2025-06-10 00:37:26 | DEBUG    | topyaz.execution.fabric_remote:is_gui_application:69 - Detected GUI application (topaz_photo_ai): tpai
2025-06-10 00:37:26 | INFO     | topyaz.execution.fabric_remote:setup_virtual_display_command:160 - Setting up virtual display using strategy: macos_launchctl
2025-06-10 00:37:26 | DEBUG    | topyaz.execution.fabric_remote:execute:345 - Executing remotely via Enhanced Fabric: bash -c 'export DISPLAY=:99; export QT_QPA_PLATFORM=offscreen; export NSUnbufferedIO=YES; export CI=true; export HEADLESS=true; export NO_GUI=true; export TERM=xterm-256color; export DYLD_LIBRARY_PATH=/System/Library/Frameworks/ApplicationServices.framework/Versions/A/Frameworks/CoreGraphics.framework/Versions/A:$DYLD_LIBRARY_PATH; export NSUIElement=1; export LSUIElement=1; /tmp/topyaz/cache/c5e75d08eba906ad65ba4f76a1b245a4278507966a886367c642d8dfee153e44/tpai_wrapper --cli /tmp/topyaz/cache/fc01b12d747d330e17608c8d42f60eed03e746b7fdb5499ad2995b32f4667c9d/poster.jpg -o /tmp/topyaz/sessions/topyaz_1749508645_ce054ab9/outputs/topyaz__photo_ai_fdi4jv35 --verbose 2>&1 || echo '"'"'Command failed with exit code: '"'"'$?'
2025-06-10 00:37:26 | DEBUG    | topyaz.execution.fabric_remote:execute:359 - Remote command completed in 0.04s with exit status: 0
2025-06-10 00:37:26 | DEBUG    | topyaz.execution.fabric_remote:execute:366 - Remote STDOUT: Running in CLI mode with minimal setup
ERROR: Unable to run tpai binary. This usually means Photo AI requires an active GUI session.
Photo AI cannot run on remote machines without an active desktop session.
Command failed with exit code: 1

2025-06-10 00:37:26 | DEBUG    | topyaz.execution.coordination:execute_with_files:106 - Remote execution completed with exit code: 0
2025-06-10 00:37:26 | DEBUG    | topyaz.execution.coordination:_debug_remote_session_contents:421 - Debugging remote session contents for topyaz_1749508645_ce054ab9
2025-06-10 00:37:26 | DEBUG    | topyaz.execution.fabric_remote:execute:345 - Executing remotely via Enhanced Fabric: find /tmp/topyaz/sessions/topyaz_1749508645_ce054ab9 -type f -ls
2025-06-10 00:37:26 | DEBUG    | topyaz.execution.fabric_remote:execute:359 - Remote command completed in 0.03s with exit status: 0
2025-06-10 00:37:26 | DEBUG    | topyaz.execution.coordination:_debug_remote_session_contents:430 - No files found in remote session directory
2025-06-10 00:37:26 | DEBUG    | topyaz.execution.fabric_remote:execute:345 - Executing remotely via Enhanced Fabric: ls -la /tmp/topyaz/sessions/topyaz_1749508645_ce054ab9/outputs
2025-06-10 00:37:26 | DEBUG    | topyaz.execution.fabric_remote:execute:359 - Remote command completed in 0.03s with exit status: 0
2025-06-10 00:37:26 | DEBUG    | topyaz.execution.fabric_remote:execute:366 - Remote STDOUT: total 0
drwxr-xr-x@ 2 adam  wheel   64 Jun 10 00:37 .
drwxr-xr-x@ 4 adam  wheel  128 Jun 10 00:37 ..

2025-06-10 00:37:26 | DEBUG    | topyaz.execution.coordination:_debug_remote_session_contents:439 - Outputs directory contents:
total 0
drwxr-xr-x@ 2 adam  wheel   64 Jun 10 00:37 .
drwxr-xr-x@ 4 adam  wheel  128 Jun 10 00:37 ..

2025-06-10 00:37:26 | DEBUG    | topyaz.execution.fabric_remote:execute:345 - Executing remotely via Enhanced Fabric: test -f /tmp/topyaz/sessions/topyaz_1749508645_ce054ab9/outputs/topyaz__photo_ai_fdi4jv35
2025-06-10 00:37:26 | DEBUG    | topyaz.execution.fabric_remote:execute:359 - Remote command completed in 0.02s with exit status: 1
2025-06-10 00:37:26 | DEBUG    | topyaz.execution.fabric_remote:execute:345 - Executing remotely via Enhanced Fabric: test -d /tmp/topyaz/sessions/topyaz_1749508645_ce054ab9/outputs/topyaz__photo_ai_fdi4jv35
2025-06-10 00:37:26 | DEBUG    | topyaz.execution.fabric_remote:execute:359 - Remote command completed in 0.04s with exit status: 1
2025-06-10 00:37:26 | WARNING  | topyaz.execution.coordination:_download_output_files:371 - Output file/directory not found on remote: /tmp/topyaz/sessions/topyaz_1749508645_ce054ab9/outputs/topyaz__photo_ai_fdi4jv35
2025-06-10 00:37:26 | DEBUG    | topyaz.execution.coordination:_cleanup_session:454 - Cleaning up remote session topyaz_1749508645_ce054ab9
2025-06-10 00:37:26 | DEBUG    | topyaz.execution.fabric_remote:execute:345 - Executing remotely via Enhanced Fabric: rm -rf /tmp/topyaz/sessions/topyaz_1749508645_ce054ab9
2025-06-10 00:37:26 | DEBUG    | topyaz.execution.fabric_remote:execute:359 - Remote command completed in 0.03s with exit status: 0
2025-06-10 00:37:26 | ERROR    | topyaz.products.photo_ai:_find_output_file:569 - No output files found in temporary directory /var/folders/05/clcynl0509ldxltl599hhhx40000gn/T/topyaz__photo_ai_fdi4jv35
2025-06-10 00:37:26 | ERROR    | topyaz.products.base:process:456 - Error processing testdata/poster.jpg with Topaz Photo AI: No output files found in temporary directory /var/folders/05/clcynl0509ldxltl599hhhx40000gn/T/topyaz__photo_ai_fdi4jv35
2025-06-10 00:37:26 | INFO     | topyaz.system.preferences:restore:226 - Restored preferences from backup: 118a454e-2377-48c9-b544-7afd210836a9
2025-06-10 00:37:26 | DEBUG    | topyaz.system.preferences:_cleanup_backup:248 - Cleaned up backup file: /var/folders/05/clcynl0509ldxltl599hhhx40000gn/T/topyaz_backups/com.topazlabs.Topaz Photo AI.plist_118a454e-2377-48c9-b544-7afd210836a9.bak
2025-06-10 00:37:26 | INFO     | topyaz.products.photo_ai:_process_with_preferences:658 - Restored original Photo AI preferences
2025-06-10 00:37:26 | INFO     | topyaz.system.preferences:restore:226 - Restored preferences from backup: 6ecec074-4ef6-463b-a179-50333be71f97
2025-06-10 00:37:26 | DEBUG    | topyaz.system.preferences:_cleanup_backup:248 - Cleaned up backup file: /var/folders/05/clcynl0509ldxltl599hhhx40000gn/T/topyaz_backups/com.topazlabs.Topaz Photo AI.plist_6ecec074-4ef6-463b-a179-50333be71f97.bak
False
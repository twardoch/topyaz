python -m topyaz photo testdata/poster.jpg --verbose

2025-06-10 01:44:55 | INFO     | topyaz.utils.logging:setup_logging:27 - Logging configured at DEBUG level.
2025-06-10 01:44:55 | INFO     | topyaz.cli:__init__:71 - Initializing topyaz wrapper
2025-06-10 01:44:55 | DEBUG    | topyaz.core.config:_load_config:138 - Config file not found: /Users/adam/.topyaz/_config.yaml
2025-06-10 01:44:55 | INFO     | topyaz.cli:__init__:94 - Using local execution
2025-06-10 01:44:55 | INFO     | topyaz.cli:__init__:105 - topyaz wrapper initialized successfully
2025-06-10 01:44:55 | INFO     | topyaz.cli:photo:402 - Processing testdata/poster.jpg with Photo AI
2025-06-10 01:44:55 | INFO     | topyaz.system.preferences:backup:187 - Created preference backup: 4cd1dc7e-4bf6-4be5-8bc3-ac51915cb143
2025-06-10 01:44:55 | INFO     | topyaz.system.preferences:backup:187 - Created preference backup: 90291197-bb49-40dc-bb88-64aac5f14b7a
2025-06-10 01:44:55 | DEBUG    | topyaz.system.preferences:read_preferences:110 - Successfully read preferences from /Users/adam/Library/Preferences/com.topazlabs.Topaz Photo AI.plist
2025-06-10 01:44:55 | DEBUG    | topyaz.products.photo_ai.preferences:validate_preferences:126 - Preferences validation passed
2025-06-10 01:44:55 | DEBUG    | topyaz.system.preferences:write_preferences:144 - Successfully wrote preferences to /Users/adam/Library/Preferences/com.topazlabs.Topaz Photo AI.plist
2025-06-10 01:44:55 | INFO     | topyaz.products.photo_ai.preferences:update_autopilot_settings:228 - Updated Photo AI autopilot settings
2025-06-10 01:44:55 | INFO     | topyaz.products.photo_ai.api:_process_with_preferences:130 - Applied enhanced autopilot settings to Photo AI preferences
2025-06-10 01:44:55 | DEBUG    | topyaz.system.paths:validate_input_path:136 - Validated input path: /Users/adam/Developer/vcs/github.twardoch/pub/topyaz/testdata/poster.jpg
2025-06-10 01:44:55 | WARNING  | topyaz.products.photo_ai.params:validate_params:50 - Preferences system not available - skipping autopilot parameter validation
2025-06-10 01:44:55 | DEBUG    | topyaz.products.base:find_executable:172 - Found Topaz Photo AI at: /Applications/Topaz Photo AI.app/Contents/Resources/bin/tpai
2025-06-10 01:44:55 | INFO     | topyaz.products.base:process:360 - Processing testdata/poster.jpg with Topaz Photo AI
2025-06-10 01:44:55 | DEBUG    | topyaz.execution.local:execute:72 - Executing locally: /Applications/Topaz Photo AI.app/Contents/Resources/bin/tpai --cli /Users/adam/Developer/vcs/github.twardoch/pub/topyaz/testdata/poster.jpg -o /private/var/folders/05/clcynl0509ldxltl599hhhx40000gn/T/topyaz__photo_ai_tvcfoqbo --verbose
2025-06-10 01:44:55 | ERROR    | topyaz.execution.local:execute:121 - Command execution failed: subprocess.run() got multiple values for keyword argument 'check'
2025-06-10 01:44:55 | ERROR    | topyaz.products.base:process:443 - Error processing testdata/poster.jpg with Topaz Photo AI: Command execution failed: subprocess.run() got multiple values for keyword argument 'check'
2025-06-10 01:44:55 | INFO     | topyaz.system.preferences:restore:226 - Restored preferences from backup: 90291197-bb49-40dc-bb88-64aac5f14b7a
2025-06-10 01:44:55 | DEBUG    | topyaz.system.preferences:_cleanup_backup:248 - Cleaned up backup file: /var/folders/05/clcynl0509ldxltl599hhhx40000gn/T/topyaz_backups/com.topazlabs.Topaz Photo AI.plist_90291197-bb49-40dc-bb88-64aac5f14b7a.bak
2025-06-10 01:44:55 | INFO     | topyaz.products.photo_ai.api:_process_with_preferences:134 - Restored original Photo AI preferences
2025-06-10 01:44:55 | INFO     | topyaz.system.preferences:restore:226 - Restored preferences from backup: 4cd1dc7e-4bf6-4be5-8bc3-ac51915cb143
2025-06-10 01:44:55 | DEBUG    | topyaz.system.preferences:_cleanup_backup:248 - Cleaned up backup file: /var/folders/05/clcynl0509ldxltl599hhhx40000gn/T/topyaz_backups/com.topazlabs.Topaz Photo AI.plist_4cd1dc7e-4bf6-4be5-8bc3-ac51915cb143.bak
False
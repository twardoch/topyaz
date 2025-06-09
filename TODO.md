
CLI:

- `dry_run`: 
  - is it actually used? 
  - there’s also `skip_processing` which is basically the same. We only need `dry_run`

- `autopilot_preset`: 
  - it should be just `preset`
  - I think its default value should be `auto`

- `override_autopilot`: 
  - do we really need this? 
  - what does the app so if it’s provided? 

For Photo AI, we have this special treatment where we can change the prefs before running the tool, and that influences autopilot. See src/topyaz/system/photo_ai_prefs.py — therefore we should explicitly add the options that are accessible via the preferences to CLI, so that they're listed in the usage
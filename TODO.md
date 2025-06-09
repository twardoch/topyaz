CLI:

- ✅ `dry_run`: 
  - FIXED: Removed `skip_processing` parameter, using only `dry_run` throughout the codebase
  - `skip_processing` calls now use `self._options.dry_run` instead

- ✅ `autopilot_preset`: 
  - FIXED: Renamed to `preset` in CLI method signature and documentation
  - FIXED: Default value changed to `"auto"` in PhotoAIParams

- ✅ `override_autopilot`: 
  - KEPT: This parameter is needed - it controls when to add the `--override` flag to Photo AI CLI
  - The logic automatically sets it when manual enhancement parameters are provided, but can also be explicitly set

- ✅ Photo AI preference options:
  - ADDED: All Photo AI autopilot preference options are now exposed as CLI parameters
  - Added parameters: face_strength, face_detection, face_parts, denoise_model, denoise_levels, denoise_strength, denoise_raw_model, denoise_raw_levels, denoise_raw_strength, sharpen_model, sharpen_levels, sharpen_strength, upscaling_model, upscaling_factor, upscaling_type, deblur_strength, denoise_upscale_strength, lighting_strength, raw_exposure_strength, adjust_color, temperature_value, opacity_value, resolution_unit, default_resolution, overwrite_files, recurse_directories, append_filters
  - These parameters are passed through to the Photo AI processing methods and handled via the preferences system
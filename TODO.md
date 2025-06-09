Here are the KB sizes of the files: 

4	./topyaz/__init__.py
4	./topyaz/__main__.py
4	./topyaz/__version__.py
4	./topyaz/core/__init__.py
4	./topyaz/execution/__init__.py
4	./topyaz/execution/base.py
4	./topyaz/products/__init__.py
4	./topyaz/system/__init__.py
4	./topyaz/utils/__init__.py
4	./topyaz/utils/logging.py
8	./topyaz/core/errors.py
8	./topyaz/core/types.py
8	./topyaz/execution/local.py
12	./topyaz/core/config.py
12	./topyaz/system/environment.py
12	./topyaz/system/gpu.py
12	./topyaz/system/memory.py
12	./topyaz/system/preferences.py
12	./topyaz/utils/validation.py
16	./topyaz/products/gigapixel.py
16	./topyaz/system/paths.py
20	./topyaz/cli.py
20	./topyaz/products/base.py
20	./topyaz/system/photo_ai_prefs.py
24	./topyaz/products/video_ai.py
28	./topyaz/products/photo_ai.py

The last 5 are too complex. 

- Analyze the entire codebase (llms.txt has a snapshot)
- In `PLAN.md` write a detailed refactoring plan/spec (suitable and sufficient for a junior dev who doesn't know the codebase to perform the refactoring)
- Move the `products` code into separate folders, one for gigapixel, one for photo_ai, one for video_ai. In there make a nicely organized codebase for each product
- Consider what code should shared, unify that into shared code
- Improve handling on Windows
- Reduce cognitive load
- Move code into dedicated pieces
- Document each construct (function, class, method, module) and include `- Used in:`
- Think whether any given piece of code is necessary or an unnecessary complication. Simplify the unnecessary complications. 
- `cli.py` must be simpler. It shouldn't contain complicated per-product logic. It really should just be a CLI class with methods that accept parameters (because Fire CLI works so), and then these should be calling Topaz-product-specific code elsewhere. The logic should not be in cli.py




You may offload some of the code inside the methods from `cli.py` to dedicated locations, so that `cli.py` really is just the CLI interface, but no logic. But the methods in `cli.py` must retain the full explicit signatures and docstrings! 
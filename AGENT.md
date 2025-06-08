## TLDR: topyaz Project

**topyaz** is a Python CLI wrapper that unifies Topaz Labs' three AI products (Video AI, Gigapixel AI, Photo AI) into a single command-line interface for professional batch processing workflows.

**🎯 Core Purpose:**
- Single CLI tool for all Topaz products instead of using separate GUIs
- Enable remote processing via SSH on powerful machines
- Batch operations with progress monitoring and error recovery

**📋 Requirements:**
- macOS 11+ (Topaz products are Mac-focused)
- Gigapixel AI Pro license ($499/year) for CLI access
- 16GB+ RAM, 80GB+ storage for models

**🚧 Current Status:**
- **Planning Stage**: Extensive specification (SPEC.md) and documentation written
- **Implementation**: Minimal skeleton code - most features in TODO.md are unimplemented
- **Architecture**: Designed around unified `topyazWrapper` class using Python Fire for CLI generation

**💡 Key Value:**
- ~2x faster than GUI for batch operations
- Remote execution on GPU servers
- Unified interface across Video AI (upscaling), Gigapixel AI (image enhancement), Photo AI (auto-enhancement)
- Production-ready error handling and recovery mechanisms

**Target Users:** Video/photo professionals, content creators, automated workflow developers who need efficient batch processing of large media collections.

# When you write code

- Iterate gradually, avoiding major changes
- Minimize confirmations and checks
- Preserve existing code/structure unless necessary
- Use constants over magic numbers
- Check for existing solutions in the codebase before starting
- Check often the coherence of the code you’re writing with the rest of the code.
- Focus on minimal viable increments and ship early
- Write explanatory docstrings/comments that explain what and WHY this does, explain where and how the code is used/referred to elsewhere in the code
- Analyze code line-by-line
- Handle failures gracefully with retries, fallbacks, user guidance
- Address edge cases, validate assumptions, catch errors early
- Let the computer do the work, minimize user decisions
- Reduce cognitive load, beautify code
- Modularize repeated logic into concise, single-purpose functions
- Favor flat over nested structures
- Consistently keep, document, update and consult the holistic overview mental image of the codebase. 

## Keep track of paths

In each source file, maintain the up-to-date `this_file` record that shows the path of the current file relative to project root. Place the `this_file` record near the top of the file, as a comment after the shebangs, or in the YAML Markdown frontmatter.

## When you write Python

- Use `uv pip`, never `pip`
- Use `python -m` when running code
- PEP 8: Use consistent formatting and naming
- Write clear, descriptive names for functions and variables
- PEP 20: Keep code simple and explicit. Prioritize readability over cleverness
- Use type hints in their simplest form (list, dict, | for unions)
- PEP 257: Write clear, imperative docstrings
- Use f-strings. Use structural pattern matching where appropriate
- ALWAYS add "verbose" mode logugu-based logging, & debug-log
- For CLI Python scripts, use fire & rich, and start the script with

```
#!/usr/bin/env -S uv run -s
# /// script
# dependencies = ["PKG1", "PKG2"]
# ///
# this_file: PATH_TO_CURRENT_FILE
```

Work in rounds: 

- Create `PLAN.md` as a detailed flat plan with `[ ]` items. 
- Identify the most important TODO items, and create `TODO.md` with `[ ]` items. 
- Implement the changes. 
- Update `PLAN.md` and `TODO.md` as you go. 
- After each round of changes, update `CHANGELOG.md` with the changes.
- Update `README.md` to reflect the changes.

Ask before extending/refactoring existing code in a way that may add complexity or break things.

When you’re finished, print "Wait, but" to go back, think & reflect, revise & improvement what you’ve done (but don’t invent functionality freely). Repeat this. But stick to the goal of "minimal viable next version". Lead two experts: "Ideot" for creative, unorthodox ideas, and "Critin" to critique flawed thinking and moderate for balanced discussions. The three of you shall illuminate knowledge with concise, beautiful responses, process methodically for clear answers, collaborate step-by-step, sharing thoughts and adapting. If errors are found, step back and focus on accuracy and progress.

## After Python changes run:

```
./cleanup.sh
```

Be creative, diligent, critical, relentless & funny!
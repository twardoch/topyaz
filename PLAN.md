# topyaz Development Plan

This document outlines the development roadmap for the topyaz CLI wrapper for Topaz Labs products.

## 1. Remote Execution Challenges and Limitations

### 1.1. The Problem

Topaz Photo AI, despite offering a `--cli` flag, is fundamentally a GUI application that requires an active desktop session to function. This creates significant challenges for remote execution scenarios, which was one of the key goals of the topyaz project.

### 1.2. Root Cause Analysis

#### 1.2.1. Why Remote Execution Fails

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

### 1.3. Attempted Solutions

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

### 1.4. Current Status
The remote execution functionality now:
-  Properly detects when Photo AI cannot run without GUI
-  Provides clear error messages explaining the limitation
-  Avoids hanging or silent failures
-  Works correctly for local execution

### 1.5. Implications
- Photo AI cannot be used for remote batch processing without an active desktop session
- Users needing remote processing should consider:
  - Using Gigapixel AI (which may have better headless support with Pro license)
  - Setting up VNC or remote desktop access on the remote machine
  - Running Photo AI only on local machines with active GUI sessions

This is a fundamental limitation of the Photo AI software itself, not the topyaz wrapper.

## 2. Implementation Progress

### 2.1. Completed Features
- [x] Basic CLI structure with Python Fire
- [x] Local execution for Photo AI
- [x] Remote SSH connection setup
- [x] File coordination system for remote execution
- [x] Preference backup/restore for Photo AI
- [x] Error handling and recovery
- [x] Virtual display detection and setup attempts
- [x] Clear error messaging for GUI requirements

### 2.2. Known Issues
- [ ] Photo AI requires active GUI session even in CLI mode
- [ ] Remote execution not possible without desktop session
- [ ] Video AI and Gigapixel AI remote execution untested

### 2.3. Future Development
- [ ] Test Gigapixel AI remote execution (may work better with Pro license)
- [ ] Test Video AI remote execution capabilities
- [ ] Implement batch processing with progress tracking
- [ ] Add configuration file support
- [ ] Create comprehensive test suite
- [ ] Document workarounds for remote execution needs



# Appendix 1: Research

Got it. I’ll investigate methods for remotely executing a Qt-based GUI application in CLI mode on macOS, from one Mac to another using Python. I’ll focus on macOS-compatible solutions that address GUI session requirements, potential use of remote desktop, VNC, AppleScript, launchd, or authenticated session emulation. I’ll get back to you with options and their trade-offs.

## 3. Background & Challenges

Executing a macOS GUI application remotely is non-trivial due to how macOS handles GUI sessions. Native Mac apps (like Qt-based GUIs) don’t use X11, so you **cannot rely on X11 forwarding over SSH** as you might on Linux. Instead, macOS GUI apps require an active user session (with WindowServer) to display or operate. If you attempt to launch a GUI app via SSH without an active logged-in user, you’ll encounter errors (e.g. *LSOpenURLsWithRole() failed with error -600/-610*) because there is *“no user display server to connect to”*. In short, the app must run within a macOS login session – crossing session boundaries is *possible but difficult*. Below are several approaches to tackle this, along with their success conditions and trade-offs.

## 4. Using the Application’s CLI/Headless Mode (If Available)

Many GUI applications offer a command-line interface (CLI) or *headless* mode for automation. In the case of **Topaz Photo AI**, the app can run in CLI mode on macOS by invoking its binary with the `--cli` flag. For example:

```bash
cd /Applications/Topaz\ Photo\ AI.app/Contents/MacOS  
./Topaz\ Photo\ AI --help  (to see options)  
./Topaz\ Photo\ AI --cli "/path/to/input/image.jpg"
```

According to Topaz Labs’ documentation, this will process images using your saved Autopilot settings without opening a GUI. On Windows, Topaz provides a separate `tpai.exe` for CLI use, which *“runs completely headless, making it ideal for automation”*. The Mac version uses the same app binary with a flag, but similarly runs without showing a window in `--cli` mode.

**Success criteria:** If the application provides a supported CLI, you can simply SSH into the remote Mac (or use a Python SSH library) and execute the CLI command. The app should perform its task (e.g. upscale an image) and exit, writing output to files or stdout as designed. This requires that the app is installed/licensed on the remote Mac and any initial setup (like logging into Topaz account or setting preferences) is already done.

**Trade-offs:** This is the **preferred solution** when available, as it avoids any GUI dependency. It’s script-friendly and reliable for batch processing. However, not all GUI apps have a headless mode. In Topaz’s case, some older products only added CLI support in later versions or for certain license tiers. For example, **Topaz Gigapixel AI** introduced a CLI in version 7.3, but it’s *“available exclusively to Pro license users”*. This means you’d need the appropriate license level to use Gigapixel’s CLI. Additionally, current CLI implementations may have limited functionality compared to the interactive GUI (e.g. you might rely on preset preferences rather than dynamic GUI controls). Always check the app’s documentation for CLI options and any limitations (Topaz’s CLI, for instance, might not expose every fine-grained setting in the UI).

## 5. SSH with GUI Session Invocation

If a true headless mode is unavailable, you can attempt to launch the GUI app on the remote Mac through SSH **within an active user session**. The key is that a user must be logged in on the remote Mac (physically or via remote desktop) so a WindowServer instance is running for that session. You would SSH in as that **same user** and run a launch command. Common techniques include:

* **Using the `open` command:** e.g. `ssh user@remote **open -a "Topaz Photo AI" "/path/to/image.jpg"**`. The `open -a` command asks LaunchServices to start the app (as if double-clicked). This should cause the app’s GUI to launch in the logged-in user’s session (processing the image if the app auto-starts that). If the user session is active and you are logged in as that user, this often works. If no one is logged in (or you use a different user via `sudo`), macOS will refuse to launch the GUI for security reasons.

* **Using AppleScript locally on the remote:** e.g. `ssh user@remote **osascript -e 'tell application "Topaz Photo AI" to launch'**`. AppleScript’s **`tell application ... to ...`** will send an Apple Event to launch the app in the GUI. This again works only if the target user’s session is running (the script runs in that context if you’re SSH’d in as the user).

* **Using `launchctl` as user:** In more complex cases, one can use launchd to target the console user’s session. For example, `sudo launchctl asuser <UID> open ...` can attempt to launch the app as a given user in their session. This was suggested in older solutions, but macOS SIP and permission changes can make it finicky (error **-600** or permission denied if not executed exactly right). Essentially, you must be root to use `launchctl asuser`, and it must target a *logged-in* user’s UID in the Aqua session. Another variant is using `launchctl bsexec <PID> ...` with a GUI process’s PID to spawn a process in that session. These are advanced and not officially documented (Apple engineers don’t recommend general use of bsexec). They may be needed for specialized workflows, but for most cases simply ensuring the same user context via SSH is easier.

**Success criteria:** The remote Mac must have an active GUI login for the user. You can verify with the `w` or `who` command that the user is logged in on console (or a remote desktop session). Then, an `open` or `osascript` command executed via SSH should successfully launch the app **in that user’s GUI** (you might not see any output in SSH, but the process will start on remote Mac). The app may show its window on the remote Mac’s display and proceed with its task. If it’s a processing app like Topaz and it auto-exits when done (CLI mode aside), you might need additional scripting to quit it or close it after processing (unless it can be run purely CLI).

**Trade-offs:** This approach avoids extra services and uses built-in tools, but it hinges on the remote Mac’s state. It **will not work if the Mac is at the login screen or the user’s session is not active**. In those cases you’ll get errors about permission or no display. It may also fail if the remote Mac is sleeping or screen-locked in a way that prevents UI launches. Additionally, if the app requires user interaction (dialog boxes, etc.), launching it blindly might leave it waiting on the remote end. This method is best for apps that can be pointed at a file or operation and then run autonomously. Always test the command locally first (on the remote Mac) to ensure it does what you expect when launched via CLI.

## 6. AppleScript Remote Apple Events

AppleScript can be used **across Macs** via Remote Apple Events. By enabling “Remote Automation” on the target Mac (in **System Settings > Sharing > Remote Apple Events**), you allow that Mac to accept AppleScript commands from another machine. From the local Mac (running Python or any language), you can send Apple events to the remote app. For example, using AppleScript:

```applescript
tell application "Topaz Photo AI" of machine "eppc://user:password@RemoteMac.local" 
    open POSIX file "/Users/remoteuser/Pictures/image.jpg"
end tell
```

This would authenticate to the remote Mac and instruct Topaz Photo AI to open a given file (which should trigger processing if the app behaves that way). Remote Apple Events essentially let an AppleScript running on your Mac **“interact with your Mac \[remotely]. For example, \[it] could open and print a document that’s located on your Mac.”** In our context, it can launch apps, send menu commands, or open files on the remote Mac’s apps, as if you were running AppleScript on that machine. Python can invoke such scripts via the `osascript` command or via libraries that interface with AppleScript.

**Success criteria:** You must have Remote Apple Events turned **on** and properly configured on the remote Mac (optionally restricting access to specific users). The network must allow communication on the AppleEvents port (e.g. no firewall blocking the “eppc” protocol). Once set, the local Mac can run the AppleScript and the remote Mac’s application should respond (e.g., Topaz Photo AI opens and processes the image). This doesn’t require an SSH login, just the Apple event authentication (user/password provided in the script’s machine URL). The remote user session still needs to be active (Remote Apple Events won’t magically start a GUI session; it will act within whatever session the specified user already has).

**Trade-offs:** This approach is fairly high-level and leverages macOS’s built-in automation capabilities. It can be powerful (you can script menu clicks, GUI actions, etc. remotely), but there are a few caveats. First, enabling remote Apple scripting might be a security concern in some environments, since it allows remote control of apps. Second, the AppleScript that you send may require the target application to be scriptable or at least respond to basic Apple events (many apps respond to `open` or `activate` even if they don’t have a rich AppleScript dictionary). If the app is not scriptable, you might be limited to just launching it. Additionally, both machines need to have matching application scripting dictionaries if you want to use app-specific commands – in practice, you can often stick to generic actions. Finally, debugging AppleScript errors remotely can be tricky. Still, for Mac-specific workflows, this is a clean solution that works within supported frameworks (no hacking of display servers, etc.).

## 7. Using `launchd` Agents or Daemons

For a more **persistent or automated approach**, you can leverage macOS’s `launchd` system to ensure the GUI app runs in the proper context, even if triggered remotely. There are a couple of patterns here:

* **Launch Agent on Login:** You can create a Launch Agent (in `/Library/LaunchAgents` for all users or `~/Library/LaunchAgents` for a specific user) that runs the GUI application or a script when the user logs in. For example, a custom LaunchAgent plist could be set to run `Topaz Photo AI.app/Contents/MacOS/Topaz Photo AI --cli /path/to/image` at login or on a certain trigger (like a file appearing in a folder). This ensures the process runs inside the user’s GUI session (since LaunchAgents run only when a user is logged in with Aqua). To trigger it remotely, you might combine this with a remote file drop or a signal. For instance, the agent could watch a specific directory for images to process – you then scp a file in, and the agent launches the app to process it. This is more complex to set up but once in place can automate processing whenever new files arrive, without manual SSH each time.

* **On-Demand Launch via `launchctl`:** As referenced earlier, macOS allows launching jobs into an existing session. An admin could SSH into the remote Mac and use `launchctl` to load or start a job in the user’s session. Example: `sudo launchctl bootstrap gui/<UID> /path/to/agent.plist` or `launchctl kickstart gui/<UID>/com.your.agent` (using the GUI session domain) to start a job on an already logged-in GUI session. Another technique is identifying a process of the logged-in user (like the Dock or Finder process) and using `launchctl bsexec <PID> <command>` to execute a command in that session’s namespace. These methods essentially “inject” your process into the user’s GUI context. They require root privileges and careful construction of commands, especially with SIP (System Integrity Protection) in play. In OS X 10.10+, a correct `bsexec` implementation existed, but by 10.11 El Capitan Apple locked down direct session-port access, making `asuser` with root the more viable approach.

**Success criteria:** For the LaunchAgent method, the remote Mac’s user simply needs to be logged in (or auto-logged in at boot), so the agent is running. The agent will then respond to the defined trigger (login or file event) and launch the GUI app as configured. You, from the local Mac, would interact by dropping files or signaling the agent’s trigger. For the on-demand `launchctl` method, you need administrative SSH access to execute the commands. Success means the app starts in the correct session (you should see it running under the console user’s processes). Proper setup of the plist (for LaunchAgent) or correct targetting of UID/PID is critical. When done right, this approach programmatically launches the app without requiring manual GUI actions.

**Trade-offs:** Using `launchd` is robust for automation but **adds complexity**. Writing and installing launchd plists requires admin rights on the remote Mac, and debugging them can be non-intuitive. There’s also the risk of the LaunchAgent launching when not desired (if misconfigured). The `launchctl` injection approach, while powerful, is using internal APIs that Apple doesn’t advertise for general use – it might break with OS updates or be blocked by security features. In all cases, the remote Mac must be in a state where the user’s session is available (LaunchAgents won’t run if the Mac is at the login screen; you’d need something like auto-login or a prior login via remote desktop). The benefit of these methods is that they **don’t require constant active VNC/ARD connections** and can be triggered via scripts or file transfers, making them suitable for automated workflows. But for a one-off or interactive use, they might be overkill compared to simpler SSH/AppleEvent approaches.

## 8. Remote Desktop or Virtual Display Sessions (VNC/Screen Sharing)

Another approach is to leverage macOS’s built-in Screen Sharing (VNC) to create a remote GUI session, and then either manually or programmatically control that session. macOS allows multiple users to be logged in simultaneously via VNC screen sharing. For example, if you connect to the remote Mac using Screen Sharing and **choose a different user account** at the login interface, *“you will be logged into that user’s desktop **in the background**. It will not affect what is seen on the physical screen.”* This means you can have a headless GUI session purely for remote control. Once connected, you can launch the GUI app normally (through the Finder or Terminal in that VNC session). The remote app will think it’s running on a real display (because the VNC session provides a virtual display).

From a Python standpoint, one could automate this by using Apple’s Remote Desktop (ARD) tools or third-party VNC automation. Apple Remote Desktop (a separate admin tool) has the ability to send Unix commands or AppleScripts to client Macs remotely, which could be used to launch apps without even opening a visible screen share. If you prefer open-source, you might script a VNC client (though that’s complex) or simply ensure the remote Mac auto-launches the needed app when a VNC session starts (perhaps via a login item for that specific “headless” user account).

**Success criteria:** Successfully establish a remote desktop session to the Mac – either to the console user or a separate user. Confirm that you can interact with the desktop (either manually or via ARD’s send commands feature). In that session, launch the application (manually or with a script). The app should run as if a user were there. Screen Sharing on macOS explicitly allows the remote controller to *“open, move, and close files and windows; open apps; and even restart your Mac”*, so this method essentially replicates sitting at the GUI. If using ARD’s command feature, success is the same as SSH: the app launches in the remote GUI.

**Trade-offs:** This approach is the most straightforward in terms of mimicking an interactive user, but it’s also the most **resource-intensive** and potentially **least automated**. It often involves maintaining a GUI session, which could be slow over a network and isn’t easily scripted unless you use additional tools. It might require the remote Mac to have “Screen Sharing” or “Remote Management” enabled (with proper credentials set). On the plus side, it doesn’t require any special CLI support from the app – you are literally running the GUI. This means you can access features not exposed via CLI. However, any required user interaction will still need to be handled (you might watch the process via VNC and intervene if needed). If the goal is full automation, this is not ideal, but it can be a good way to *set up* the remote session (log in the user, etc.) before using one of the more automated methods. In practice, many headless Mac setups use a combination of auto-login + VNC to ensure a persistent desktop, then trigger apps via scripts. Just be mindful of security (VNC should be password protected, etc.), and consider using this as a stepping stone to a more automated solution once everything is working.

## 9. UI Automation as a Last Resort

If the application has no CLI and requires actual GUI interaction (for example, pressing buttons within the app), you may need to employ UI automation techniques. macOS has an Accessibility API that can be driven by AppleScript or languages like Python (with PyObjC or tools like SikuliX). For instance, community members have created AppleScript-based automators for Topaz apps that **“use the System Events application to send menu commands and button clicks to the UI”**. One such script (`gigapixel-automator`) was used to batch process images by controlling Topaz Gigapixel’s GUI: it would launch the app, assume certain dialog settings, and programmatically click the “Start” or “Save” buttons. This kind of tool essentially **emulates a user** in the GUI.

From a remote execution standpoint, you could trigger such a script via any of the above methods (SSH, Apple Events, ARD, etc.) to run on the remote Mac. The script would then drive the GUI to accomplish the task.

**Success criteria:** UI automation scripts require that the GUI application is running in a session **and** that the script has permission to control the GUI. On macOS, the script (e.g. Terminal or whatever host process runs it) must be granted **Accessibility privileges** in System Settings for it to control other apps. Once set, the script can, for example, find a window or menu item and activate it. Success means the automation performs the needed steps (load image, select settings, start processing, etc.) without human intervention. You often can observe it via screen sharing to verify it’s clicking the right buttons.

**Trade-offs:** This method is **fragile and maintenance-heavy**. Any change in the app’s UI (an update that moves a button or changes a menu) can break the script. It also might be slow, as it mimics user delays and waits for UI elements. Additionally, some interactions might still need confirmation dialogs or handle unexpected pop-ups (like license prompts or error messages). Use this only if there is absolutely no better automation interface. It’s also worth noting that Topaz and similar vendors are moving toward providing real CLI support (as seen with Photo AI and new Gigapixel versions), so UI scripting might only be needed for older versions or unsupported apps. Whenever possible, prefer a supported API or CLI (approaches 1–3) over GUI automation.

## 10. Comparison & Key Trade-Offs

Each approach has its niche, and often a combination might yield the best result. Here is a quick comparison:

* **Built-in CLI:** *Most reliable and script-friendly* – runs headless, suitable for Python automation. No GUI needed, but requires the app to support it (and possibly a license upgrade). Ideal for batch processing and server-like use cases.
* **SSH + Open/AppleScript:** *Lightweight and straightforward* – leverages the OS’s ability to launch apps in an existing session. Requires an active user session on remote. Minimal setup, but if the environment isn’t right (no user logged in, or wrong user), it fails. Good for ad-hoc remote launches when you ensure the remote Mac is prepared (logged in and awake).
* **Remote Apple Events:** *Flexible and Mac-native* – allows high-level control of the remote app (open files, invoke menu items) without a full remote desktop. Needs one-time setup (enable remote scripting) and network accessibility. Works well for triggering known actions in scriptable apps. Security must be managed (limit allowed users).
* **Launchd/Agent:** *Automation-centric* – great for a hands-off or repetitive processing pipeline. Once set up, the remote Mac can respond to triggers or schedule runs of the app without direct live commands. Ensures the app runs in proper session (since it’s tied to user login) and can even survive reboots (auto-launch on login). However, setup is complex and debugging issues (if the app doesn’t launch) can be tricky, since there may be no immediate feedback. Use this for production-like scenarios where the overhead is justified.
* **VNC/Remote Desktop:** *Interactive and visual* – essentially gives you a remote “seat” at the Mac. Useful for initial configuration or when manual oversight is needed. Not an automated solution by itself (though ARD can send commands). Overhead of streaming a GUI and possibly manual login is a downside. Suitable if you need to actually see the GUI or troubleshoot issues in real time.
* **UI Automation (Accessibility):** *Last resort* – enables automation when the app provides no direct API. High maintenance and can be brittle. Might require combining with one of the above methods (e.g. use SSH or Apple Events to run the script that performs UI automation). Only consider this if the vendor doesn’t offer a proper CLI and you absolutely must automate the GUI workflow.

**Limitations & Other Considerations:** Keep in mind that some applications (particularly those involving GPU or special hardware) might behave differently in a “headless” environment. For instance, if no physical display is attached, some GPU-accelerated apps might not initialize properly. In such cases, using a dummy display adaptor (to simulate a monitor) or the VNC session trick can help ensure the app thinks a display is present. Also, licensing can be a show-stopper: ensure the remote app is activated or in trial mode as needed. Topaz apps typically require you to sign in at least once; running the CLI headless might prompt for login if never done, so you may need to have opened the GUI once locally to authenticate. Finally, consider error handling and feedback: when running remotely, especially in automated mode, capture logs or outputs (Topaz CLI writes to stdout/stderr) so you can monitor progress or failures.

**In summary**, macOS can run GUI apps remotely but you must either *trick the app into thinking a user is present* (by providing a GUI session or using its headless mode). For Topaz Photo AI, the recommended path is to use its built-in CLI (`--cli` mode) for true headless operation. If that’s not viable, leverage Apple’s remote execution capabilities (SSH or Apple Events) to launch it within a normal user session on the remote Mac. Reserve the heavier solutions (persistent launchd jobs, VNC, or UI scripting) for cases where simpler methods fall short. By evaluating these approaches’ trade-offs – ease vs. reliability vs. interactivity – you can choose the method that best fits your remote execution needs and environment constraints.

**Sources:** The approaches and limitations above are drawn from macOS documentation and community expertise, including Apple’s guidelines on remote scripting, Topaz Labs’ own CLI documentation, and forum discussions on launching Mac apps in remote sessions. Community-driven solutions like the Gigapixel UI automator script also illustrate how GUI automation can be achieved when official support is lacking. These resources reinforce the importance of using supported headless modes when available and understanding macOS’s security model when attempting to control GUI apps remotely.








# High-Fidelity Computer Use: Mouse, Keyboard & Screenshots

Warp's `computer_use` crate provides a cross-platform (macOS, Windows, Linux) implementation for low-level system interaction. Compared to Jarvis's current reliance on `pyautogui`, Warp's implementation is significantly more robust, particularly regarding display scaling (DPI) and multi-monitor setups.

## 1. Key Improvements over `pyautogui`

### **DPI Awareness (The "Click Accuracy" Fix)**
*   **Warp:** Uses a `DpiAwarenessGuard` on Windows to opt the thread into `per-monitor-v2` awareness for every operation. This ensures that coordinates are always treated as **physical pixels**, regardless of the host process's settings or the monitor's scaling (e.g., 150% vs 100%).
*   **Jarvis:** `pyautogui` often struggles with Windows scaling, frequently resulting in clicks being offset or "missed" on high-res displays.

### **Multi-Monitor Logic**
*   **Warp:** Explicitly handles the "Virtual Screen" (the coordinate space spanning all monitors). It accounts for monitors positioned to the left or above the primary (which can have negative coordinates).
*   **Jarvis:** Current implementation assumes a single primary coordinate space, which can fail in complex multi-head setups.

### **Reliable Input Dispatch**
*   **Warp:** Uses native Win32 `SendInput` and `SetCursorPos` with explicit `WM_INPUT` visibility. This ensures that even low-level hooks (like those in games or anti-cheat) see the motion, making it feel more "human" and compatible.
*   **Jarvis:** Uses `pyautogui`, which is a wrapper that can sometimes be blocked or ignored by certain applications.

## 2. Advanced Features

### **Screenshot "Snapshots"**
Warp's screenshot tool isn't just a "print screen."
*   **Region-Specific:** Supports capturing specific `ScreenshotRegion`s.
*   **Auto-Scaling:** Includes a `screenshot_utils` pipeline that can auto-resize images to meet a "long-edge" or "total-pixel" budget before sending them to the LLM (saving tokens and latency).
*   **DIB Manipulation:** Uses GDI `BitBlt` and `GetDIBits` directly for high-performance capture without overhead.

### **Keyboard Mastery**
*   **Auto-Shift Bookkeeping:** Warp's `Keyboard` manager tracks if *it* was the one that pressed Shift for a character (e.g., typing 'A'). It ensures that if the layout changes or if multiple keys are pressed, Shift is released at exactly the right time to avoid "stuck keys."
*   **Unicode Fallback:** If a character isn't found in the current keyboard layout (e.g., an emoji or special symbol), it falls back to `KEYEVENTF_UNICODE`, ensuring text is typed correctly regardless of layout.

### **PTY Control**
*   **Bracketed Paste:** For terminal interactions, Warp uses bracketed paste mode to avoid the "auto-indent" mess that happens when you paste code into a running shell or editor like `vim`.

## 3. Why this matters for Jarvis

Jarvis's current "Set-of-Mark" and `mouse_controller.py` approach is a good start, but it's prone to hardware/display variation.

**Implementation Plan for Jarvis:**
1.  **Replace `pyautogui` with Native Bindings:** Move towards using `pywin32` or a compiled Rust extension based on Warp's `computer_use` crate for higher click accuracy.
2.  **DPI-Aware Coordinates:** Implement a DPI-awareness check in the `observation_module.py` to ensure that bounding boxes from the vision model map correctly to screen pixels.
3.  **Screenshot Pre-processing:** Adopt Warp's `get_scale_factor` logic to resize screenshots *before* sending them to the backend, drastically reducing costs.
4.  **Terminal Interaction:** Use the "Bracketed Paste" pattern when Jarvis needs to write multi-line code into a terminal.

## 🔗 References
*   `warp-master/crates/computer_use/src/windows/mouse.rs` (DPI-aware movement)
*   `warp-master/crates/computer_use/src/windows/screenshot.rs` (GDI capture)
*   `warp-master/crates/computer_use/src/windows/keyboard.rs` (Stateful input)
*   `warp-master/crates/computer_use/src/screenshot_utils.rs` (Scaling & Processing)

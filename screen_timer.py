import tkinter as tk
import time
import sys
import math

# --- Configuration ---
TARGET_COLOR = "#00FF00" # Target overlay color (Pure Green)
MAX_ALPHA = 0.7         # How opaque the green becomes (0.0 transparent, 1.0 opaque). Adjust as needed.
FADE_IN_DURATION_SECONDS = 10 # How long it takes to fade in fully (seconds)
FRAMES_PER_SECOND = 30     # Smoothness of the fade animation

# --- Global Variables ---
fade_window = None
current_alpha = 0.0

# --- Functions ---

def update_fade():
    """Gradually increases the alpha (opacity) of the fade window."""
    global current_alpha, fade_window

    # Calculate how much alpha to add in this frame
    total_frames = FADE_IN_DURATION_SECONDS * FRAMES_PER_SECOND
    if total_frames <= 0: total_frames = 1 # Avoid division by zero
    alpha_increment = MAX_ALPHA / total_frames

    current_alpha += alpha_increment

    if current_alpha >= MAX_ALPHA:
        current_alpha = MAX_ALPHA
        print("Fade complete. Press ESC to exit.")
        # No more scheduling needed, just set final alpha
        try:
            # Usingwinfo_exists() to prevent errors if window closed prematurely
            if fade_window and fade_window.winfo_exists():
                 fade_window.attributes('-alpha', current_alpha)
        except tk.TclError as e:
             # Handle specific errors if window is destroyed during attribute set
             if "invalid command name" not in str(e):
                 print(f"Warning: Failed to set final alpha: {e}")
        # Keep window open after fading is complete until ESC is pressed
    else:
        try:
            if fade_window and fade_window.winfo_exists():
                 fade_window.attributes('-alpha', current_alpha)
                 # Schedule the next update
                 delay_ms = int(1000 / FRAMES_PER_SECOND)
                 fade_window.after(delay_ms, update_fade)
        except tk.TclError as e:
            if "invalid command name" not in str(e):
                print(f"Warning: Failed to set alpha during fade: {e}")
            # Stop fading if window is gone
        except Exception as e:
             print(f"Error during fade update: {e}")
             close_app() # Attempt to clean up on unexpected error


def start_screen_fade():
    """Creates the full-screen overlay window and starts the fade."""
    global fade_window, current_alpha
    print("\nTimer finished! Starting screen fade...")

    try:
        fade_window = tk.Tk()

        # --- Window Configuration ---
        # Set background color
        fade_window.configure(bg=TARGET_COLOR)
        # Make it cover the whole screen (borderless)
        fade_window.attributes('-fullscreen', True)
        # Keep it on top of other windows
        fade_window.attributes('-topmost', True)
        # Make it initially fully transparent
        # NOTE: Transparency (-alpha) might behave differently or require
        #       a compositing window manager on Linux/macOS. Works well on Windows.
        fade_window.attributes('-alpha', 0.0)
        # Disable window decorations (title bar, etc.) - often implicit with fullscreen
        fade_window.overrideredirect(True)

        # --- Event Binding ---
        # Bind the Escape key to close the application
        fade_window.bind("<Escape>", lambda event: close_app())
        # You could also bind a click to close it:
        # fade_window.bind("<Button-1>", lambda event: close_app())

        # --- Start Fade ---
        current_alpha = 0.0 # Reset alpha just in case
        print("Fading screen to green... Press ESC to stop/exit.")
        update_fade()      # Start the fade animation loop

        # --- Run Tkinter Event Loop ---
        fade_window.mainloop() # This keeps the window open and responsive

    except tk.TclError as e:
        print(f"\nError creating Tkinter window: {e}")
        print("This might be due to limitations on your OS or Window Manager regarding transparency or fullscreen.")
        sys.exit(1)
    except Exception as e:
        print(f"\nAn unexpected error occurred: {e}")
        sys.exit(1)

def close_app():
    """Destroys the fade window and exits the script."""
    global fade_window
    print("Closing overlay...")
    if fade_window:
        try:
            # Stop any pending 'after' calls to prevent errors after destroy
            after_ids = fade_window.tk.eval('after info').split()
            for after_id in after_ids:
                fade_window.after_cancel(after_id)

            fade_window.destroy()
            fade_window = None # Clear the reference
        except tk.TclError:
            pass # Ignore errors if window is already gone
        except Exception as e:
            print(f"Error during cleanup: {e}")
    sys.exit(0) # Ensure the script terminates cleanly

def run_timer(duration_minutes):
    """Sets the timer and schedules the fade function."""
    if duration_minutes <= 0:
        print("Duration must be positive.")
        return

    duration_seconds = duration_minutes * 60
    print(f"Timer set for {duration_minutes} minutes ({int(duration_seconds)} seconds).")
    print("The screen will slowly turn green when the timer finishes.")
    print("Press Ctrl+C in this terminal to cancel the timer *before* it finishes.")
    print("Once the green overlay appears, press ESC to close it.")

    # We use a dummy hidden Tkinter root window purely to use its 'after' method.
    # This avoids blocking the main thread with time.sleep() and integrates
    # properly with the event loop needed for the fade window later.
    timer_root = tk.Tk()
    timer_root.withdraw() # Hide this dummy window

    try:
        # Schedule the start_screen_fade function to run after the specified delay
        timer_delay_ms = int(duration_seconds * 1000)
        timer_root.after(timer_delay_ms, start_screen_fade)

        # Start the Tkinter event loop for the timer window.
        # This loop will wait until the 'after' event triggers start_screen_fade,
        # or until the window is destroyed (e.g., by Ctrl+C).
        timer_root.mainloop()

    except KeyboardInterrupt:
        print("\nTimer cancelled by user (Ctrl+C).")
        # Cleanly destroy the timer window if it exists
        try:
             if timer_root and timer_root.winfo_exists():
                 timer_root.destroy()
        except tk.TclError:
            pass # Window might already be destroyed
        sys.exit(0)
    except Exception as e:
        print(f"\nAn error occurred during the timer phase: {e}")
        try:
            if timer_root and timer_root.winfo_exists():
                 timer_root.destroy()
        except tk.TclError:
             pass
        sys.exit(1)


# --- Main Execution ---
if __name__ == "__main__":
    while True:
        try:
            minutes_str = input("Enter timer duration in minutes: ")
            minutes = float(minutes_str)
            break # Exit loop if input is a valid number
        except ValueError:
            print("Invalid input. Please enter a number (e.g., 5 or 0.5).")

    run_timer(minutes)
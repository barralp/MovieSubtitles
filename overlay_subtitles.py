import objc
import pysrt
from AppKit import (
    NSApplication,
    NSWindow,
    NSScreen,
    NSColor,
    NSTextField,
    NSFont,
    NSMakeRect,
    NSWindowCollectionBehaviorFullScreenAuxiliary,
    NSWindowCollectionBehaviorCanJoinAllSpaces,
    NSShadow,
    NSAttributedString,
    NSForegroundColorAttributeName,
    NSMutableParagraphStyle,
    NSParagraphStyleAttributeName,
    NSShadowAttributeName
)
from PyObjCTools import AppHelper
import time
import threading
from pynput import mouse, keyboard
from Quartz import CGEventGetLocation

class TransparentOverlayApp:
    def __init__(self, srt_file, start_time=0, first_time=None, last_time=None, scaling_factor=1.0):
        # Parse and rescale subtitles
        subtitles = pysrt.open(srt_file, encoding='latin-1')
        self.subtitles = rescale_subtitles(subtitles, first_time, last_time, scaling_factor)
        self.time_position_in_subtitles = start_time  # Skip subtitles before this time
        self.is_paused = True  # Start in the "paused" state
        self.is_alt_pressed = False  # Track Alt key state
        self.current_index = 0
        self.absolute_start_time_subtitles = time.time() - self.time_position_in_subtitles
        self.loop_time_ = 0.01

        # Determine the initial subtitle index based on start_time
        for i, subtitle in enumerate(self.subtitles):
            if subtitle.start.ordinal / 1000 >= self.time_position_in_subtitles:
                self.current_index = i
                break

        # Access shared application
        self.app = NSApplication.sharedApplication()
        self.app.setActivationPolicy_(2)  # Set app as Agent for overlay behavior

        # Use the main screen dimensions for the overlay
        screen_frame = NSScreen.mainScreen().frame()

        # Create a transparent window
        self.window = NSWindow.alloc().initWithContentRect_styleMask_backing_defer_(
            screen_frame,
            0,  # NSWindowStyleMaskBorderless
            2,  # NSBackingStoreBuffered
            False,
        )

        # Configure the window
        self.window.setOpaque_(False)  # Enable transparency
        self.window.setBackgroundColor_(NSColor.clearColor())  # Set transparent background
        self.window.setIgnoresMouseEvents_(True)  # Allow clicks to pass through
        self.window.setCollectionBehavior_(
            NSWindowCollectionBehaviorFullScreenAuxiliary | NSWindowCollectionBehaviorCanJoinAllSpaces
        )  # Allow joining fullscreen and all spaces
        self.window.setFrame_display_(screen_frame, True)  # Match screen size
        self.window.orderFrontRegardless()  # Ensure the window stays visible

        # Add a text field for subtitles at the center of the screen
        font_size = 52
        subtitle_height = 140
        subtitle_frame = NSMakeRect(
            screen_frame.size.width / 4,  # X position (centered horizontally)
            screen_frame.size.height / 10,  # Y position (10% above the bottom of the screen)
            screen_frame.size.width / 2,  # Width
            subtitle_height,  # Height
        )
        self.subtitle_field = NSTextField.alloc().initWithFrame_(subtitle_frame)
        self.subtitle_field.setBezeled_(False)
        self.subtitle_field.setDrawsBackground_(False)
        self.subtitle_field.setEditable_(False)
        self.subtitle_field.setSelectable_(False)
        self.subtitle_field.setFont_(NSFont.systemFontOfSize_(font_size))  # Adjusted font size
        self.subtitle_field.setTextColor_(NSColor.whiteColor())
        self.subtitle_field.setAlignment_(1)  # Center alignment
        self.subtitle_field.setStringValue_("")

        self.window.contentView().addSubview_(self.subtitle_field)

        print("Transparent subtitle overlay initialized.")
        print(f"Window frame: {screen_frame}")
        print(f"Start time: {self.time_position_in_subtitles}")

        # Start a background thread to keep the window on top
        threading.Thread(target=self.keep_window_on_top, daemon=True).start()

        # Set up global listeners
        self.setup_listeners()

    def keep_window_on_top(self):
        """Ensure the overlay window remains visible and on top."""
        while True:
            AppHelper.callAfter(self.window.orderFrontRegardless)
            time.sleep(1)  # Adjust the interval as needed
    
    def setup_listeners(self):
        """Set up listeners for controlling playback."""
        self.keyboard_listener = keyboard.Listener(on_press=self.handle_key_press, on_release=self.handle_key_release)
        self.mouse_listener = mouse.Listener(on_click=self.handle_click)
        self.keyboard_listener.start()
        self.mouse_listener.start()

    def handle_right_key_press(self, key):
        """Handle keypress events."""
        try:
            if key == keyboard.Key.right:
                self.is_alt_pressed = True
        except AttributeError:
            pass

    def handle_key_press(self, key):
        """Handle keypress events for playback and skipping."""
        try:
            # Check for Alt + Right Arrow Key
            if key == keyboard.Key.right and self.is_alt_pressed:
                self.skip_to_next_subtitle()

            # Check for Alt + Left Arrow Key
            if key == keyboard.Key.left and self.is_alt_pressed:
                self.skip_to_previous_subtitle()

            # Detect Alt key press
            if key == keyboard.Key.alt_l or key == keyboard.Key.alt_r:
                self.is_alt_pressed = True

        except AttributeError:
            pass

    def handle_key_release(self, key):
        """Handle key release events."""
        try:
            # Detect Alt key release
            if key == keyboard.Key.alt_l or key == keyboard.Key.alt_r:
                self.is_alt_pressed = False

        except AttributeError:
            pass

    def handle_click(self, x, y, button, pressed):
        """Handle mouse click to toggle between play and pause states."""
        if not pressed:  # Ignore the release action
            return

        print(f"Mouse clicked at ({x}, {y}) with {button}.")
        if self.is_alt_pressed:
            if self.is_paused:
                # absolute_start_time_subtitles is the absolute time at which a fictitious
                # operator started the subtitle started from scratch
                self.absolute_start_time_subtitles = time.time() - self.time_position_in_subtitles
                print("Resuming subtitles.")
                self.is_paused = False
                threading.Thread(target=self.play_subtitles, daemon=True).start()
            else:
                print("Pausing subtitles.")
                self.is_paused = True
                self.time_position_in_subtitles = time.time() - self.absolute_start_time_subtitles
        else:
            print("Click ignored - press click + alt for action.")
    
    def skip_to_next_subtitle(self):
        self.is_paused = True
        print(f'Skip to subtitle {self.current_index + 1}')
        time.sleep(self.loop_time_ * 5)
        self.current_index += 1
        subtitle = self.subtitles[self.current_index]
        self.time_position_in_subtitles = subtitle.start.ordinal / 1000 + self.loop_time_ / 5
        self.absolute_start_time_subtitles = time.time() - self.time_position_in_subtitles
        self.is_paused = False
        threading.Thread(target=self.play_subtitles, daemon=True).start()

    def skip_to_previous_subtitle(self):
        self.is_paused = True
        print(f'Skip to subtitle {self.current_index - 1}')
        time.sleep(self.loop_time_ * 5)
        self.current_index -= 1
        subtitle = self.subtitles[self.current_index]
        self.time_position_in_subtitles = subtitle.start.ordinal / 1000 + self.loop_time_ / 5
        self.absolute_start_time_subtitles = time.time() - self.time_position_in_subtitles
        self.is_paused = False
        threading.Thread(target=self.play_subtitles, daemon=True).start()

    def play_subtitles(self):
        """Play subtitles with synchronization based on start and end times."""
        print("Playing subtitles.")
        self.time_position_in_subtitles = time.time() - self.absolute_start_time_subtitles

        while self.current_index < len(self.subtitles):
            subtitle = self.subtitles[self.current_index]
            start_time = subtitle.start.ordinal / 1000
            end_time = subtitle.end.ordinal / 1000

            self.time_position_in_subtitles = time.time() - self.absolute_start_time_subtitles

            # Check if paused
            if self.is_paused:
                print("Playback paused.")
                self.time_position_in_subtitles = time.time() - self.absolute_start_time_subtitles
                return

            # If within the subtitle's display range
            if start_time <= self.time_position_in_subtitles < end_time:
                remaining_display_time = end_time - self.time_position_in_subtitles
                print(f"Displaying subtitle {self.current_index + 1}: '{subtitle.text}' for {remaining_display_time:.2f} seconds.")
                self.display_subtitle_with_shadow(subtitle.text)

                # Wait for the remaining display time
                while remaining_display_time > 0:
                    if self.is_paused:
                        print(f"Paused during display of subtitle {self.current_index + 1}. Remaining display: {remaining_display_time:.2f} seconds.")
                        self.time_position_in_subtitles = time.time() - self.absolute_start_time_subtitles
                        return
                    sleep_interval = min(self.loop_time_, remaining_display_time)
                    time.sleep(sleep_interval)
                    self.time_position_in_subtitles = time.time() - self.absolute_start_time_subtitles
                    remaining_display_time = end_time - self.time_position_in_subtitles

                # Clear the subtitle after display
                AppHelper.callAfter(self.subtitle_field.setStringValue_, "")
                print(f"Subtitle {self.current_index + 1} completed.")
                self.current_index += 1

            # If before the subtitle's start time, wait until it begins
            elif self.time_position_in_subtitles < start_time:
                delay = start_time - self.time_position_in_subtitles
                print(f"Waiting for {delay:.2f} seconds before displaying subtitle {self.current_index + 1}.")

                while delay > 0:
                    if self.is_paused:
                        print(f"Paused while waiting for subtitle {self.current_index + 1}. Remaining wait: {delay:.2f} seconds.")
                        self.time_position_in_subtitles = time.time() - self.absolute_start_time_subtitles
                        return
                    sleep_interval = min(self.loop_time_, delay)
                    time.sleep(sleep_interval)
                    self.time_position_in_subtitles = time.time() - self.absolute_start_time_subtitles
                    delay = start_time - self.time_position_in_subtitles

            # If the current time is after the subtitle's end time, move to the next one
            else:
                print(f"Skipped subtitle {self.current_index + 1}: '{subtitle.text}'")
                self.current_index += 1

        print("All subtitles displayed.")
        AppHelper.callAfter(self.subtitle_field.setStringValue_, "")
        
    def display_subtitle_with_shadow(self, text):
        """Apply shadow effect and center alignment to subtitles dynamically."""
        shadow = NSShadow.alloc().init()
        shadow.setShadowColor_(NSColor.blackColor())
        shadow.setShadowOffset_((0, -1))  # Slight downward shadow
        shadow.setShadowBlurRadius_(2.0)  # Slim blur radius

        # Create paragraph style for center alignment
        paragraph_style = NSMutableParagraphStyle.alloc().init()
        paragraph_style.setAlignment_(1)  # Center alignment

        # Create attributes with shadow and alignment
        attributes = {
            NSForegroundColorAttributeName: NSColor.whiteColor(),
            NSShadowAttributeName: shadow,
            NSParagraphStyleAttributeName: paragraph_style,  # Add center alignment
        }

        # Create an attributed string with shadow and text
        attributed_string = NSAttributedString.alloc().initWithString_attributes_(
            text, attributes
        )

        # Apply the attributed string to the text field
        AppHelper.callAfter(self.subtitle_field.setAttributedStringValue_, attributed_string)

    def run(self):
        threading.Thread(target=self.play_subtitles, daemon=True).start()
        AppHelper.runEventLoop()

def rescale_subtitles(subtitles, first_time=None, last_time=None, scaling_factor=1.0):
    """Rescale subtitle timings. The presence of last_time overrides the scaling_factor."""
    rescaled_subtitles = subtitles.copy()

    original_start = subtitles[0].start.ordinal / 1000
    original_end = subtitles[-1].end.ordinal / 1000

    if first_time is None:
        first_time = original_start

    if last_time:
        scaling_factor = (last_time - first_time) / (original_end - original_start)

    for subtitle in rescaled_subtitles:
        subtitle.start.ordinal = int(((subtitle.start.ordinal / 1000 - original_start) * scaling_factor + first_time) * 1000)
        subtitle.end.ordinal = int(((subtitle.end.ordinal / 1000 - original_start) * scaling_factor + first_time) * 1000)

    return rescaled_subtitles

if __name__ == "__main__":
    app = TransparentOverlayApp(
        srt_file="diner_de_cons.srt",
        start_time=1080,  # Sync with the movie start
        # first_time=88,  # Adjust start time of the first subtitle
        # last_time=4803,  # Scale subtitles to end at this time
        # scaling_factor=1.0,  # Default scaling
    )
    app.run()
from overlay_subtitles import TransparentOverlayApp


# Application description:
# This script launches a transparent subtitle overlay application for displaying .srt subtitles
# synchronized with a movie or video. The application supports several interactive commands
# for controlling subtitle playback.

# Commands:
# - Alt + Left Click:
#     Toggles between pausing and resuming subtitle playback.
# - Alt + Right Arrow:
#     Skips to the next subtitle.
# - Alt + Left Arrow:
#     Skips to the previous subtitle.

# Parameters description:
# - srt_file: The path to the subtitle file in .srt format.
#             This is a required parameter and should point to a valid file.
# - start_time: (Optional, default 0) The time (in seconds) at which the program starts in the
#               subtitle file.
# - first_time: (Optional, default is time of the first subtitle) The new start time for the first
#               subtitle after rescaling. If specified, rescaling will adjust the timeline to this value.
# - last_time: (Optional, default is time of the last subtitle) The new end time for the last subtitle
#               after rescaling. If specified, the timeline will be scaled to fit within this duration.
# - scaling_factor: (Optional) A multiplier to adjust the overall timing of subtitles.
#                   Default is 1.0 (no scaling). This parameter is bypassed if last_time is non zero

# Operation
# Prepare your movie at start_time (by default 0) and then press atl + click on the play button to start
# syncronously the movie and the subtitle. If there is a constant offset in timing then use first_time to
# readjust. If the first dialog in the movie appears at 14 seconds, then first time should be set at 14 seconds.
# last_time or scaling_factor are two ways to take care of linear drift over time in the movie. If the last
# subtitle appears at 4807 seconds, then last_time should be set at that value. Otherwise use scaling factor
# to slow down (< 1) or accelerate (> 1) the prompt of the subtitles.
# If the subtitles go out of sync during the movie, simply press alt + left or right arrow to move to the next
# or previous subtitle.
# https://www.opensubtitles.org/en/search/subs is a good place to find subtitles.

def main():
    app = TransparentOverlayApp(
        srt_file="test_subtitles.srt",
        start_time=50,
        first_time=None,
        last_time=None,
        scaling_factor=1.0
    )
    app.run()

if __name__ == "__main__":
    main()
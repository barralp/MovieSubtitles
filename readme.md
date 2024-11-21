# Transparent Subtitle Overlay Application

This Python application provides a transparent subtitle overlay synchronized with your movie or video. It allows for interactive subtitle controls using keyboard and mouse shortcuts.

## Features
- Transparent always-on-top subtitle overlay.
- Control playback with intuitive commands:
  - **Alt + Left Click**: Toggle pause/resume.
  - **Alt + Right Arrow**: Skip to the next subtitle.
  - **Alt + Left Arrow**: Skip to the previous subtitle.
- Customizable parameters:
  - `srt_file`: Path to the `.srt` subtitle file.
  - `start_time`: Sync subtitles with your movie (in seconds).
    - Adjust start and end times.
    - Scale subtitle timings to correct drift.

## Installation
1. **Clone the repository**:
   ```bash
   git clone https://github.com/barralp/MovieSubtitles.git
   cd your-repo-name# MovieSubtitles

2. **Set Up a Virtual Environment**:
   - On macOS/Linux:
     ```bash
     python -m venv .venv
     source .venv/bin/activate
     ```
   - On Windows (script untested):
     ```bash
     python -m venv .venv
     .venv\Scripts\activate
     ```

3. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt

4. **Run**:
   ```bash
   python run.py


## Application Description
This script launches a transparent subtitle overlay application for displaying `.srt` subtitles synchronized with a movie or video. The application supports several interactive commands for controlling subtitle playback.

---

## Commands
- **Alt + Left Click**: Toggles between pausing and resuming subtitle playback.
- **Alt + Right Arrow**: Skips to the next subtitle.
- **Alt + Left Arrow**: Skips to the previous subtitle.

---

## Parameters Description
- **`srt_file`**: The path to the subtitle file in `.srt` format. This is a required parameter and should point to a valid file.
- **`start_time`**: (Optional, default: `0`) The time (in seconds) at which the program starts in the subtitle file.
- **`first_time`**: (Optional, default: time of the first subtitle) The new start time for the first subtitle after rescaling. If specified, rescaling will adjust the timeline to this value.
- **`last_time`**: (Optional, default: time of the last subtitle) The new end time for the last subtitle after rescaling. If specified, the timeline will be scaled to fit within this duration.
- **`scaling_factor`**: (Optional) A multiplier to adjust the overall timing of subtitles. Default is `1.0` (no scaling). This parameter is bypassed if `last_time` is non-zero.

---

## Operation
Prepare your movie at `start_time` (by default `0`) and then press **Alt + Left Click** on the play button to start the movie and subtitles synchronously. 

If there is a constant offset in timing, then use `first_time` to readjust. For example if the first dialog in the movie appears at 14 seconds, then `first_time` should be set to 14 seconds.

`last_time` or `scaling_factor` are two ways to account for linear drift over time in the movie:
- If the last subtitle appears at 4807 seconds, then `last_time` should be set to that value.
- Alternatively, use `scaling_factor` to slow down (`< 1`) or speed up (`> 1`) the subtitle timing.

If the subtitles go out of sync during the movie, simply press:
- **Alt + Right Arrow**: To move to the next subtitle.
- **Alt + Left Arrow**: To move to the previous subtitle.

[OpenSubtitles](https://www.opensubtitles.org/en/search/subs) is a good place to find subtitles.
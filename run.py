from overlay_subtitles import TransparentOverlayApp

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
from __future__ import annotations

from pathlib import Path

from moviepy import (
    AudioFileClip,
    CompositeAudioClip,
    CompositeVideoClip,
    ImageClip,
    afx,
    concatenate_audioclips,
    concatenate_videoclips,
    vfx,
)

from ..config import BACKGROUND_MUSIC_PATH, DEFAULT_FPS, DEFAULT_VIDEO_SIZE


class MovieComposer:
    def compose(
        self,
        scene_frames: list[str],
        subtitle_frames: list[str],
        narration_audio: list[str],
        durations: list[float],
        output_path: Path,
    ) -> float:
        clips = []
        audio_clips = [AudioFileClip(path) for path in narration_audio]
        music = None
        try:
            for index, frame_path in enumerate(scene_frames):
                duration = durations[index]
                base = (
                    ImageClip(frame_path)
                    .with_duration(duration)
                    .resized(DEFAULT_VIDEO_SIZE)
                    .with_position("center")
                )
                subtitle = ImageClip(subtitle_frames[index]).with_duration(duration).with_position(("center", "bottom"))
                clip = CompositeVideoClip([base, subtitle], size=DEFAULT_VIDEO_SIZE).with_duration(duration)
                if index:
                    clip = clip.with_effects([vfx.CrossFadeIn(0.35)])
                clips.append(clip)

            final_video = concatenate_videoclips(clips, method="compose", padding=-0.35)
            narration = concatenate_audioclips(audio_clips)
            audio_tracks = [narration]
            if BACKGROUND_MUSIC_PATH and Path(BACKGROUND_MUSIC_PATH).exists():
                music = AudioFileClip(BACKGROUND_MUSIC_PATH).with_effects(
                    [afx.AudioLoop(duration=narration.duration), afx.MultiplyVolume(0.08)]
                )
                audio_tracks.append(music)
            final_video = final_video.with_audio(CompositeAudioClip(audio_tracks)).with_duration(narration.duration)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            final_video.write_videofile(
                str(output_path),
                fps=DEFAULT_FPS,
                codec="libx264",
                audio_codec="aac",
                preset="ultrafast",
                threads=4,
                ffmpeg_params=["-movflags", "+faststart"],
                logger=None,
            )
            return float(narration.duration)
        finally:
            for clip in clips:
                clip.close()
            for audio in audio_clips:
                audio.close()
            if music:
                music.close()

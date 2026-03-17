---
name: suno-music
description: Generate music using Suno AI through dmxapi.cn API. Supports two modes - inspiration mode (generate from description) and custom mode (generate from lyrics, title, and style tags). Use when users request music generation, AI music creation, or mention Suno. Automatically polls task status until completion and returns audio URLs and cover images. Requires DMX_API_KEY or 302AI_API_KEY environment variable.
---

# Suno Music Generation

Generate AI music using Suno through the dmxapi.cn API.

## Environment Setup

**Required**: Set API key before use:

```bash
export DMX_API_KEY="your_api_key_here"
# OR
export 302AI_API_KEY="your_api_key_here"
```

**Default output directory**: `./assets/audios/` (auto-created)

## Generation Modes

### Inspiration Mode

Generate music from a text description. Best for quick creative exploration.

```bash
python3 scripts/generate_music.py \
  --mode inspiration \
  --description "中国风trap音乐，融合古筝和现代节奏" \
  --instrumental \
  --download
```

Parameters:
- `--description, -d`: Music description (required)
- `--instrumental, -i`: Generate instrumental (no lyrics)
- `--model`: Model version (default: chirp-v5)
- `--download`: Download audio files
- `--output, -o`: Output directory for downloads

### Custom Mode

Generate music with specific lyrics, title, and style tags. Best for precise control.

```bash
python3 scripts/generate_music.py \
  --mode custom \
  --lyrics "歌词内容..." \
  --title "歌曲标题" \
  --tags "pop,upbeat,romantic" \
  --download
```

Parameters:
- `--lyrics, -l`: Song lyrics (required)
- `--title, -t`: Song title (required)
- `--tags`: Style tags, comma-separated (optional)
- `--model`: Model version (default: chirp-v5)
- `--download`: Download audio files
- `--output, -o`: Output directory for downloads

## Available Models

- `chirp-v5` (default, latest)
- `chirp-v4`
- `chirp-v3`

## Available Style Tags

Common tags: `pop`, `rock`, `electronic`, `classical`, `jazz`, `hip-hop`, `r&b`, `country`, `folk`, `blues`, `reggae`, `latin`, `ambient`, `cinematic`, `lo-fi`, `trap`, `house`, `techno`, `dubstep`, `romantic`, `upbeat`, `melancholic`, `energetic`, `peaceful`, `dramatic`

## Output Format

The script returns JSON with audio URLs and cover images:

```json
[
  {
    "title": "Song Title",
    "duration": 180,
    "audio_url": "https://...",
    "image_url": "https://..."
  }
]
```

## Python API Usage

```python
from scripts.generate_music import SunoMusicGenerator

generator = SunoMusicGenerator()

# Inspiration mode
results = generator.generate_inspiration(
    description="轻松的爵士乐",
    make_instrumental=False,
    model="chirp-v5"
)

# Custom mode
results = generator.generate_custom(
    lyrics="歌词内容...",
    title="我的歌",
    tags="pop,upbeat",
    model="chirp-v5"
)

# Download audio
for result in results:
    generator.download_audio(
        audio_url=result["audio_url"],
        filename=f"{result['title']}.mp3"
    )
```

## Task Polling

The script automatically polls task status every 3 seconds for up to 60 attempts (3 minutes total). Progress is displayed during generation.

## Error Handling

Common errors:
- Missing API key: Set `DMX_API_KEY` or `302AI_API_KEY`
- Task timeout: Generation took longer than 3 minutes
- Task failed: API returned failure status
- Invalid model: Use one of the supported models

## Tips

- Use inspiration mode for quick experimentation
- Use custom mode when you have specific lyrics
- Combine multiple style tags for unique sounds
- Enable `--download` to save files locally
- Suno typically generates 2 variations per request

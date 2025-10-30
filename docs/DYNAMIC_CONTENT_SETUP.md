# Dynamic Content System Setup Guide

## Overview

The system now **dynamically analyzes each video's content** and selects:
- **Music** that matches the mood/theme
- **Voice** that matches the content style
- **All automatically** - no hard-coding!

## How It Works

1. **Content Analysis**: AI analyzes the topic and script to determine:
   - Mood (serious, fun, mysterious, upbeat, etc.)
   - Genre (educational, entertainment, news, etc.)
   - Energy level (low, medium, high)
   - Voice style (formal, casual, energetic, calm, etc.)
   - Music style (ambient, upbeat, dramatic, minimalist, etc.)

2. **Dynamic Music Selection**: Based on analysis, selects appropriate music from your library

3. **Dynamic Voice Selection**: Based on analysis, selects appropriate voice accent/tone

## Setting Up Music Library

### Option 1: Manual Organization (Recommended - Free!)

1. Create music folders:
   ```
   assets/music/
   ├── ambient/
   ├── upbeat/
   ├── dramatic/
   ├── minimalist/
   ├── cinematic/
   ├── electronic/
   ├── acoustic/
   ├── orchestral/
   ├── suspenseful/
   └── inspiring/
   ```

2. Download free music from:
   - **YouTube Audio Library**: https://studio.youtube.com/channel/UC.../music
     - Free, royalty-free, no attribution needed for YouTube
     - Filter by genre, mood, duration
   
   - **Incompetech (Kevin MacLeod)**: https://incompetech.com/music/
     - All CC licenses, free with attribution
     - Great selection of cinematic music
   
   - **Freesound.org**: https://freesound.org/
     - Free sound effects and music
     - Various licenses (check each file)

3. Place music files in appropriate style folders:
   - Upbeat music → `assets/music/upbeat/`
   - Dramatic music → `assets/music/dramatic/`
   - Ambient music → `assets/music/ambient/`
   - etc.

### Option 2: Automatic Download (Future)

We can integrate Freesound.org API for automatic music downloads based on content analysis.

## How Content Analysis Works

### Example 1: Medical Topic
- **Topic**: "10 Weird Medical Conditions"
- **Analysis**: 
  - Mood: serious
  - Music: ambient
  - Voice: calm, authoritative
- **Result**: Calm British voice, ambient background music

### Example 2: Wealth Topic
- **Topic**: "The 1% of population that controls 40% of wealth"
- **Analysis**:
  - Mood: inspirational
  - Music: upbeat
  - Voice: energetic
- **Result**: Energetic American voice, upbeat background music

### Example 3: Dark History Topic
- **Topic**: "The Dark History Behind Your Favorite Products"
- **Analysis**:
  - Mood: mysterious
  - Music: dramatic
  - Voice: dramatic
- **Result**: Dramatic British voice, dramatic/suspenseful background music

## Voice Styles Available

- **Formal**: American accent, professional tone
- **Casual**: Australian accent, friendly tone
- **Energetic**: American accent, upbeat tone
- **Calm**: British accent, soothing tone
- **Authoritative**: American accent, confident tone
- **Friendly**: Australian accent, warm tone
- **Dramatic**: British accent, expressive tone

## Music Styles Available

- **ambient**: Soft, background music
- **upbeat**: Energetic, positive music
- **dramatic**: Intense, emotional music
- **minimalist**: Simple, clean music
- **cinematic**: Movie-like, epic music
- **electronic**: Modern, digital music
- **acoustic**: Natural, organic music
- **orchestral**: Classical, orchestral music
- **suspenseful**: Tense, mysterious music
- **inspiring**: Motivational, uplifting music

## Testing

1. Generate a video with a medical topic → Should get calm voice + ambient music
2. Generate a video with a wealth/money topic → Should get energetic voice + upbeat music
3. Generate a video with dark history → Should get dramatic voice + dramatic music

## Customization

You can adjust the analysis in `core/content_analyzer.py`:
- Add more mood categories
- Add more music styles
- Adjust voice selection logic

## Notes

- If no music is found in the library, video will have voiceover only (still works!)
- System falls back to keyword-based analysis if AI analysis fails
- All music selection is automatic - no manual intervention needed!


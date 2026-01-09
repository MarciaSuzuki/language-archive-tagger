# Language Archive Tagger - Deployment Guide

## Overview

This package contains the Language Archive Tagger application with 600 segments across 10 stories, ready for your Tripod Workshop.

## Files Included

| File | Description |
|------|-------------|
| `language_archive_tagger.html` | Complete app (single file, no audio) |
| `data.js` | Segment data with AI suggestions |
| `english_story_scripts.md` | Story scripts for audio generation |
| `generate_audio_elevenlabs.py` | Full audio generation script |
| `generate_audio_by_story.py` | Generate audio one story at a time |

---

## Part 1: Deploy to GitHub Pages (Free Hosting)

### Step 1: Create a GitHub Repository

1. Go to [github.com](https://github.com) and sign in
2. Click the **+** icon (top right) → **New repository**
3. Name it: `language-archive-tagger`
4. Select **Public**
5. Check **Add a README file**
6. Click **Create repository**

### Step 2: Upload the HTML File

1. In your new repository, click **Add file** → **Upload files**
2. Drag `language_archive_tagger.html` into the upload area
3. **Important**: Rename it to `index.html` before uploading, OR:
   - After uploading, click the file → pencil icon (edit)
   - Click the filename and rename to `index.html`
4. Click **Commit changes**

### Step 3: Enable GitHub Pages

1. Go to repository **Settings** (tab at top)
2. Scroll down to **Pages** (left sidebar)
3. Under "Source", select **Deploy from a branch**
4. Select branch: **main**
5. Select folder: **/ (root)**
6. Click **Save**

### Step 4: Access Your App

Wait 1-2 minutes, then your app will be live at:
```
https://YOUR-USERNAME.github.io/language-archive-tagger/
```

Share this URL with your workshop participants!

---

## Part 2: Generate Audio with ElevenLabs

### Prerequisites

1. Create an ElevenLabs account at [elevenlabs.io](https://elevenlabs.io)
2. Get your API key from the profile settings
3. Install Python 3.8+ on your computer

### Setup

```bash
# Install the ElevenLabs package
pip install elevenlabs

# Set your API key (Linux/Mac)
export ELEVENLABS_API_KEY="your-api-key-here"

# Set your API key (Windows Command Prompt)
set ELEVENLABS_API_KEY=your-api-key-here

# Set your API key (Windows PowerShell)
$env:ELEVENLABS_API_KEY="your-api-key-here"
```

### Option A: Generate All Audio at Once

```bash
python generate_audio_elevenlabs.py --script english_story_scripts.md
```

This generates all 600 segments (~24,000 characters). Requires ElevenLabs Starter plan ($5/month for 30,000 characters).

### Option B: Generate One Story at a Time (Recommended)

```bash
# Generate Story 1 (segments 0-59)
python generate_audio_by_story.py --story 1

# Generate Story 2 (segments 60-119)
python generate_audio_by_story.py --story 2

# ... and so on for stories 3-10
```

Each story uses ~2,400 characters. This lets you stay within the free tier (10,000 chars/month) by generating 4 stories per month.

### Voice Options

List available voices:
```bash
python generate_audio_elevenlabs.py --list-voices
```

Use a specific voice:
```bash
python generate_audio_by_story.py --story 1 --voice "George"
```

Recommended voices for West African English storytelling:
- **Daniel** (British, warm)
- **George** (British, narrative)
- **Clyde** (American, storytelling)

### Output

Audio files are saved to the `audio/` folder:
- `segment_0.mp3`
- `segment_1.mp3`
- ... through `segment_599.mp3`

---

## Part 3: Deploy with Audio Files

Once you have the audio files, you have two options:

### Option A: GitHub Pages (for small file sizes)

1. Create an `audio` folder in your repository
2. Upload all MP3 files to that folder
3. The app will automatically find them

**Note**: GitHub has a 100MB file limit and repositories over 1GB may be slow.

### Option B: External Audio Hosting (Recommended)

Host audio files separately on:
- **Google Drive** (make files public)
- **Dropbox** (use direct links)
- **Amazon S3** (reliable, pay-per-use)
- **Cloudflare R2** (free egress)

Then modify `data.js` to use full URLs:
```javascript
"audio_file": "https://your-host.com/audio/segment_0.mp3"
```

---

## Part 4: Customization

### Change the Number of Segments

Edit the HTML file and find this line in the JavaScript:
```javascript
let segments = WORKSHOP_DATA;
```

To use only the first 60 segments (Story 1):
```javascript
let segments = WORKSHOP_DATA.slice(0, 60);
```

To use stories 1-3 (180 segments):
```javascript
let segments = WORKSHOP_DATA.slice(0, 180);
```

### Filter by Story

```javascript
// Only Story 5: The Harvest Festival
let segments = WORKSHOP_DATA.filter(s => s.story === 5);
```

---

## Troubleshooting

### "Audio not playing"
- Check that audio files are in the correct location
- Verify file names match exactly (segment_0.mp3, not segment_00.mp3)
- Check browser console for errors (F12 → Console)

### "GitHub Pages not working"
- Make sure the file is named `index.html`
- Check that Pages is enabled in Settings
- Wait 2-3 minutes for deployment
- Clear your browser cache

### "ElevenLabs quota exceeded"
- Check your usage at elevenlabs.io
- Use the by-story script to generate in batches
- Consider upgrading to Starter plan ($5/month)

---

## Cost Summary

| Item | Cost |
|------|------|
| GitHub Pages hosting | Free |
| ElevenLabs (4 stories/month) | Free |
| ElevenLabs (all 10 stories) | $5 one-time |
| External audio hosting | Varies |

---

## Support

For questions about the Tripod Method or this application, contact the Ready Vessels Project team.

#!/usr/bin/env python3
"""
Generate all 600 audio segments using Joe's voice
==================================================

SETUP:
1. pip install elevenlabs
2. export ELEVENLABS_API_KEY="your-api-key"
3. python generate_audio_joe.py

That's it! The script will generate all 600 MP3 files.
"""

import os
import sys
import time
import re

try:
    from elevenlabs import ElevenLabs, VoiceSettings
except ImportError:
    print("Please run: pip install elevenlabs")
    sys.exit(1)

# Joe's voice ID
VOICE_ID = "LEvd0YiWkwZ6hTZOmdVE"

def extract_segments(script_path):
    """Extract all segments from the story script"""
    with open(script_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    segments = []
    current_story = 0
    
    for line in content.split('\n'):
        if line.startswith('## Story'):
            match = re.search(r'Story (\d+)', line)
            if match:
                current_story = int(match.group(1))
        
        match = re.match(r'^(\d+)\.\s+(.+)$', line.strip())
        if match:
            num = int(match.group(1))
            text = match.group(2)
            global_id = (current_story - 1) * 60 + num - 1
            segments.append({'id': global_id, 'text': text})
    
    return segments


def main():
    # Check API key
    api_key = os.environ.get("ELEVENLABS_API_KEY")
    if not api_key:
        print("ERROR: Set ELEVENLABS_API_KEY environment variable")
        print("  export ELEVENLABS_API_KEY='your-key-here'")
        sys.exit(1)
    
    # Check script file
    script_path = "english_story_scripts.md"
    if not os.path.exists(script_path):
        print(f"ERROR: {script_path} not found in current directory")
        sys.exit(1)
    
    # Initialize client
    client = ElevenLabs(api_key=api_key)
    
    # Extract segments
    segments = extract_segments(script_path)
    total_chars = sum(len(s['text']) for s in segments)
    
    print("=" * 50)
    print("Language Archive Tagger - Audio Generator")
    print("=" * 50)
    print(f"Voice: Joe (ID: {VOICE_ID})")
    print(f"Segments: {len(segments)}")
    print(f"Characters: ~{total_chars:,}")
    print("=" * 50)
    
    # Check for existing files
    os.makedirs("audio", exist_ok=True)
    existing = [f for f in os.listdir("audio") if f.endswith(".mp3")]
    if existing:
        print(f"Found {len(existing)} existing files (will skip)")
    
    response = input("\nGenerate audio? (y/n): ")
    if response.lower() != 'y':
        print("Aborted.")
        return
    
    print("\nGenerating audio...")
    print("-" * 50)
    
    success = 0
    failed = 0
    
    for i, seg in enumerate(segments):
        output_path = f"audio/segment_{seg['id']}.mp3"
        
        if os.path.exists(output_path):
            print(f"[{i+1}/600] Skip (exists): segment_{seg['id']}.mp3")
            success += 1
            continue
        
        print(f"[{i+1}/600] {seg['text'][:50]}...")
        
        try:
            audio = client.text_to_speech.convert(
                voice_id=VOICE_ID,
                text=seg['text'],
                model_id="eleven_multilingual_v2",
                voice_settings=VoiceSettings(
                    stability=0.5,
                    similarity_boost=0.75,
                    style=0.0,
                    use_speaker_boost=True
                )
            )
            
            with open(output_path, 'wb') as f:
                for chunk in audio:
                    f.write(chunk)
            
            success += 1
            time.sleep(0.3)  # Small delay to be nice to the API
            
        except Exception as e:
            print(f"  ERROR: {e}")
            failed += 1
            time.sleep(2)
    
    print("-" * 50)
    print(f"\nComplete!")
    print(f"  Success: {success}")
    print(f"  Failed: {failed}")
    print(f"  Audio files: audio/segment_0.mp3 through audio/segment_599.mp3")


if __name__ == "__main__":
    main()

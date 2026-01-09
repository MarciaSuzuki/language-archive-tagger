#!/usr/bin/env python3
"""
Generate audio by story using ElevenLabs API
=============================================

This is a simpler version that processes one story at a time.
Easier to manage your character quota.

QUICK START:
1. pip install elevenlabs
2. export ELEVENLABS_API_KEY="your-key"
3. python generate_audio_by_story.py --story 1

Each story = 60 segments ≈ 2,400 characters
"""

import os
import sys
import time
import argparse
import re

try:
    from elevenlabs import ElevenLabs, VoiceSettings
except ImportError:
    print("Please run: pip install elevenlabs")
    sys.exit(1)

STORY_TITLES = [
    "The Hunter and the Lion",
    "The Fisherman's Journey",
    "The Wise Elder's Advice",
    "The Lost Child",
    "The Harvest Festival",
    "The Drought and the Prayer",
    "The Wedding Celebration",
    "The Healer's Gift",
    "The Great Storm",
    "The New Village"
]

def extract_story_segments(script_path, story_num):
    """Extract segments for a specific story"""
    with open(script_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    segments = []
    current_story = 0
    
    for line in content.split('\n'):
        if line.startswith('## Story'):
            match = re.search(r'Story (\d+)', line)
            if match:
                current_story = int(match.group(1))
        
        if current_story == story_num:
            match = re.match(r'^(\d+)\.\s+(.+)$', line.strip())
            if match:
                num = int(match.group(1))
                text = match.group(2)
                global_id = (story_num - 1) * 60 + num - 1
                segments.append({'id': global_id, 'text': text})
    
    return segments


def main():
    parser = argparse.ArgumentParser(description='Generate audio for one story')
    parser.add_argument('--story', type=int, required=True, help='Story number (1-10)')
    parser.add_argument('--voice', type=str, default='Daniel', help='Voice name')
    parser.add_argument('--script', type=str, default='english_story_scripts.md')
    parser.add_argument('--output-dir', type=str, default='audio')
    args = parser.parse_args()
    
    if not 1 <= args.story <= 10:
        print("ERROR: Story must be 1-10")
        sys.exit(1)
    
    api_key = os.environ.get("ELEVENLABS_API_KEY")
    if not api_key:
        print("ERROR: Set ELEVENLABS_API_KEY environment variable")
        sys.exit(1)
    
    client = ElevenLabs(api_key=api_key)
    
    # Get voice ID
    voices = client.voices.get_all()
    voice_id = None
    for v in voices.voices:
        if v.name.lower() == args.voice.lower():
            voice_id = v.voice_id
            break
    
    if not voice_id:
        print(f"Voice '{args.voice}' not found. Available voices:")
        for v in voices.voices:
            print(f"  - {v.name}")
        sys.exit(1)
    
    # Extract segments
    segments = extract_story_segments(args.script, args.story)
    if not segments:
        print(f"No segments found for story {args.story}")
        sys.exit(1)
    
    total_chars = sum(len(s['text']) for s in segments)
    
    print(f"\nStory {args.story}: {STORY_TITLES[args.story-1]}")
    print(f"Segments: {len(segments)}")
    print(f"Characters: ~{total_chars:,}")
    print(f"Voice: {args.voice}")
    print()
    
    response = input("Generate audio? (y/n): ")
    if response.lower() != 'y':
        return
    
    os.makedirs(args.output_dir, exist_ok=True)
    
    for i, seg in enumerate(segments):
        output_path = os.path.join(args.output_dir, f"segment_{seg['id']}.mp3")
        
        if os.path.exists(output_path):
            print(f"[{i+1}/60] Skip (exists): segment_{seg['id']}.mp3")
            continue
        
        print(f"[{i+1}/60] {seg['text'][:40]}...")
        
        try:
            audio = client.text_to_speech.convert(
                voice_id=voice_id,
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
            
            time.sleep(0.5)
            
        except Exception as e:
            print(f"  ERROR: {e}")
            time.sleep(5)
    
    print(f"\nDone! Story {args.story} audio saved to {args.output_dir}/")


if __name__ == "__main__":
    main()

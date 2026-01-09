#!/usr/bin/env python3
"""
Generate audio segments using ElevenLabs API
============================================

This script reads the story scripts and generates individual MP3 files
for each segment using ElevenLabs text-to-speech.

SETUP:
1. Install the ElevenLabs package:
   pip install elevenlabs

2. Get your API key from https://elevenlabs.io
   
3. Set your API key as an environment variable:
   export ELEVENLABS_API_KEY="your-api-key-here"
   
   Or on Windows:
   set ELEVENLABS_API_KEY=your-api-key-here

4. Run the script:
   python generate_audio_elevenlabs.py

VOICE SELECTION:
- The script uses a default voice, but you can change it
- To list available voices, run with --list-voices
- To use a specific voice, run with --voice "Voice Name"

COST ESTIMATE:
- ~600 segments × ~8 words average × ~5 characters/word = ~24,000 characters
- ElevenLabs free tier: 10,000 characters/month
- Starter plan ($5/month): 30,000 characters/month
- You may need the Starter plan for all 600 segments

OUTPUT:
- Creates an 'audio' folder with segment_0.mp3 through segment_599.mp3
"""

import os
import sys
import time
import argparse
import re

try:
    from elevenlabs import ElevenLabs, Voice, VoiceSettings
except ImportError:
    print("ERROR: elevenlabs package not installed.")
    print("Please run: pip install elevenlabs")
    sys.exit(1)


def get_api_key():
    """Get API key from environment variable"""
    api_key = os.environ.get("ELEVENLABS_API_KEY")
    if not api_key:
        print("ERROR: ELEVENLABS_API_KEY environment variable not set.")
        print("\nTo set it:")
        print("  Linux/Mac: export ELEVENLABS_API_KEY='your-key-here'")
        print("  Windows:   set ELEVENLABS_API_KEY=your-key-here")
        print("\nGet your API key at: https://elevenlabs.io")
        sys.exit(1)
    return api_key


def list_voices(client):
    """List all available voices"""
    print("\nAvailable voices:")
    print("-" * 50)
    voices = client.voices.get_all()
    for voice in voices.voices:
        print(f"  {voice.name} (ID: {voice.voice_id})")
        if voice.labels:
            labels = ", ".join([f"{k}: {v}" for k, v in voice.labels.items()])
            print(f"    Labels: {labels}")
    print("-" * 50)


def extract_segments(script_path):
    """Extract all segments from the story script"""
    with open(script_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    segments = []
    current_story = 0
    
    lines = content.split('\n')
    for line in lines:
        # Check for story headers
        if line.startswith('## Story'):
            match = re.search(r'Story (\d+)', line)
            if match:
                current_story = int(match.group(1))
        
        # Check for numbered sentences
        match = re.match(r'^(\d+)\.\s+(.+)$', line.strip())
        if match:
            num = int(match.group(1))
            text = match.group(2)
            global_id = (current_story - 1) * 60 + num - 1
            segments.append({
                'id': global_id,
                'story': current_story,
                'text': text
            })
    
    return segments


def generate_audio(client, text, voice_id, output_path, stability=0.5, similarity=0.75):
    """Generate audio for a single segment"""
    audio = client.text_to_speech.convert(
        voice_id=voice_id,
        text=text,
        model_id="eleven_multilingual_v2",
        voice_settings=VoiceSettings(
            stability=stability,
            similarity_boost=similarity,
            style=0.0,
            use_speaker_boost=True
        )
    )
    
    # Write audio to file
    with open(output_path, 'wb') as f:
        for chunk in audio:
            f.write(chunk)


def main():
    parser = argparse.ArgumentParser(description='Generate audio segments using ElevenLabs')
    parser.add_argument('--list-voices', action='store_true', help='List available voices')
    parser.add_argument('--voice', type=str, default='Daniel', help='Voice name to use (default: Daniel)')
    parser.add_argument('--voice-id', type=str, help='Voice ID to use (overrides --voice)')
    parser.add_argument('--script', type=str, default='english_story_scripts.md', help='Path to story scripts')
    parser.add_argument('--output-dir', type=str, default='audio', help='Output directory for audio files')
    parser.add_argument('--start', type=int, default=0, help='Start from segment number')
    parser.add_argument('--end', type=int, default=None, help='End at segment number')
    parser.add_argument('--stability', type=float, default=0.5, help='Voice stability (0-1)')
    parser.add_argument('--similarity', type=float, default=0.75, help='Voice similarity boost (0-1)')
    parser.add_argument('--delay', type=float, default=0.5, help='Delay between API calls in seconds')
    args = parser.parse_args()
    
    # Initialize client
    api_key = get_api_key()
    client = ElevenLabs(api_key=api_key)
    
    # List voices if requested
    if args.list_voices:
        list_voices(client)
        return
    
    # Check script file exists
    if not os.path.exists(args.script):
        print(f"ERROR: Script file not found: {args.script}")
        print("Make sure english_story_scripts.md is in the current directory.")
        sys.exit(1)
    
    # Get voice ID
    voice_id = args.voice_id
    if not voice_id:
        # Look up voice by name
        voices = client.voices.get_all()
        voice_match = None
        for voice in voices.voices:
            if voice.name.lower() == args.voice.lower():
                voice_match = voice
                break
        
        if not voice_match:
            print(f"ERROR: Voice '{args.voice}' not found.")
            print("Use --list-voices to see available voices.")
            sys.exit(1)
        
        voice_id = voice_match.voice_id
        print(f"Using voice: {voice_match.name} (ID: {voice_id})")
    
    # Create output directory
    os.makedirs(args.output_dir, exist_ok=True)
    
    # Extract segments
    print(f"Reading segments from: {args.script}")
    segments = extract_segments(args.script)
    print(f"Found {len(segments)} segments")
    
    # Filter by start/end
    end = args.end if args.end is not None else len(segments)
    segments_to_process = [s for s in segments if args.start <= s['id'] < end]
    print(f"Processing segments {args.start} to {end-1} ({len(segments_to_process)} total)")
    
    # Calculate estimated characters
    total_chars = sum(len(s['text']) for s in segments_to_process)
    print(f"Estimated total characters: {total_chars:,}")
    
    # Confirm before proceeding
    print("\nThis will use your ElevenLabs character quota.")
    response = input("Continue? (y/n): ")
    if response.lower() != 'y':
        print("Aborted.")
        return
    
    # Generate audio for each segment
    print("\nGenerating audio...")
    print("-" * 50)
    
    for i, seg in enumerate(segments_to_process):
        output_path = os.path.join(args.output_dir, f"segment_{seg['id']}.mp3")
        
        # Skip if already exists
        if os.path.exists(output_path):
            print(f"[{i+1}/{len(segments_to_process)}] Skipping segment_{seg['id']}.mp3 (exists)")
            continue
        
        print(f"[{i+1}/{len(segments_to_process)}] Generating segment_{seg['id']}.mp3: {seg['text'][:50]}...")
        
        try:
            generate_audio(
                client,
                seg['text'],
                voice_id,
                output_path,
                stability=args.stability,
                similarity=args.similarity
            )
            
            # Delay to avoid rate limiting
            time.sleep(args.delay)
            
        except Exception as e:
            print(f"  ERROR: {e}")
            print("  Waiting 10 seconds before retrying...")
            time.sleep(10)
            try:
                generate_audio(client, seg['text'], voice_id, output_path)
            except Exception as e2:
                print(f"  FAILED: {e2}")
                continue
    
    print("-" * 50)
    print(f"\nDone! Audio files saved to: {args.output_dir}/")
    print(f"Total files: {len([f for f in os.listdir(args.output_dir) if f.endswith('.mp3')])}")


if __name__ == "__main__":
    main()

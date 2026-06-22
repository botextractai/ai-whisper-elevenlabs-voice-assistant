#!/usr/bin/env python3
"""
Speechify API Migration Test Script

This script verifies that the migration from ElevenLabs to Speechify API was successful.
It tests:
1. API key configuration
2. Voice listing functionality
3. Text-to-speech generation
4. Audio file creation

Run this script to verify your Speechify integration before using the main application.

Usage:
    python test_speechify.py

Requirements:
    - SPEECHIFY_API_KEY must be set in your .env file
    - speechify-api package must be installed
"""

import os
from dotenv import load_dotenv
from speechify import Speechify
from speechify.tts import GetSpeechOptionsRequest
import base64

# Load environment variables
load_dotenv()

def test_speechify_connection():
    """Test basic connection to Speechify API"""
    print("🔧 Testing Speechify API configuration...")
    
    api_key = os.environ.get('SPEECHIFY_API_KEY')
    
    if not api_key:
        print("❌ SPEECHIFY_API_KEY not found in environment variables")
        print("   Please add your Speechify API key to the .env file")
        return False
    
    try:
        # Initialize Speechify client
        client = Speechify(token=api_key)
        print("✅ Speechify client initialized successfully")
        
        # Test voice listing
        print("\n🎤 Testing voice listing...")
        voices_response = client.tts.voices.list()
        print(f"✅ Successfully fetched {len(voices_response)} voices")
        
        # Show sample voices
        if voices_response and len(voices_response) > 0:
            print("\n📋 Sample voices available:")
            for i, voice in enumerate(voices_response[:5]):  # Show first 5 voices
                voice_id = getattr(voice, 'id', 'N/A')
                gender = getattr(voice, 'gender', 'Unknown')
                name = getattr(voice, 'name', f'Voice {i+1}')
                print(f"  {i+1}. ID: {voice_id[:8]}... | Gender: {gender} | Name: {name}")
            
            # Use the first voice ID for testing
            test_voice_id = getattr(voices_response[0], 'id', 'voice_id')
        else:
            print("⚠️ No voices found, using default voice_id")
            test_voice_id = "voice_id"
        
        # Test TTS generation
        print(f"\n🔊 Testing TTS generation with voice: {test_voice_id[:8]}...")
        test_text = "Hello! This is a test of the Speechify API integration. The migration from ElevenLabs to Speechify was successful."
        
        audio_response = client.tts.audio.speech(
            audio_format="mp3",
            input=test_text,
            language="en-US",
            model="simba-english",
            options=GetSpeechOptionsRequest(
                loudness_normalization=True,
                text_normalization=True
            ),
            voice_id=test_voice_id
        )
        
        # Decode audio
        audio_bytes = base64.b64decode(audio_response.audio_data)
        print(f"✅ Successfully generated audio ({len(audio_bytes)} bytes)")
        print(f"✅ Billable characters: {audio_response.billable_characters_count}")
        print(f"✅ Audio format: {audio_response.audio_format}")
        
        # Save test audio file
        with open("speechify_test_audio.mp3", "wb") as f:
            f.write(audio_bytes)
        print("✅ Test audio saved as 'speechify_test_audio.mp3'")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing Speechify API: {str(e)}")
        print("   This could indicate:")
        print("   - Invalid API key")
        print("   - Network connectivity issues")
        print("   - API service unavailable")
        return False

def compare_migration():
    """Compare features between ElevenLabs and Speechify"""
    print("\n📊 Migration Feature Comparison:")
    print("┌─────────────────────────┬─────────────────┬─────────────────┐")
    print("│ Feature                 │ ElevenLabs      │ Speechify       │")
    print("├─────────────────────────┼─────────────────┼─────────────────┤")
    print("│ Audio Formats           │ MP3             │ MP3, AAC, OGG,  │")
    print("│                         │                 │ WAV             │")
    print("├─────────────────────────┼─────────────────┼─────────────────┤")
    print("│ Voice Selection         │ Named voices    │ Voice IDs       │")
    print("│                         │ (e.g., 'Bella') │ (UUID format)   │")
    print("├─────────────────────────┼─────────────────┼─────────────────┤")
    print("│ Language Support        │ Auto-detect     │ Explicit lang   │")
    print("│                         │                 │ codes (en-US)   │")
    print("├─────────────────────────┼─────────────────┼─────────────────┤")
    print("│ Audio Enhancement       │ Basic           │ Loudness &      │")
    print("│                         │                 │ Text Normal.    │")
    print("├─────────────────────────┼─────────────────┼─────────────────┤")
    print("│ Speech Marks            │ No              │ Yes (timing     │")
    print("│                         │                 │ information)    │")
    print("├─────────────────────────┼─────────────────┼─────────────────┤")
    print("│ Model Selection         │ Default         │ simba-english,  │")
    print("│                         │                 │ simba-multi     │")
    print("└─────────────────────────┴─────────────────┴─────────────────┘")

if __name__ == "__main__":
    print("=" * 60)
    print("🚀 SPEECHIFY API MIGRATION TEST")
    print("=" * 60)
    
    success = test_speechify_connection()
    
    compare_migration()
    
    print("\n" + "=" * 60)
    if success:
        print("🎉 MIGRATION TEST PASSED!")
        print("✅ Your application is ready to use Speechify API")
        print("✅ You can now run: streamlit run chat.py")
    else:
        print("💥 MIGRATION TEST FAILED!")
        print("❌ Please check your API key and network connection")
        print("❌ Refer to the README for setup instructions")
    print("=" * 60) 
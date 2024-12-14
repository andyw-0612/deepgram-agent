import sounddevice as sd
import soundfile as sf
import tempfile
import os
import re
from deepgram import DeepgramClient, SpeakOptions
from utils import print_debug

class AudioPlayer:
    """
    Handles text-to-speech synthesis and audio playback using Deepgram's API
    Includes support for interrupting ongoing playback
    """
    def __init__(self, api_key: str):
        # Initialize Deepgram client and playback state
        self.deepgram = DeepgramClient(api_key)
        self.is_playing = False
        self.stop_current_playback = False
        # Create temporary directory for audio files
        self.temp_dir = tempfile.mkdtemp()
        print_debug("SYSTEM", "Audio player initialized")

    def split_text_by_length(self, text: str, max_length: int = 2000) -> list:
        """
        Split text into chunks not exceeding max_length characters,
        ensuring splits occur at sentence boundaries
        """
        # Find all sentences
        sentences = re.findall(r"[^.!?]+[.!?]", text)
        chunks = []
        current_chunk = ""

        for sentence in sentences:
            # If adding this sentence would exceed max_length,
            # save current chunk and start a new one
            if len(current_chunk) + len(sentence) > max_length and current_chunk:
                chunks.append(current_chunk.strip())
                current_chunk = sentence
            else:
                current_chunk += sentence

        # Add the last chunk if it's not empty
        if current_chunk:
            chunks.append(current_chunk.strip())

        return chunks

    async def synthesize_and_play(self, text: str) -> None:
        """
        Convert text to speech and play audio segments sequentially
        Handles interruption between segments
        """
        # Split text into chunks of maximum 2000 characters
        segments = self.split_text_by_length(text)
        print_debug("DEBUG", f"Segmented text into {len(segments)} segments")

        for i, segment in enumerate(segments):
            if self.stop_current_playback:
                print_debug("DEBUG", "Stopping TTS due to interruption")
                break

            temp_file = None
            try:
                # Create temporary file for current segment
                temp_file = os.path.join(self.temp_dir, f"temp_{i}.mp3")
                # Generate audio using Deepgram
                text_formatted = {"text": segment}
                options = SpeakOptions(model="aura-luna-en")
                await self.deepgram.speak.asyncrest.v("1").save(temp_file, text_formatted, options)
                # Play audio segment
                data, samplerate = sf.read(temp_file)
                self.is_playing = True
                sd.play(data, samplerate, blocksize=128)
                # Wait for playback to complete or interruption
                while sd.get_stream().active and not self.stop_current_playback:
                    sd.sleep(50)
            except Exception as e:
                print_debug("SYSTEM", f"Error with audio: {e}")
            finally:
                # Cleanup and reset state
                self.is_playing = False
                if temp_file and os.path.exists(temp_file):
                    os.remove(temp_file)

            if self.stop_current_playback:
                break

    def stop_playback(self):
        """
        Stop current audio playback if playing
        """
        if self.is_playing:
            self.stop_current_playback = True
            sd.stop()
            print_debug("SYSTEM", "Stopping audio playback")

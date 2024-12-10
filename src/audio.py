import sounddevice as sd
import soundfile as sf
import tempfile
import os
import re
from deepgram import DeepgramClient, SpeakOptions
from utils import print_debug

class AudioPlayer:
    """
    handles text-to-speech synthesis and audio playback using deepgram's api
    includes support for interrupting ongoing playback
    """
    def __init__(self, api_key: str):
        # initialize deepgram client and playback state
        self.deepgram = DeepgramClient(api_key)
        self.is_playing = False
        self.stop_current_playback = False
        # create temporary directory for audio files
        self.temp_dir = tempfile.mkdtemp()
        print_debug("SYSTEM", "Audio player initialized")

    async def synthesize_and_play(self, text: str) -> None:
        """
        convert text to speech and play audio segments sequentially
        handles interruption between segments
        """
        # split text into sentence segments for smoother playback
        segments = re.findall(r"[^.!?]+[.!?]", text)
        print_debug("DEBUG", f"Segmented text into {len(segments)} segments")

        for i, segment in enumerate(segments):
            if self.stop_current_playback:
                print_debug("DEBUG", "Stopping TTS due to interruption")
                break

            temp_file = None
            try:
                # create temporary file for current segment
                temp_file = os.path.join(self.temp_dir, f"temp_{i}.mp3")

                # generate audio using deepgram
                text_formatted = {"text": segment}
                options = SpeakOptions(model="aura-orion-en")
                await self.deepgram.speak.asyncrest.v("1").save(temp_file, text_formatted, options)

                # play audio segment
                data, samplerate = sf.read(temp_file)
                self.is_playing = True
                sd.play(data, samplerate, blocksize=128)

                # wait for playback to complete or interruption
                while sd.get_stream().active and not self.stop_current_playback:
                    sd.sleep(50)

            except Exception as e:
                print_debug("SYSTEM", f"Error with audio: {e}")
            finally:
                # cleanup and reset state
                self.is_playing = False
                if temp_file and os.path.exists(temp_file):
                    os.remove(temp_file)

            if self.stop_current_playback:
                break

    def stop_playback(self):
        """
        stop current audio playback if playing
        """
        if self.is_playing:
            self.stop_current_playback = True
            sd.stop()
            print_debug("SYSTEM", "Stopping audio playback")

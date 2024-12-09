import numpy as np
import sounddevice as sd
from typing import Callable, List
from utils import print_debug

class SpeechProcessor:
    """
    handles speech processing, transcription, and audio interruption
    manages communication between speech input and llm
    """
    def __init__(self, llm_callback: Callable[[str], None], audio_player: 'AudioPlayer'):
        # initialize state and callbacks
        self.is_finals: List[str] = []
        self.llm_callback = llm_callback
        self.audio_player = audio_player

        # set up microphone monitoring
        self.monitor_stream = sd.InputStream(callback=self.audio_callback)
        self.monitor_stream.start()
        print_debug("SYSTEM", "Speech processor with mic monitoring initialized")

    def audio_callback(self, indata, frames, time, status):
        """
        monitor microphone input and interrupt playback if speech detected
        """
        # calculate volume level from input data
        volume_norm = np.linalg.norm(indata) * 10
        if volume_norm > 1.0:  # threshold for speech detection
            if self.audio_player.is_playing:
                self.audio_player.stop_playback()

    def process_final_speech(self, utterance: str):
        """
        process completed speech and forward to llm
        """
        if utterance.strip():
            print_debug("USER", f"Final: {utterance}")
            self.audio_player.stop_playback()
            self.llm_callback(utterance)

    def handle_transcript(self, result) -> None:
        """
        handle incoming transcription results and build complete utterances
        """
        sentence = result.channel.alternatives[0].transcript
        if not sentence:
            return

        if result.is_final:
            # accumulate final transcriptions
            self.is_finals.append(sentence)

            if result.speech_final:
                # complete utterance detected
                utterance = " ".join(self.is_finals)
                print_debug("DEBUG", "Speech final detected")
                self.process_final_speech(utterance)
                self.is_finals = []
        else:
            # display interim results
            print_debug("USER", f"{sentence}", is_interim=True)

    def handle_utterance_end(self) -> None:
        """
        handle end of utterance and process accumulated speech
        """
        if self.is_finals:
            utterance = " ".join(self.is_finals)
            print_debug("DEBUG", "Utterance end detected")
            self.process_final_speech(utterance)
            self.is_finals = []

    def cleanup(self):
        """
        cleanup resources and close audio streams
        """
        if hasattr(self, 'monitor_stream'):
            self.monitor_stream.stop()
            self.monitor_stream.close()

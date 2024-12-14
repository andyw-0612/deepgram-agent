from queue import Queue
import threading
import asyncio
from deepgram import DeepgramClient, LiveTranscriptionEvents, LiveOptions, Microphone
from config import DEEPGRAM_API_KEY, GROQ_API_KEY
from audio import AudioPlayer
from llm import GroqLLM
from speech import SpeechProcessor
from utils import print_debug

class LiveTranscriptionSystem:
    """
    manages the complete voice assistant system
    coordinates speech recognition, llm interaction, and audio playback
    """
    def __init__(self):
        # initialize system components
        self.response_queue = Queue()
        self.audio_player = AudioPlayer(DEEPGRAM_API_KEY)
        self.llm = GroqLLM(GROQ_API_KEY)
        self.speech_processor = SpeechProcessor(self.queue_llm_request, self.audio_player)
        self.tts_thread = None
        print_debug("SYSTEM", "Live transcription system initialized")

    def queue_llm_request(self, text: str) -> None:
        """
        queue text for llm processing and response generation
        """
        print_debug("DEBUG", "Queueing LLM request")
        asyncio.run(self.process_llm_request(text))

    async def process_llm_request(self, text: str) -> None:
        """
        process text through llm and handle text-to-speech response
        """
        # get llm response
        response = await self.llm.generate_response(text)
        print_debug("LLM", response)

        # handle existing playback
        if self.tts_thread and self.tts_thread.is_alive():
            self.audio_player.stop_playback()
            self.tts_thread.join()

        self.audio_player.stop_current_playback = False

        # start new text-to-speech playback
        self.tts_thread = threading.Thread(
            target=asyncio.run,
            args=(self.audio_player.synthesize_and_play(response),)
        )
        self.tts_thread.start()

    def setup_connection(self) -> tuple:
        """
        set up deepgram connection and configure transcription options
        """
        print_debug("SYSTEM", "Setting up Deepgram connection")
        deepgram = DeepgramClient(DEEPGRAM_API_KEY)
        dg_connection = deepgram.listen.websocket.v("1")

        # set up event handlers for transcription
        def on_transcript(_, result, **kwargs):
            self.speech_processor.handle_transcript(result)

        def on_utterance_end(*args, **kwargs):
            self.speech_processor.handle_utterance_end()

        dg_connection.on(LiveTranscriptionEvents.Open,
                        lambda _, *args, **kwargs: print_debug("SYSTEM", "Connection opened"))
        dg_connection.on(LiveTranscriptionEvents.Transcript, on_transcript)
        dg_connection.on(LiveTranscriptionEvents.UtteranceEnd, on_utterance_end)
        dg_connection.on(LiveTranscriptionEvents.Close,
                        lambda _, *args, **kwargs: print_debug("SYSTEM", "Connection closed"))
        dg_connection.on(LiveTranscriptionEvents.Error,
                        lambda _, error, **kwargs: print_debug("SYSTEM", f"Error: {error}"))

        # configure transcription options
        options = LiveOptions(
            model="nova-2",
            language="en-US",
            smart_format=True,
            encoding="linear16",
            channels=1,
            sample_rate=16000,
            interim_results=True,
            utterance_end_ms="1000",
            vad_events=True,
            endpointing=750,
        )

        return dg_connection, options

    def run(self):
        """
        run the voice assistant system
        handles initialization, main loop, and cleanup
        """
        try:
            # system startup and initialization
            print_debug("SYSTEM", "Starting live transcription system")
            print_debug("SYSTEM", "Colored output legend:")
            print_debug("SYSTEM", "Blue: System messages")
            print_debug("USER", "Green: User speech")
            print_debug("LLM", "Yellow: LLM responses")
            print_debug("DEBUG", "Gray: Debug information")

            # set up deepgram connection
            dg_connection, options = self.setup_connection()

            if not dg_connection.start(options, addons={"no_delay": "true"}):
                print_debug("SYSTEM", "Failed to connect to Deepgram")
                return

            # start microphone and main loop
            microphone = Microphone(dg_connection.send)
            microphone.start()
            print_debug("SYSTEM", "Microphone activated")

            print_debug("SYSTEM", "Press Enter to stop recording...")
            input("")

            # cleanup on exit
            if self.tts_thread and self.tts_thread.is_alive():
                self.audio_player.stop_playback()
                self.tts_thread.join()

            self.speech_processor.cleanup()
            microphone.finish()
            dg_connection.finish()
            print_debug("SYSTEM", "System shutdown complete")

        except Exception as e:
            print_debug("SYSTEM", f"Error: {e}")

if __name__ == "__main__":
    system = LiveTranscriptionSystem()
    system.run()

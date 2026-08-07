import os
from groq import Groq

class VoiceEngine:
    """Processes incoming WhatsApp voice notes and converts text to speech."""

    def __init__(self):
        self.api_key = os.environ.get("GROQ_API_KEY")

    def transcribe_audio_file(self, audio_file_path: str) -> str:
        """Transcribes WhatsApp voice note using Groq Whisper model."""
        if not self.api_key or not os.path.exists(audio_file_path):
            return "Voice note received."

        try:
            client = Groq(api_key=self.api_key)
            with open(audio_file_path, "rb") as file:
                transcription = client.audio.transcriptions.create(
                    file=(os.path.basename(audio_file_path), file.read()),
                    model="whisper-large-v3",
                    response_format="json",
                    language="en"
                )
                return transcription.text
        except Exception as e:
            print(f"[ERROR] Voice transcription failed: {e}")
            return "Voice note received."

voice_engine = VoiceEngine()

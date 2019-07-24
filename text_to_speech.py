from google.cloud import texttospeech
import os


class TextToSpeech:
    def __init__(self, path: str):
        os.makedirs(path, exist_ok=True)
        self._path = path
        self._client = texttospeech.TextToSpeechClient()

    def gen_speech(self, handle_id: str, text: str):
        synthesis_input = texttospeech.types.SynthesisInput(text=text)
        voice = texttospeech.types.VoiceSelectionParams(
            language_code='en-US',
            ssml_gender=texttospeech.enums.SsmlVoiceGender.NEUTRAL)

        audio_config = texttospeech.types.AudioConfig(
            audio_encoding=texttospeech.enums.AudioEncoding.MP3)

        response = self._client.synthesize_speech(synthesis_input, voice, audio_config)
        path = os.path.join(self._path, f'{handle_id}.mp3')

        with open(path, 'wb') as f:
            f.write(response.audio_content)

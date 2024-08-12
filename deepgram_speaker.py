from deepgram import DeepgramClient, SpeakOptions
import pygame

class DeepgramSpeaker:
    def __init__(self, api_key: str):
        self.deepgram = DeepgramClient(api_key)

    def speak(self, text: str, filename: str = "audio.wav"):
        try:
            pygame.mixer.init()
            

            options = SpeakOptions(model="aura-asteria-en",
                                   encoding="linear16",
                                   container="wav"
                                   )
            response = self.deepgram.speak.v("1").save(filename, {"text": text}, options)
            pygame.mixer.music.load(filename)
            pygame.mixer.music.play()
            # Wait for the music to finish
            while pygame.mixer.music.get_busy():
                pygame.time.Clock().tick(10)

            # Stop the mixer after playback to release the file
            pygame.mixer.music.stop()
            pygame.mixer.quit()
            print(response.to_json(indent=4))
            return response
        except Exception as e:
            print(f"Exception: {e}")

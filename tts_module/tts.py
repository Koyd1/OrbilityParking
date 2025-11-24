"""
piper_tts_module.py

Модуль для синтеза речи через piper-tts (pip-пакет) и последующего воспроизведения.
Работает полностью локально

Требования:
    pip install piper-tts simpleaudio или pip install -r requirements.txt

Использование:
    from piper_tts_module import PiperTTS

    tts = PiperTTS(voice="en_US-amy-medium.onnx")
    tts.synthesize_to_file("Hello!", "out.wav")
    tts.play_file("out.wav")

    tts.synth_and_play("Hello world!")
"""
import threading

import os
import wave
import tempfile
from typing import Optional
import simpleaudio as sa
from piper import PiperVoice


class PiperTTS:
    def __init__(self, voice: str):
        """
        voice: путь к .onnx модели голоса Piper (обязательный параметр!)
        sample_rate: частота дискретизации выходного WAV-файла
        """
        self.voice = voice


    def synthesize_to_file(self, text: str, out_path: str, voice: Optional[str] = None) -> str:
        """
        Синтезирует речь в WAV файл с использованием piper-tts.
        """
        out_path = os.path.abspath(out_path)
        os.makedirs(os.path.dirname(out_path) or ".", exist_ok=True)

        model_path = voice or self.voice
        if model_path is None:
            raise RuntimeError(
                "Не указан путь к модели (.onnx). Передайте voice='model.onnx' в PiperTTS()."
            )

        # Загружаем модель
        voice_obj = PiperVoice.load(model_path)
    
        # Синтезируем
        audio = voice_obj.synthesize(text)

        model_rate = voice_obj.config.sample_rate  # Устанавливаем sample_rate модели

        # WAV файл
        with wave.open(out_path, "wb") as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)  # int16
            wf.setframerate(model_rate)

            for chunk in audio:
                # chunk.audio_int16_array — numpy.ndarray int16
                wf.writeframes(chunk.audio_int16_array)
                
        return out_path

    def play_file(self, path: str) -> None:
        """
        Проигрывает WAV-файл с помощью simpleaudio.
        """
        path = os.path.abspath(path)
        if not os.path.exists(path):
            raise FileNotFoundError(path)

        wave_obj = sa.WaveObject.from_wave_file(path)
        play_obj = wave_obj.play()
        play_obj.wait_done()

    # def synth_and_play(self, text: str, voice: Optional[str] = None) -> None:
    #     """
    #     Синтезирует текст во временный файл и сразу воспроизводит его.
    #     """
    #     fd, tmp = tempfile.mkstemp(suffix=".wav")
    #     os.close(fd)

    #     try:
    #         self.synthesize_to_file(text, tmp, voice=voice)
    #         self.play_file(tmp)
    #     finally:
    #         if os.path.exists(tmp):
    #             os.remove(tmp)
    def synth_and_play(self, text: str, voice: Optional[str] = None) -> None:
        import tempfile, os
        fd, tmp = tempfile.mkstemp(suffix=".wav")
        os.close(fd)

        try:
            self.synthesize_to_file(text, tmp, voice=voice)
            # Воспроизведение синхронно, без потоков
            import simpleaudio as sa
            wave_obj = sa.WaveObject.from_wave_file(tmp)
            play_obj = wave_obj.play()
            play_obj.wait_done()
        finally:
            if os.path.exists(tmp):
                os.remove(tmp)





if __name__ == "__main__":

    model_path = "low_models/es_ES-carlfm-x_low.onnx" # Здесь путь к модели ONNX и JSON файлу
    tts = PiperTTS(model_path)
    tts.synthesize_to_file("Un débil resplandor azul brillaba sobre el lago mientras diminutos insectos danzaban en el aire frío, haciendo que la noche se sintiera viva de una manera tranquila y casi secreta.", "spanish_low.wav")
    

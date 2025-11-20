import whisper
import torch
import numpy as np
import threading
import queue
import pyaudio
import psutil
import os


class WhisperSTT:
    def __init__(self, model_size="small", device=None):
        """
        Инициализация модели Whisper.
        model_size: tiny, base, small (medium и large > 2 ГБ)
        """
        if device is None:
            device = "cuda" if torch.cuda.is_available() else "cpu"

        # Загружаем модель в нужном dtype в зависимости от устройства
        dtype = torch.float16 if device == "cuda" else torch.float32
        self.model = whisper.load_model(model_size, device=device).to(dtype=dtype)
        self.sample_rate = 16000
        self.buffer_queue = queue.Queue()
        self.is_listening = False
        self.transcript_callback = None

    def transcribe_file(self, audio_path):
        """
        Транскрибация аудиофайла.
        """
        result = self.model.transcribe(audio_path, language=None)
        return result["text"]

    def transcribe_buffer(self, audio_buffer):
        """
        Транскрибация аудио-буфера (numpy array).
        """
        audio = audio_buffer.astype(np.float32)
        audio = audio / 32768.0
        result = self.model.transcribe(audio, language=None)
        return result["text"], result["language"]

    def start_realtime_transcription(self, callback=None):
        """
        Начать транскрибацию в реальном времени из буфера.
        callback(text, language) - вызывается при завершении фразы.
        """
        self.transcript_callback = callback
        self.is_listening = True
        self.listen_thread = threading.Thread(target=self._process_buffer_stream)
        self.listen_thread.start()

    def stop_realtime_transcription(self):
        """
        Остановить транскрибацию в реальном времени.
        """
        self.is_listening = False
        if hasattr(self, 'listen_thread'):
            self.listen_thread.join()

    def _process_buffer_stream(self):
        """
        Внутренний метод для обработки буфера в реальном времени.
        """
        accumulated_audio = np.array([], dtype=np.float32)

        while self.is_listening:
            try:
                chunk = self.buffer_queue.get(timeout=0.1)
                if chunk is None:
                    break
                accumulated_audio = np.concatenate([accumulated_audio, chunk])

                # Если накоплено >= 4 секунд — транскрибировать
                if len(accumulated_audio) >= self.sample_rate * 4:
                    text, lang = self.transcribe_buffer(accumulated_audio)
                    if text.strip():
                        if self.transcript_callback:
                            self.transcript_callback(text, lang)
                    accumulated_audio = np.array([], dtype=np.float32)

            except queue.Empty:
                continue

    def add_audio_chunk(self, chunk):
        self.buffer_queue.put(chunk)

    def transcribe_microphone(self, duration=60, callback=None, show_resources=True):
        """
        Метод для транскрибации с микрофона.
        Запускает микрофон и транскрибацию в реальном времени.
        """
        def default_callback(text, lang):
            print(f"[{lang.upper()}] -> {text}")

        if callback is None:
            callback = default_callback

        # Запуск мониторинга ресурсов, если включён
        stop_event = threading.Event()
        resource_thread = None
        if show_resources:
            resource_thread = threading.Thread(target=resource_monitor, args=(stop_event,), daemon=True)
            resource_thread.start()

        self.start_realtime_transcription(callback=callback)

        p = pyaudio.PyAudio()
        stream = p.open(
            format=pyaudio.paInt16,
            channels=1,
            rate=self.sample_rate,
            input=True,
            frames_per_buffer=1600
        )
        print("Запись начата... Говорите!")

        try:
            for _ in range(0, int(self.sample_rate / 1600 * duration)):
                data = stream.read(1600, exception_on_overflow=False)
                audio_chunk = np.frombuffer(data, dtype=np.int16).astype(np.float32)
                self.add_audio_chunk(audio_chunk)
        except KeyboardInterrupt:
            print("\nОстановка по прерыванию пользователя...")
        finally:
            print("Запись завершена.")
            stream.stop_stream()
            stream.close()
            p.terminate()
            self.stop_realtime_transcription()
            if show_resources:
                stop_event.set()
                if resource_thread:
                    resource_thread.join()


def print_resources():
    process = psutil.Process(os.getpid())
    mem = process.memory_info().rss / (1024*1024)
    cpu = process.cpu_percent()
    print(f"[STATS] RAM: {mem:.1f} MB | CPU: {cpu}%")


def resource_monitor(stop_event):
    while not stop_event.is_set():
        print_resources()
        stop_event.wait(2)


def main():
    print("Инициализация Whisper STT...")
    stt = WhisperSTT()  # Модель с хорошим качеством и <2 ГБ RAM

    print("\nЗапуск транскрибации с микрофона...")
    stt.transcribe_microphone(duration=60, show_resources=True)


if __name__ == "__main__":
    main()

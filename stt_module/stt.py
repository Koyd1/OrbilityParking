import whisper
import torch
import numpy as np
import threading
import queue

class WhisperSTT:
    def __init__(self, model_size="small", device=None):
        """
        Инициализация модели Whisper.
        model_size: tiny, base, small
        """
        if device is None:
            device = "cuda" if torch.cuda.is_available() else "cpu"
        
        self.model = whisper.load_model(model_size, device=device).to(dtype=torch.float32)  # FP16 не поддерживается на CPU
        self.sample_rate = 16000
        self.buffer_queue = queue.Queue()
        self.is_listening = False
        self.transcript_callback = None

    def transcribe_file(self, audio_path):
        """
        Транскрибация аудиофайла.
        """
        result = self.model.transcribe(audio_path, language=None)  # None = автоопределение
        return result["text"]

    def transcribe_buffer(self, audio_buffer):
        """
        Транскрибация аудио-буфера (numpy array).
        """
        audio = audio_buffer.astype(np.float32)
        audio = audio / 32768.0  # если int16 -> float32
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


def record_microphone(stt_instance, duration=20):
    import pyaudio
    p = pyaudio.PyAudio()
    stream = p.open(format=pyaudio.paInt16, channels=1, rate=16000, input=True, frames_per_buffer=1600)
    print("Запись начата... Говорите!")
    try:
        for _ in range(0, int(16000 / 1600 * duration)):
            data = stream.read(1600, exception_on_overflow=False)
            audio_chunk = np.frombuffer(data, dtype=np.int16).astype(np.float32)
            stt_instance.add_audio_chunk(audio_chunk)
    except KeyboardInterrupt:
        print("\nОстановка по прерыванию пользователя...")
    finally:
        print("Запись завершена.")
        stream.stop_stream()
        stream.close()
        p.terminate()

import psutil, os

def resource_monitor_thread(stop_event):
    while not stop_event.is_set():
        print_resources()
        stop_event.wait(2)  # ждем 2 секунды или пока не будет установлен флаг остановки

def print_resources():
    process = psutil.Process(os.getpid())
    mem = process.memory_info().rss / (1024*1024)
    cpu = process.cpu_percent()
    print(f"[STATS] RAM: {mem:.1f} MB | CPU: {cpu}%")


# Пример использования
def main():
    print("Инициализация Whisper STT...")
    stt = WhisperSTT(model_size="small")

    def on_transcript(text, language):
        print(f"[{language.upper()}] -> {text}")

    stop_event = threading.Event()
    resource_thread = threading.Thread(target=resource_monitor_thread, args=(stop_event,))
    resource_thread.daemon = True  # поток завершится при завершении основной программы
    resource_thread.start()

    print("Запуск транскрибации в реальном времени...")
    stt.start_realtime_transcription(callback=on_transcript)

    print("Запуск записи с микрофона...")
    try:
        record_microphone(stt, duration=20)  # запись 20 секунд
    except KeyboardInterrupt:
        print("\nОстановка по прерыванию пользователя...")

    print("Остановка транскрибации...")
    stt.stop_realtime_transcription()
    print("Готово.")
    print_resources()


if __name__ == "__main__":
    main()
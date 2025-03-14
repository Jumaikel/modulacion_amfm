import numpy as np
import scipy.integrate
import sounddevice as sd
from scipy.io import wavfile
from PyQt5.QtWidgets import QApplication, QFileDialog, QVBoxLayout, QPushButton, QLineEdit, QWidget
import pyqtgraph as pg

app = QApplication([])


def select_file():
    options = QFileDialog.Options()
    file_path, _ = QFileDialog.getOpenFileName(None, "Seleccionar archivo de audio", "", "WAV files (*.wav)",
                                               options=options)
    return file_path


class ModulationApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Modulación de Audio")
        self.setGeometry(100, 100, 800, 600)

        self.layout = QVBoxLayout()

        self.freq_input = QLineEdit(self)
        self.freq_input.setPlaceholderText("Ingrese la frecuencia portadora (Hz), por defecto 5000")
        self.layout.addWidget(self.freq_input)

        self.load_button = QPushButton("Seleccionar Archivo WAV", self)
        self.load_button.clicked.connect(self.load_audio)
        self.layout.addWidget(self.load_button)

        self.play_orig_button = QPushButton("Reproducir Audio Original", self)
        self.play_orig_button.clicked.connect(self.play_original_audio)
        self.layout.addWidget(self.play_orig_button)

        self.play_am_button = QPushButton("Reproducir AM Modulada", self)
        self.play_am_button.clicked.connect(self.play_am_audio)
        self.layout.addWidget(self.play_am_button)

        self.play_fm_button = QPushButton("Reproducir FM Modulada", self)
        self.play_fm_button.clicked.connect(self.play_fm_audio)
        self.layout.addWidget(self.play_fm_button)

        self.setLayout(self.layout)

        self.audio = None
        self.sample_rate = None
        self.time = None
        self.am_modulated = None
        self.fm_modulated = None
        self.win = None

    def load_audio(self):
        audio_file = select_file()
        if not audio_file:
            return

        self.sample_rate, self.audio = wavfile.read(audio_file)
        self.audio = self.audio if len(self.audio.shape) == 1 else self.audio[:, 0]
        self.audio = self.audio / np.max(np.abs(self.audio))
        self.time = np.linspace(0, len(self.audio) / self.sample_rate, num=len(self.audio))

        carrier_freq = float(self.freq_input.text()) if self.freq_input.text() else 5000
        carrier = np.cos(2 * np.pi * carrier_freq * self.time)
        self.am_modulated = (1 + self.audio) * carrier

        modulation_index = 5
        integral_audio = scipy.integrate.cumulative_trapezoid(self.audio, self.time, initial=0)
        self.fm_modulated = np.cos(2 * np.pi * carrier_freq * self.time + modulation_index * integral_audio)

        self.show_results()

    def show_results(self):
        self.win = pg.GraphicsLayoutWidget(show=True,
                                           title="Resultados de Modulación")
        self.win.resize(1280, 720)
        self.win.setWindowTitle('Resultados de Modulación')

        p1 = self.win.addPlot(title="Señal de Audio Original")
        p1.plot(self.time, self.audio, pen='b')

        self.win.nextRow()
        p2 = self.win.addPlot(title="Señal Modulada en AM")
        p2.plot(self.time, self.am_modulated, pen='r')

        self.win.nextRow()
        p3 = self.win.addPlot(title="Señal Modulada en FM")
        p3.plot(self.time, self.fm_modulated, pen='g')

    def play_original_audio(self):
        if self.audio is not None:
            sd.play(self.audio, self.sample_rate)

    def play_am_audio(self):
        if self.am_modulated is not None:
            sd.play(self.am_modulated, self.sample_rate)

    def play_fm_audio(self):
        if self.fm_modulated is not None:
            sd.play(self.fm_modulated, self.sample_rate)


if __name__ == "__main__":
    window = ModulationApp()
    window.show()
    app.exec_()

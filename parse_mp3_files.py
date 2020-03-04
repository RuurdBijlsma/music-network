import pathlib
import sqlite3
import librosa
import librosa.display
# We'll need numpy for some mathematical operations
import numpy as np

# matplotlib for displaying the output
import matplotlib.pyplot as plt
# %matplotlib inline

# and IPython.display for audio output
# import IPython.display

# Librosa for audio
import librosa
# And the display module for visualization
import librosa.display

db_file = '.slider.db'

db_file = pathlib.Path(db_file)
db = sqlite3.connect(str(db_file))
cursor = db.cursor()


def do():
    # cursor.execute("SELECT DISTINCT mp3_file FROM beatmaps")
    # mp3_files = cursor.fetchall()
    file = "C:\\Users\\Ruurd\\Pictures\\dota.mp3"
    # file = librosa.util.example_audio_file()

    y, sr = librosa.load(file, sr=None)
    # Let's make and display a mel-scaled power (energy-squared) spectrogram
    S = librosa.feature.melspectrogram(y, sr=sr, n_fft=2048, n_mels=256)

    # Convert to log scale (dB). We'll use the peak power (max) as reference.
    log_S = librosa.power_to_db(S, ref=np.max)

    # Make a new figure
    plt.figure(figsize=(12, 4))

    # Display the spectrogram on a mel scale
    # sample rate and hop length parameters are used to render the time axis
    librosa.display.specshow(log_S, sr=sr, x_axis='time', y_axis='mel')

    # Put a descriptive title on the plot
    plt.title('mel power spectrogram')

    # draw a color bar
    plt.colorbar(format='%+02.0f dB')

    # Make the figure layout compact
    plt.tight_layout()
    plt.show()
    input("???")


if __name__ == '__main__':
    do()

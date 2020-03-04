import os
import pathlib
from osu.slider import Beatmap, GameMode
import sqlite3
from multiprocessing import Pool, cpu_count

folder_location = 'D:\\Songs - All Ranked+Loved+More'
db_file = '.slider.db'

db_file = pathlib.Path(db_file)
db = sqlite3.connect(str(db_file))
cursor = db.cursor()


def time_to_ms(time):
    return int(time.days * 86400 * 1000 +
               time.seconds * 1000 +
               time.microseconds / 1000)


def write_to_db(beatmap, path):
    mp3_path = path.parent.joinpath(beatmap.audio_filename)

    try:
        cursor.execute('INSERT INTO beatmaps VALUES (?,?,?,?,?,?)',
                       (None, str(path), str(mp3_path),
                        beatmap.approach_rate,
                        time_to_ms(beatmap.audio_lead_in),
                        beatmap.overall_difficulty))
    except sqlite3.IntegrityError as e:
        print("BM Integrity error")
        pass

    last_id = cursor.lastrowid
    for hit_object in beatmap.hit_objects:
        try:
            time_ms = time_to_ms(hit_object.time)
            ho_column = int(hit_object.position.x * beatmap.grid_size / 512)
            cursor.execute('INSERT INTO hit_objects VALUES (?,?,?,?)',
                           (None, last_id, ho_column, time_ms))
        except sqlite3.IntegrityError as e:
            print("HO Integrity error")
            pass


def get_osu_files(path):
    """An iterator of ``.osu`` filepaths in a directory.

    Parameters
    ----------
    path : path-like
        The directory to search in.

    Yields
    ------
    path : str
        The path to a ``.osu`` file.
    """
    for directory, _, filenames in os.walk(path):
        for filename in filenames:
            if filename.endswith('.osu'):
                yield pathlib.Path(os.path.join(directory, filename))


def pickle_rick(path):
    with open(path, 'rb') as f:
        data = f.read()

    try:
        return Beatmap.parse(data.decode('utf-8-sig')), data, path
    except (ValueError, KeyError, StopIteration, OverflowError):
        print(f'failed to parse {path}')
        return False, False, False


def do():
    inp = input("About to clear beatmap database, continue? [Y/n]")
    if str.lower(inp) != 'y' and inp != '':
        print("Stopping...")
        return
    print("Clearing...")

    clear_db = True
    if clear_db:
        cursor.execute("DROP TABLE IF EXISTS hit_objects")
        cursor.execute("DROP TABLE IF EXISTS beatmaps")
    cursor.execute("""\
        CREATE TABLE IF NOT EXISTS beatmaps (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            osu_file TEXT UNIQUE NOT NULL,
            mp3_file TEXT NOT NULL,
            approach_rate FLOAT,
            audio_lead_in_ms INTEGER,
            difficulty float
        )
        """)
    cursor.execute("""\
        CREATE TABLE IF NOT EXISTS hit_objects (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            beatmap_id INTEGER NOT NULL,
            x INTEGER NOT NULL,
            ms INTEGER NOT NULL
        )
        """)

    files = get_osu_files(folder_location)
    amount = len(os.listdir(folder_location))

    with Pool(cpu_count()) as pool:
        results = pool.imap_unordered(pickle_rick, files)

        mania_count = 0
        for i, (beatmap, data, path) in enumerate(results):
            if beatmap and beatmap.mode == GameMode.mania:
                mania_count += 1
                write_to_db(beatmap, path)
                print(f"[{i}/{amount}] {mania_count} manias found")

        db.commit()
        db.close()


if __name__ == '__main__':
    do()

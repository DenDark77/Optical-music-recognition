from music21 import note, stream, tempo, instrument
import pandas as pd
from .model import process_image


def notes_to_music_with_instrument(input_file, instrument_name, temp):
    music_stream = stream.Stream()

    prediction = process_image(input_file)
    instr = instrument.fromString(instrument_name)
    music_stream.insert(0, instr)

    for note_names in prediction:
        for note_name in note_names:
            if note_name != '.':
                if '{' in note_name:
                    notes_with_duration = note_name.strip('{}').split(',')
                    for note_with_duration in notes_with_duration:
                        note_t, duration = note_with_duration.split('/')
                        new_note = note.Note(note_t)
                        new_note.duration.quarterLength = float(duration)
                        music_stream.append(new_note)
                else:
                    note_t, duration = note_name.split('/')
                    new_note = note.Note(note_t)
                    new_note.duration.quarterLength = float(duration)
                    music_stream.append(new_note)

    music_stream.insert(0, tempo.MetronomeMark(number=temp))

    return music_stream



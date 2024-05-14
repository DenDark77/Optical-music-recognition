from music21 import note, stream, tempo, instrument
import pandas as pd
from .model import process_image


def notes_to_music_with_instrument(notes_data, instrument_name, temp):
    music_stream = stream.Stream()
    print(notes_data.split)
    instr = instrument.fromString(instrument_name)
    music_stream.insert(0, instr)
    for note_name in notes_data.split():
        if note_name != '.':
            if '{' in note_name:
                notes_with_duration = note_name.strip('{}').split(',')
                for note_with_duration in notes_with_duration:
                    note_t, duration = note_with_duration.split('/')
                    new_note = note.Note(note_t)
                    new_note.duration.quarterLength = float(duration)
                    music_stream.append(new_note)
            elif '/' in note_name:
                note_t, duration = note_name.split('/')
                if note_t:
                    new_note = note.Note(note_t)
                    new_note.duration.quarterLength = float(duration)
                    music_stream.append(new_note)

    music_stream.insert(0, tempo.MetronomeMark(number=temp))

    return music_stream


def prediction(input_file):
    print(input_file)
    prediction_note = process_image(input_file)
    unpacked_data = prediction_note[0]
    formatted_data = " ".join(unpacked_data)
    return formatted_data

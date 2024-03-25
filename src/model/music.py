from music21 import note, stream, tempo, instrument


def notes_to_music_with_instrument(notes_sequence, instrument_name, temp):
    music_stream = stream.Stream()

    instr = instrument.fromString(instrument_name)
    music_stream.insert(0, instr)

    for note_name in notes_sequence:
        if len(note_name) == 2:
            new_note = note.Note(note_name)
            music_stream.append(new_note)

    music_stream.insert(0, tempo.MetronomeMark(number=temp))

    return music_stream



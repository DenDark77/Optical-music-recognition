from .preprocessing import *
from .staff_removal import *
from .helper_methods import *

import argparse
import os
import datetime

# Initialize parser
# parser = argparse.ArgumentParser()
# parser.add_argument("inputfolder", help = "Input File")
# parser.add_argument("outputfolder", help = "Output File")
#
# args = parser.parse_args()
#
# with open(f"{args.outputfolder}/Output.txt", "w") as text_file:
#     text_file.write("Input Folder: %s" % args.inputfolder)
#     text_file.write("Output Folder: %s" % args.outputfolder)
#     text_file.write("Date: %s" % datetime.datetime.now())


# Threshold for line to be considered as an initial staff line #
threshold = 0.8
filename = 'recognize/model/model.sav'
model = pickle.load(open(filename, 'rb'))
accidentals = ['x', 'hash', 'b', 'symbol_bb', 'd']


def preprocessing(inputfolder):
    # Get image and its dimensions #
    print(inputfolder)
    height, width, in_img = preprocess_img(f'{inputfolder}')

    # Get line thinkness and list of staff lines #
    staff_lines_thicknesses, staff_lines = get_staff_lines(width, height, in_img, threshold)

    # Remove staff lines from original image #
    cleaned = remove_staff_lines(in_img, width, staff_lines, staff_lines_thicknesses)

    # Get list of cutted buckets and cutting positions #
    cut_positions, cutted = cut_image_into_buckets(cleaned, staff_lines)

    # Get reference line for each bucket #
    ref_lines, lines_spacing = get_ref_lines(cut_positions, staff_lines)

    return cutted, ref_lines, lines_spacing


def get_target_boundaries(label, cur_symbol, y2):
    if label == 'b_8':
        cutted_boundaries = cut_boundaries(cur_symbol, 2, y2)
        label = 'a_8'
    elif label == 'b_8_flipped':
        cutted_boundaries = cut_boundaries(cur_symbol, 2, y2)
        label = 'a_8_flipped'
    elif label == 'b_16':
        cutted_boundaries = cut_boundaries(cur_symbol, 4, y2)
        label = 'a_16'
    elif label == 'b_16_flipped':
        cutted_boundaries = cut_boundaries(cur_symbol, 4, y2)
        label = 'a_16_flipped'
    else: 
        cutted_boundaries = cut_boundaries(cur_symbol, 1, y2)

    return label, cutted_boundaries


def get_label_cutted_boundaries(boundary, height_before, cutted):
    # Get the current symbol #
    x1, y1, x2, y2 = boundary
    cur_symbol = cutted[y1-height_before:y2+1-height_before, x1:x2+1]

    # Clean and cut #
    cur_symbol = clean_and_cut(cur_symbol)
    cur_symbol = 255 - cur_symbol

    # Start prediction of the current symbol #
    feature = extract_hog_features(cur_symbol)
    label = str(model.predict([feature])[0])

    return get_target_boundaries(label, cur_symbol, y2)


def process_image(inputfolder):
    cutted, ref_lines, lines_spacing = preprocessing(inputfolder)

    results = []

    for it in range(len(cutted)):
        result = []
        is_started = False

        symbols_boundaries = segmentation(0, cutted[it])
        symbols_boundaries.sort(key=lambda x: (x[0], x[1]))

        for boundary in symbols_boundaries:
            label, cutted_boundaries = get_label_cutted_boundaries(boundary, 0, cutted[it])

            if label == 'clef':
                is_started = True

            for cutted_boundary in cutted_boundaries:
                _, y1, _, y2 = cutted_boundary
                if is_started and label != 'barline' and label != 'clef':
                    text = text_operation(label, ref_lines[it], lines_spacing[it], y1, y2)

                    if (label == 't_2' or label == 't_4') and not result:
                        result.append(text)
                    elif label in accidentals:
                        result.append(text)
                    else:
                        if result and result[-1] in accidentals:
                            text = result.pop()[:-1] + text

                        if result and result[-1] in ['t_2', 't_4']:
                            result[-1] = f'\meter<"{text}/{result[-1]}">'
                        else:
                            result.append(text)

        results.append(result)

    return results


# def main():
#     try:
#         os.mkdir(args.outputfolder)
#     except OSError as error:
#         pass
#
#     list_of_images = os.listdir(args.inputfolder)
#     for _, fn in enumerate(list_of_images):
#         # Open the output text file #
#         file_prefix = fn.split('.')[0]
#         f = open(f"{args.outputfolder}/{file_prefix}.txt", "w")
#
#         # Process each image separately #
#         try:
#             process_image(args.inputfolder, fn, f)
#         except Exception as e:
#             print(e)
#             print(f'{args.inputfolder}-{fn} has been failed !!')
#             pass
#
#         f.close()
#     print('Finished !!')


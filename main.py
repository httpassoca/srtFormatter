import os
import glob
import logging
from blacklist_strings import BLACKLIST_STRINGS

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def remove_blacklisted_subtitles(input_directory, output_directory):
    def process_file(input_file, output_file):
        logging.info(f'Start processing file: {input_file}')
        with open(input_file, 'r', encoding='utf-8') as infile, open(output_file, 'w', encoding='utf-8') as outfile:
            subtitle_blocks = []
            last_text = None
            skip_block = False

            for line in infile:
                if line.strip().isdigit():
                    if not skip_block:
                        # Check for repeated subtitles and merge time range if necessary
                        if subtitle_blocks and last_text == subtitle_blocks[-1][-1].strip():
                            subtitle_blocks[-1][1] = subtitle_blocks[-1][1].split(' --> ')[0] + ' --> ' + subtitle_blocks[-2][1].split(' --> ')[1]
                        else:
                            subtitle_blocks.append([])
                    skip_block = False
                elif line.strip() and '-->' in line:
                    if not skip_block:
                        subtitle_blocks[-1].append(line)
                elif any(blacklist_string in line for blacklist_string in BLACKLIST_STRINGS):
                    skip_block = True
                    logging.info(f'Blacklisted string found, skipping block in file: {input_file}')
                else:
                    if not skip_block:
                        subtitle_blocks[-1].append(line)
                        last_text = line.strip()

            # Write processed blocks to file
            for block in subtitle_blocks:
                outfile.write('\n'.join(block) + '\n')

        logging.info(f'Finished processing file: {input_file} -> {output_file}')

    # Ensure output directory exists
    if not os.path.exists(output_directory):
        os.makedirs(output_directory)
        logging.info(f'Created output directory: {output_directory}')

    # Find all SRT files in the input directory
    srt_files = glob.glob(os.path.join(input_directory, '*.srt'))

    if not srt_files:
        logging.warning(f'No SRT files found in directory: {input_directory}')
        return

    for file_path in srt_files:
        file_name = os.path.basename(file_path)
        output_file_path = os.path.join(output_directory, file_name.rsplit('.', 1)[0] + '.srt')
        process_file(file_path, output_file_path)

# Example usage
remove_blacklisted_subtitles('input', 'output')  # Replace 'input' and 'output' with your directory names

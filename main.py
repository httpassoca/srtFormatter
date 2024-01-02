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
            subtitle_block = []
            last_text = None
            last_block_start = None
            skip_block = False

            for line in infile:
                if line.strip().isdigit():
                    if not skip_block and subtitle_block:
                        if last_text is not None and subtitle_block[-1].strip() == last_text:
                            # Modify the time range of the last block instead of writing a new one
                            modified_block = subtitle_block[:-1] + [last_block_start + ' --> ' + subtitle_block[1].split(' --> ')[1]] + subtitle_block[-1:]
                            outfile.write(''.join(modified_block) + '\n')
                        else:
                            outfile.write(''.join(subtitle_block) + '\n')

                    subtitle_block = [line]
                    skip_block = False
                elif line.strip() and '-->' in line:
                    last_block_start = line.split(' --> ')[0]
                    subtitle_block.append(line)
                elif any(blacklist_string in line for blacklist_string in BLACKLIST_STRINGS):
                    skip_block = True
                    logging.info(f'Blacklisted string found, skipping block in file: {input_file}')
                else:
                    subtitle_block.append(line)
                    last_text = line.strip()

            if not skip_block and subtitle_block:
                outfile.write(''.join(subtitle_block))

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
remove_blacklisted_subtitles('input', 'output') 

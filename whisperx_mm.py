import os
import subprocess
import csv
import json
import string
from moviepy.editor import VideoFileClip

def process_audio_files(input_directory, output_directory):
    # Ensure the output directory exists
    if not os.path.exists(output_directory):
        os.makedirs(output_directory)

    # Iterate over each file in the input directory
    for filename in os.listdir(input_directory):
        if filename.lower().endswith(('.mp4')):  # Add or remove file extensions as needed
            # remove the file extension
            filename_original = os.path.splitext(filename)[0]
            output_directory_final = os.path.join(output_directory, filename_original)
            if not os.path.exists(output_directory_final):
                os.makedirs(output_directory_final)
            input_path = os.path.join(input_directory, filename)
            audio_output_path = os.path.join(output_directory_final, filename_original + '.mp3')
            audio_vocal_output_path = os.path.join(output_directory_final, filename_original + '_vocals.wav')
            # file_output_dir = os.path.join(output_directory, filename)

            # # Create a directory for this file's output
            # if not os.path.exists(file_output_dir):
            #     os.makedirs(file_output_dir)

            # Construct the command
            separate_audio_from_video(input_path,output_directory_final, filename_original)
            spleeter(output_directory_final, input_path)
            whisperx_transcription(audio_output_path,output_directory_final)
            whisperx_transcription(audio_vocal_output_path, output_directory_final)
            json_to_csv(output_directory_final)


# Example usage

def spleeter(input_directory, input_path):
   #
    # Construct the command
    # separate the audio into vocals and accompaniment for the input file
    
    command = [
        "spleeter", "separate", 
        "-p", "spleeter:2stems",
        "-o", input_directory,
        "-d", "3000",
        input_path,
        "-f", "{filename}_{instrument}.{codec}"
    ]

    # Execute the command   
    subprocess.run(command)


def separate_audio_from_video(input_path, input_directory, filename):
    video = VideoFileClip(input_path)
    output_path = os.path.join(input_directory,filename + '.mp3')
    # Extract the audio
    audio = video.audio
    
    # Write the audio to a file
    audio.write_audiofile(output_path)
    
    # Close the video and audio clips to free up resources
    video.close()
    audio.close()


def whisperx_transcription(input_path, output_directory):
    command = [
                    "whisperx", input_path, 
                    "--output_dir", output_directory,
                    "--output_format", "all",
                    "--device", "cuda",
                    "--language", "en",
                    "--model", "large-v3",
                    "--align_model", "WAV2VEC2_ASR_LARGE_LV60K_960H",
                    "--batch_size", "8",
                    "--highlight_words","True"
                ]

    # Execute the command
    subprocess.run(command)

def json_to_csv(json_directory):
    for filename in os.listdir(json_directory):
        if filename.lower().endswith(('.json')): 
            filename_original = os.path.splitext(filename)[0]
            json_file_path = os.path.join(json_directory, filename)
            with open(json_file_path, 'r') as file:
                data = json.load(file)

            # Path to the CSV file you want to create
            csv_file_path = os.path.join(json_directory, filename_original + '_wordlevel.csv')

            translator = str.maketrans('', '', string.punctuation)

            with open(csv_file_path, 'w', newline='',encoding='utf-8-sig') as file:
                writer = csv.writer(file)
                # Write the header
                writer.writerow(['word', 'start', 'end'])
                last_end = 0  # Initialize last_end to 0 for the start
                # Write the data
                for segment in data['segments']:
                    # if segment['start'] > last_end:
                    #     add_silence(writer, last_end, segment['start'])
                    for i, word_info in enumerate(segment['words']):
                        # Remove punctuation from the word
                        start = word_info.get('start', '')
                        end = word_info.get('end', '')
                    
                        if (start != ''):
                            # Write the current word
                            clean_word = word_info['word'].translate(translator)
                            writer.writerow([clean_word, start, end])
                print("Updated CSV file created successfully.")
                print(f"CSV file created successfully at {csv_file_path}.")


def initiate_process(input_directory, output_directory):
    process_audio_files(input_directory, output_directory)
    for folders in os.listdir(input_directory):
        process_audio_files(os.path.join(input_directory, folders), output_directory)
    
if __name__ == "__main__":
    initiate_process("input", "output") 
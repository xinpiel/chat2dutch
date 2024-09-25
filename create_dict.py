import csv
import pandas as pd
from datetime import datetime
import pdb

# Function to read words from CSV file
def read_words_from_csv(file_name):
    words = []
    with open(file_name, mode='r', encoding='utf-8') as csv_file:
        csv_reader = csv.reader(csv_file)
        next(csv_reader)  # Skip header
        for row in csv_reader:
            if len(row) > 0:  # Ensure the row has at least one column
                words.append(row[0])
    return words

# Function to read word frequencies from CSV file
def read_word_frequencies_from_csv(file_name):
    word_frequencies = {}
    with open(file_name, mode='r', encoding='utf-8') as csv_file:
        csv_reader = csv.reader(csv_file)
        next(csv_reader)  # Skip header
        for row in csv_reader:
            print(f"Processing row: {row}")  # Debugging output
            #pdb.set_trace()
            if len(row) >= 2:  # Ensure the row has at least two columns
                word = row[0]
                try:
                    frequency = int(row[1])
                except ValueError:
                    print(f"Invalid frequency value for word '{word}': {row[1]}")
                    frequency = 0
                word_frequencies[word] = frequency
            else:
                print(f"Skipping invalid row: {row}")  # Skip rows that do not have at least two columns
    return word_frequencies

# Function to create and populate the Dutch dictionary CSV file
def create_dutch_dictionary_csv(words, word_frequencies, output_file='dutch_dictionary.csv'):
    data = []
    current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    for word in words:
        # Get frequency from word_frequencies dictionary, default to 0 if not found
        frequency = word_frequencies.get(word, 0)
        if frequency != 0:
            print(f"Word '{word}' found in frequency file with frequency {frequency}.")
        data.append([word, frequency, 0, current_time])  # Status set to 0 (unknown)

    # Sort the data by frequency in descending order
    data.sort(key=lambda x: x[1], reverse=True)

    # Write the data to a CSV file
    with open(output_file, mode='w', newline='', encoding='utf-8') as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow(['Word', 'Frequency', 'Status', 'Last Updated'])  # Write header
        writer.writerows(data)

    print(f"\nDutch dictionary CSV file created and populated at '{output_file}'")

if __name__ == "__main__":
    # Read words from dutch_words.csv
    dutch_words = read_words_from_csv('dutch_words.csv')

    # Read word frequencies from dutch_word_frequency.csv
    word_frequencies = read_word_frequencies_from_csv('dutch_word_frequency.csv')

    # Create and populate the Dutch dictionary CSV file
    create_dutch_dictionary_csv(dutch_words, word_frequencies)
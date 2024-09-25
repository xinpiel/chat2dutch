import requests
import csv
import re
import pdb

# URL of the Dutch frequency list CSV file
# Replace with the actual URL of the Dutch frequency data
url = "https://raw.githubusercontent.com/hermitdave/FrequencyWords/master/content/2018/nl/nl_50k.txt"

# Name of the file to save the downloaded CSV
csv_file_name = "dutch_word_frequency.csv"

def download_csv(url, file_name):
    try:
        # Send a GET request to the URL
        response = requests.get(url)
        # Raise an error for bad status codes
        response.raise_for_status()

        # Write the content to a CSV file
        with open(file_name, "wb") as file:
            file.write(response.content)

        print(f"CSV file downloaded successfully and saved as '{file_name}'")
    except requests.exceptions.RequestException as e:
        print(f"Error downloading the file: {e}")

def process_csv(file_name, output_file_name):
    try:
        with open(file_name, mode='r', encoding='utf-8') as csv_file:
            lines = csv_file.readlines()
            header = ['Word', 'Frequency']  # Define the header

            with open(output_file_name, mode='w', newline='', encoding='utf-8') as output_file:
                writer = csv.writer(output_file)
                writer.writerow(header)  # Write the header

                for index, line in enumerate(lines):
                    print(f"Processing line: {line.strip()}")  # Debugging output
                    row = re.split(r'\s+', line.strip())  # Split by one or more spaces
                    if len(row) >= 2:  # Ensure the row has at least two columns
                        word = row[0]
                        try:
                            frequency = int(row[1])
                        except ValueError:
                            print(f"Invalid frequency value for word '{word}': {row[1]}")
                            frequency = 0
                        writer.writerow([word, frequency])
                        if (index + 1) % 100 == 0:
                            print(f"{index + 1} words processed: {row}")
                    else:
                        print(f"Skipping invalid row: {row}")  # Skip rows that do not have at least two columns

        print(f"\nProcessed CSV file saved as '{output_file_name}'")
        
        # Verify the output file
        with open(output_file_name, mode='r', encoding='utf-8') as verify_file:
            first_line = verify_file.readline().strip()
            print(f"First line of output file: {first_line}")
            
    except Exception as e:
        print(f"Error processing the file: {e}")

if __name__ == "__main__":
    # Download the CSV file
    download_csv(url, csv_file_name)

    # Process the CSV file and output progress every 100 words
    process_csv(csv_file_name, csv_file_name)

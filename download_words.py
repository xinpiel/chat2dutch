import requests
import csv

# URL of the OpenTaal word list
word_list_url = 'https://raw.githubusercontent.com/OpenTaal/opentaal-wordlist/master/wordlist.txt'

# Function to download the word list
def download_word_list(url):
    response = requests.get(url)
    if response.status_code == 200:
        return response.text.splitlines()  # Return as a list of words
    else:
        print("Failed to download the word list.")
        return []

# Function to filter out numeric words
def filter_words(words):
    return [word for word in words if not any(char.isdigit() for char in word)]

def save_to_csv(words, csv_filename='dutch_words.csv'):
    with open(csv_filename, mode='w', newline='', encoding='utf-8') as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow(['Word'])  # Write header
        for index, word in enumerate(words):
            writer.writerow([word])  # Write each word in a new row
            if (index + 1) % 100 == 0:
                print(f"{index + 1} words processed: {words[index - 99:index + 1]}")

    print(f"\nWord list saved to {csv_filename}")

if __name__ == "__main__":
    # Download the OpenTaal word list
    dutch_words = download_word_list(word_list_url)

    # Filter out numeric words
    filtered_words = filter_words(dutch_words)

    # Save the word list to a CSV file
    save_to_csv(filtered_words)

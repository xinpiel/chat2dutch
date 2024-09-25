import json
import os
from datetime import datetime
import csv
import threading
from openai import OpenAI
import openai
import pandas as pd

class LanguageLearningManager:
    def __init__(self):
        self.settings_file = 'profile_settings.json'
        self.daily_target = None
        self.milestones_rewards = []
        self.client, self.model = self.get_openai_connection()
        self.csv_file_path = 'dutch_dictionary.csv'
        self.search_history_file = 'search_history.csv'
        self.dictionary = self.load_dictionary_from_csv()
        self.search_history = self.load_search_history()
        self.words_quiz = []
        self.openai_client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.current_quiz_words = []
        self.current_quiz_index = 0
        self.unknown_word_count = 0
        self.total_words_learned = 0
        self.load_data_from_json()  # Load data from JSON file

    def get_openai_connection(self):
        api_key = os.getenv("OPENAI_API_KEY")
        model = os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")
        client = OpenAI(api_key=api_key)
        return client, model

    def load_data_from_json(self):
        if os.path.exists(self.settings_file):
            with open(self.settings_file, 'r') as f:
                data = json.load(f)
                self.daily_target = data.get('daily_target')
                self.milestones_rewards = data.get('milestones_rewards', [])
                self.total_words_learned = data.get('total_words_learned', 0)
        else:
            self.daily_target = None
            self.milestones_rewards = []
            self.total_words_learned = 0
            self.save_data_to_json()

    def save_data_to_json(self):
        data = {
            'daily_target': self.daily_target,
            'milestones_rewards': self.milestones_rewards,
            'total_words_learned': self.total_words_learned
        }
        with open(self.settings_file, 'w') as f:
            json.dump(data, f, indent=2)

    def get_daily_target(self):
        return self.daily_target

    def set_daily_target(self, target):
        self.daily_target = target
        self.save_data_to_json()
        return f"Daily target set to {target} words."

    def get_milestones_rewards(self):
        return pd.DataFrame(self.milestones_rewards, columns=["milestone", "reward"])

    def update_milestones_rewards(self, df):
        # Convert DataFrame to list of dictionaries
        self.milestones_rewards = df.to_dict('records')
        # Filter out empty rows and convert milestone to int
        self.milestones_rewards = [
            {"milestone": int(mr["milestone"]), "reward": mr["reward"]}
            for mr in self.milestones_rewards
            if pd.notna(mr["milestone"]) and pd.notna(mr["reward"])
        ]
        self.save_data_to_json()
        return "Milestones and rewards updated successfully."

    def clear_milestones_rewards(self):
        self.daily_target = []
        self.milestones_rewards = []
        self.save_data_to_json()
        return "All milestones and rewards cleared successfully."

    def has_daily_target(self):
        return self.daily_target is not None

    def has_milestones_rewards(self):
        return len(self.milestones_rewards) > 0

    def load_dictionary_from_csv(self):
        dictionary = []
        with open(self.csv_file_path, mode='r', encoding='utf-8') as csv_file:
            csv_reader = csv.reader(csv_file)
            next(csv_reader)  # Skip header
            for row in csv_reader:
                word, frequency, status, last_updated = row
                dictionary.append({
                    'word': word,
                    'frequency': int(frequency),
                    'status': int(status),
                    'last_updated': datetime.strptime(last_updated, '%Y-%m-%d %H:%M:%S')
                })
        return dictionary

    def load_search_history(self):
        if not os.path.exists(self.search_history_file):
            return []
        with open(self.search_history_file, mode='r', encoding='utf-8') as csv_file:
            return [row[0] for row in csv.reader(csv_file)]

    def save_search_history(self):
        with open(self.search_history_file, mode='w', newline='', encoding='utf-8') as csv_file:
            csv_writer = csv.writer(csv_file)
            for w in self.search_history:
                csv_writer.writerow([w])

    def save_dictionary_to_csv(self):
        with open(self.csv_file_path, mode='w', newline='', encoding='utf-8') as csv_file:
            writer = csv.writer(csv_file)
            writer.writerow(['Word', 'Frequency', 'Status', 'Last Updated'])
            for entry in self.dictionary:
                writer.writerow([
                    entry['word'],
                    entry['frequency'],
                    entry['status'],
                    entry['last_updated'].strftime('%Y-%m-%d %H:%M:%S')
                ])

    def daily_word_quiz(self):
        # Check if daily target is set
        if not self.has_daily_target():
            raise ValueError("Daily target must be set before starting the quiz.")   
        # Check if milestones and rewards are set
        if not self.has_milestones_rewards():
            raise ValueError("Milestones and rewards must be set before starting the quiz.")
        self.current_quiz_words = self.select_words()
        self.current_quiz_index = 0
        self.unknown_word_count = 0
        return self.get_next_quiz_word()

    def get_next_quiz_word(self):
        if self.unknown_word_count >= 10:
            return None
        if self.current_quiz_index < len(self.current_quiz_words):
            word = self.current_quiz_words[self.current_quiz_index]
            word_info = self.get_word_info(word)
            self.current_quiz_index += 1
            self.update_search_history(word, False)  # Add to history as unknown
            return word_info
        else:
            return None

    def select_words(self):
        prioritized_words = []
        # First, select from search history if it exists
        if os.path.exists(self.search_history_file):
            for word in self.search_history:
                dict_entry = next((entry for entry in self.dictionary if entry['word'] == word), None)
                if dict_entry:
                    prioritized_words.append(word)
        # Add high-frequency unknown words directly from the sorted dictionary
        for entry in self.dictionary:
            if entry['status'] == 0 and entry['word'] not in prioritized_words:
                prioritized_words.append(entry['word'])
                if len(prioritized_words) >= self.daily_target:
                    break
        return prioritized_words

    def is_dutch_word(self, word):
        check_prompt = f"Is '{word}' a Dutch word? Respond with only 'Yes' or 'No'."
        check_response = self.openai_client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a Dutch language expert."},
                {"role": "user", "content": check_prompt}
            ]
        )
        return check_response.choices[0].message.content.strip().lower() == "yes"

    def get_word_info(self, word, is_searched=False):
        if is_searched:
            is_dutch = self.is_dutch_word(word)
            if not is_dutch:
                return f"'{word}' is not recognized as a Dutch word. Please check your spelling or try a different word."

        prompt = f"""
        Provide information for the Dutch word '{word}':
        1. Translation in English
        2. Translation in Chinese (with pinyin)
        3. Variations (if any)
        4. Two example sentences in Dutch with English translations
        5. A brief explanation of its usage
        Format the response as follows:
        Word: {word}
        English: [English translation]
        Chinese: [Chinese translation (pinyin)]
        Examples:
        1. [Dutch sentence] ([English translation])
        2. [Dutch sentence] ([English translation])
        Usage: [Brief explanation of usage]
        """
        response = self.openai_client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant for learning Dutch."},
                {"role": "user", "content": prompt}
            ]
        )
        word_info = response.choices[0].message.content

        if is_searched and is_dutch:
            self.update_search_history(word, False)
        return word_info

    def update_search_history(self, word, is_known):
        if not self.search_history:
            self.search_history = self.load_search_history()

        if is_known:
            # Remove the word if it's marked as known
            if word in self.search_history:
                self.search_history.remove(word)
        else:
            # Add or move the word to the beginning if it's unknown
            if word in self.search_history:
                self.search_history.remove(word)
            self.search_history.insert(0, word)
        
        # Update the file with the new order
        with open(self.search_history_file, mode='w', newline='', encoding='utf-8') as csv_file:
            csv_writer = csv.writer(csv_file)
            for w in self.search_history:
                csv_writer.writerow([w])

    def update_word_status(self, word, status):
        for entry in self.dictionary:
            if entry['word'] == word:
                entry['status'] = 1 if status else 0
                entry['last_updated'] = datetime.now()
                break
        
        self.save_dictionary_to_csv()

    def format_word_info(self, word_info):
        if word_info:
            return f"Word: {word_info['word']}\nFrequency: {word_info['frequency']}\nStatus: {'known' if word_info['status'] else 'unknown'}\nLast Updated: {word_info['last_updated']}"
        else:
            return "Word not found."

    def check_if_word_learned(self, response):
        # Implement your logic to determine if a word was learned
        return "new word" in response.lower()
    
    def mark_word(self, word, is_known):
        self.update_word_status(word, is_known)
        self.update_search_history(word, is_known)
        if is_known:
            self.total_words_learned += 1
            self.save_data_to_json()
        elif not is_known:
            self.unknown_word_count += 1
        
        achieved_milestones = self.check_milestones()
        return achieved_milestones

    def check_milestones(self):
        achieved_milestones = []
        for milestone in self.milestones_rewards:
            if self.total_words_learned >= int(milestone['milestone']):
                achieved_milestones.append(f"Congratulations! You've learned {milestone['milestone']} words. You've earned: {milestone['reward']}")
        return achieved_milestones

    def __del__(self):
        pass



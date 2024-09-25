import sqlite3
import pandas as pd

def print_dutch_dictionary_sample():
    # Connect to the database
    conn = sqlite3.connect('dutch_dictionary.db')
    
    # Read the entire Words table into a pandas DataFrame
    df = pd.read_sql_query("SELECT * FROM Words", conn)
    
    # Close the connection
    conn.close()
    
    # Print the total number of words
    print(f"Total words in the dictionary: {len(df)}")
    
    # Print the first 10 entries
    print("\nFirst 10 entries:")
    print(df.head(10).to_string(index=False))
    
    # Print the last 10 entries
    print("\nLast 10 entries:")
    print(df.tail(10).to_string(index=False))
    
    # Print some statistics
    print("\nDictionary Statistics:")
    print(f"Words with pronunciation: {df['pronunciation'].notna().sum()}")
    print(f"Words with variations: {df['variations'].notna().sum()}")
    print(f"Words with examples: {df['examples'].notna().sum()}")
    print(f"Words with translations: {df['translation'].notna().sum()}")
    
    # Print a random sample of 5 words
    print("\nRandom sample of 5 words:")
    print(df.sample(5).to_string(index=False))

def print_user_profile_sample():
    conn = sqlite3.connect('profile_setting.db')
    cursor = conn.cursor()
    
    # Print daily target
    cursor.execute('SELECT daily_target FROM user_profile WHERE id = 1')
    daily_target = cursor.fetchone()
    if daily_target:
        print(f"\nDaily Target: {daily_target[0]}")
    else:
        print("\nNo daily target set.")
    
    # Print milestones and rewards
    cursor.execute('SELECT words, reward FROM milestones_rewards ORDER BY words')
    milestones = cursor.fetchall()
    
    print("\nMilestones and Rewards:")
    if milestones:
        for words, reward in milestones:
            print(f"{words} words: {reward}")
    else:
        print("No milestones set.")
    
    conn.close()

if __name__ == "__main__":
    print_dutch_dictionary_sample()
    print_user_profile_sample()
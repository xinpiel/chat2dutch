import sqlite3
from datetime import datetime
import json

def init_db():
    conn = sqlite3.connect('profile_setting.db')
    cursor = conn.cursor()
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS user_profiles
    (user_id INTEGER PRIMARY KEY, daily_target INTEGER, total_words_learned INTEGER,
     milestones TEXT)
    ''')
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS milestones
    (id INTEGER PRIMARY KEY, words INTEGER, reward TEXT)
    ''')
    conn.commit()
    conn.close()

def get_user_profile(user_id):
    conn = sqlite3.connect('profile_setting.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM user_profiles WHERE user_id = ?', (user_id,))
    profile = cursor.fetchone()
    conn.close()
    if profile:
        return {
            'user_id': profile[0],
            'daily_target': profile[1],
            'total_words_learned': profile[2],
            'milestones': json.loads(profile[3]) if profile[3] else []
        }
    return None

def update_user_profile(user_id, daily_target=None, milestones=None):
    conn = sqlite3.connect('profile_setting.db')
    cursor = conn.cursor()
    updates = []
    params = []
    if daily_target is not None:
        updates.append('daily_target = ?')
        params.append(daily_target)
    if milestones is not None:
        updates.append('milestones = ?')
        params.append(json.dumps(milestones))
    
    if updates:
        query = f"INSERT OR REPLACE INTO user_profiles (user_id, daily_target, total_words_learned, milestones) VALUES (?, COALESCE(?, (SELECT daily_target FROM user_profiles WHERE user_id = ?)), COALESCE((SELECT total_words_learned FROM user_profiles WHERE user_id = ?), 0), ?)"
        params = [user_id, daily_target, user_id, user_id, json.dumps(milestones)]
        cursor.execute(query, params)
        conn.commit()
    conn.close()

def increment_words_learned(user_id, count=1):
    conn = sqlite3.connect('profile_setting.db')
    cursor = conn.cursor()
    cursor.execute('UPDATE user_profiles SET total_words_learned = total_words_learned + ? WHERE user_id = ?', (count, user_id))
    conn.commit()
    conn.close()

def get_milestones():
    conn = sqlite3.connect('profile_setting.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM milestones ORDER BY words')
    milestones = [{'id': row[0], 'words': row[1], 'reward': row[2]} for row in cursor.fetchall()]
    conn.close()
    return milestones

def check_milestones(user_id):
    profile = get_user_profile(user_id)
    if not profile:
        return None
    
    total_words = profile['total_words_learned']
    achieved_milestones = []
    
    for milestone in get_milestones():
        if total_words >= milestone['words']:
            achieved_milestones.append(f"Congratulations! You've reached {milestone['words']} words. Reward: {milestone['reward']}")

    return achieved_milestones if achieved_milestones else None

def manage_milestones(action, milestone_id=None, words=None, reward=None):
    conn = sqlite3.connect('profile_setting.db')
    cursor = conn.cursor()
    
    if action == 'add':
        cursor.execute('INSERT INTO milestones (words, reward) VALUES (?, ?)', (words, reward))
    elif action == 'update':
        cursor.execute('UPDATE milestones SET words = ?, reward = ? WHERE id = ?', (words, reward, milestone_id))
    elif action == 'delete':
        cursor.execute('DELETE FROM milestones WHERE id = ?', (milestone_id,))
    
    conn.commit()
    conn.close()
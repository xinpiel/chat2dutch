import gradio as gr
from language_learning_manager import LanguageLearningManager
import os
import pandas as pd
import pdb

# Disable Gradio analytics
os.environ['GRADIO_ANALYTICS_ENABLED'] = 'False'

manager = LanguageLearningManager()

def chat(message, history):
    try:
        if message.lower() == "daily quiz":
            word_info = manager.daily_word_quiz()
            if word_info:
                history.append(("System", "Here's your first word:"))
                history.append(("Word", word_info))
                return "", history, gr.update(visible=True), gr.update(visible=True), gr.update(visible=True)
            else:
                history.append(("System", "No more words in the quiz."))
                return "", history, gr.update(visible=False), gr.update(visible=False), gr.update(visible=False)
        elif message.strip().endswith('?'):
            # Handle searched word
            searched_word = message.strip()[:-1]  # Remove the question mark and any trailing spaces
            word_info = manager.get_word_info(searched_word, is_searched=True)
            if "not recognized as a Dutch word" in word_info:
                history.append(("System", word_info))
            else:
                history.append(("System", f"Here's the information for '{searched_word}':"))
                history.append(("Word", word_info))
            return "", history, gr.update(visible=False), gr.update(visible=False), gr.update(visible=False)
        else:
            # Handle other chat messages here
            response = "I'm here to help you learn Dutch. Type 'daily quiz' to start a quiz or end your message with '?' to search for a word."
            history.append((message, response))
            return "", history, gr.update(visible=False), gr.update(visible=False), gr.update(visible=False)

    except Exception as e:
        error_message = f"An error occurred: {str(e)}"
        history.append(("System", error_message))
        return "", history, gr.update(visible=False), gr.update(visible=False), gr.update(visible=False)

def submit_quiz(is_known, history):
    try:
        current_word = manager.current_quiz_words[manager.current_quiz_index - 1]
        achieved_milestones = manager.mark_word(current_word, is_known)
        
        status_message = "known" if is_known else "unknown"
        history.append(("System", f"Word '{current_word}' marked as {status_message}."))
        
        # Display achieved milestones
        for milestone in achieved_milestones:
            history.append(("System", milestone))
        
        word_info = manager.get_next_quiz_word()
        if word_info:
            history.append(("System", "Here's the next word:"))
            history.append(("Word", word_info))
            return history, gr.update(visible=True), gr.update(visible=True), gr.update(visible=True)
        else:
            print("Quiz completed. 10 unknown words encountered.")  # Debugging statement
            history.append(("System", "Quiz completed. You have encountered 10 unknown words. Type 'daily quiz' to start a new one."))
            return history, gr.update(visible=False), gr.update(visible=False), gr.update(visible=False)
    except Exception as e:
        error_message = f"An error occurred: {str(e)}"
        print(error_message)  # Debugging statement
        history.append(("System", error_message))
        return history, gr.update(visible=False), gr.update(visible=False), gr.update(visible=False)

def set_target(target):
    manager.set_daily_target(int(target))
    return f"Target set to {target} words."

def add_milestone_reward(data):
    new_row = pd.DataFrame([["", ""]], columns=["milestone", "reward"])
    return pd.concat([data, new_row], ignore_index=True)

def clear_milestones_rewards():
    result = manager.clear_milestones_rewards()
    return result, pd.DataFrame(columns=["milestone", "reward"])

def submit_milestones_rewards(data):
    # Remove empty rows
    data = data.dropna(subset=['milestone', 'reward'], how='all')
    result = manager.update_milestones_rewards(data)
    updated_table = manager.get_milestones_rewards()
    return result, updated_table


with gr.Blocks() as interface:
    gr.HTML("<h1>Chat2Dutch - An app to learn Dutch</h1>")
    
    chatbot = gr.Chatbot()
    msg = gr.Textbox()
    
    with gr.Row():
        known_button = gr.Button("Known", size="sm")
        unknown_button = gr.Button("Unknown", size="sm")
        clear = gr.Button("Clear")

    with gr.Tab("Quiz"):
        with gr.Column(visible=False) as quiz_column:
            pass

    with gr.Tab("Settings"):
        with gr.Group():
            gr.Markdown("### Daily Target")
            target_input = gr.Number(label="Set Target", value=manager.get_daily_target())
            target_button = gr.Button("Set Target")
            target_output = gr.Textbox(label="Target Status", interactive=False)
        
        with gr.Group():
            gr.Markdown("### Manage Milestones and Rewards")
            milestones_table = gr.DataFrame(
                value=manager.get_milestones_rewards(),
                headers=["Milestone", "Reward"],
                label="Milestones and Rewards",
                interactive=True,
                col_count=(2, "fixed")
            )
            with gr.Row():
                add_button = gr.Button("Add Row")
                clear_button = gr.Button("Clear All")
                submit_button = gr.Button("Submit")
            update_output = gr.Textbox(label="Update Status", interactive=False)

    msg.submit(chat, inputs=[msg, chatbot], outputs=[msg, chatbot, quiz_column, known_button, unknown_button])
    clear.click(lambda: None, None, chatbot, queue=False)
    known_button.click(submit_quiz, inputs=[gr.State(True), chatbot], outputs=[chatbot, known_button, unknown_button])
    unknown_button.click(submit_quiz, inputs=[gr.State(False), chatbot], outputs=[chatbot, known_button, unknown_button])
    target_button.click(set_target, inputs=[target_input], outputs=[target_output])

    add_button.click(
        add_milestone_reward,
        inputs=[milestones_table],
        outputs=[milestones_table]
    )
    clear_button.click(
        clear_milestones_rewards,
        outputs=[update_output, milestones_table]
    )
    submit_button.click(
        submit_milestones_rewards,
        inputs=[milestones_table],
        outputs=[update_output, milestones_table]
    )

if __name__ == "__main__":
    interface.launch()
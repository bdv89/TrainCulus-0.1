import tkinter as tk
from tkinter import ttk
import random
import time
import csv
from datetime import datetime
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# Default number of questions
num_questions = 10

# Function to generate random addition or subtraction problem
def generate_problem():
    num1 = random.randint(1, 9)
    num2 = random.randint(1, 9)
    operator = random.choice(['+', '-'])

    # Ensure no negative results for subtraction
    if operator == '-' and num1 < num2:
        num1, num2 = num2, num1  # Swap to ensure positive result

    problem = f"{num1} {operator} {num2}"
    answer = eval(problem)
    return problem, answer

# Function to start the mental math challenge
def start_challenge():
    global problems, answers, user_answers, times, start_time, entry_count
    problems = []
    answers = []
    user_answers = []
    times = []
    entry_count = 0

    # Clear previous problems from the table
    table.delete(*table.get_children())

    # Generate problems based on the number of questions
    for i in range(num_questions):
        problem, answer = generate_problem()
        problems.append(problem)
        answers.append(answer)
        table.insert("", "end", values=(problem, ""))  # Add problem to table

    start_time = time.time()  # Start the timer
    entry.focus()  # Focus on the input field
    entry.delete(0, tk.END)  # Clear the input field at the start

# Function to handle user input when pressing spacebar
def check_answer(event):
    global entry_count, start_time, times

    if event.keysym == 'space':  # Trigger on spacebar press
        # Get the current user input
        user_input = entry.get().strip()

        try:
            # Convert input to integer and check the answer
            user_answer = int(user_input)
            user_answers.append(user_answer)
            end_time = time.time()  # Stop timer for this answer
            elapsed_time = round((end_time - start_time) * 1000, 2)  # Calculate time taken in milliseconds
            times.append(elapsed_time)
            start_time = end_time  # Reset timer for next problem

            # Update table with the user's answer
            table.item(table.get_children()[entry_count], values=(problems[entry_count], user_answer))
            entry_count += 1

            # Check if all problems are solved
            if entry_count == num_questions:
                show_results()
                return

            entry.delete(0, tk.END)  # Clear the input field for the next question

        except ValueError:
            # If input is not a valid integer, clear the input
            entry.delete(0, tk.END)

# Function to show results after all answers are given
def show_results():
    result_window = tk.Toplevel(root)
    result_window.title("Results")
    result_window.geometry("500x350")
    result_window.configure(bg="black")


    # Define styles for correct and incorrect answers
    style = ttk.Style()
    style.configure("Correct.TREEVIEW", background="light green")
    style.configure("Incorrect.TREEVIEW", background="light coral")
    style.configure("Custom.Treeview", 
                background="black",  # Couleur de fond
                foreground="white",  # Couleur du texte
                fieldbackground="black",  # Couleur de fond des champs de saisie
                font=('Arial', 12))  # Police de texte


    # Create a Treeview to display results in a structured table
    columns = ('Problem', 'Your Answer', 'Correct Answer', 'Time (ms)')
    result_table = ttk.Treeview(result_window, columns=columns, show="headings", height=num_questions + 1)

    # Set column widths
    result_table.column('Problem', width=100)
    result_table.column('Your Answer', width=100)
    result_table.column('Correct Answer', width=100)
    result_table.column('Time (ms)', width=100)

    result_table.heading('Problem', text='Problem')
    result_table.heading('Your Answer', text='Your Answer')
    result_table.heading('Correct Answer', text='Correct Answer')
    result_table.heading('Time (ms)', text='Time (ms)')

    # Populate the results table
    correct_answers = 0
    total_time = 0
    for i in range(num_questions):
        if user_answers[i] == answers[i]:
            correct_answers += 1
            result_table.insert("", "end", values=(problems[i], user_answers[i], answers[i], times[i]), tags=("correct",))
        else:
            result_table.insert("", "end", values=(problems[i], user_answers[i], answers[i], times[i]), tags=("incorrect",))
        total_time += times[i]

    # Apply tags for color coding
    result_table.tag_configure("correct", background="light green")
    result_table.tag_configure("incorrect", background="light coral")
    result_table.tag_configure("Column1", background="light blue", foreground="black")
    result_table.tag_configure("Column2", background="light yellow", foreground="black")



    # Calculate success rate and average time
    success_rate = (correct_answers / num_questions) * 100
    average_time = total_time / num_questions if num_questions > 0 else 0

    # Add final row for success rate and average time
    result_table.insert("", "end", values=("Success Rate", f"{success_rate:.2f}%", "", f"Avg Time: {average_time:.2f} ms"))

    result_table.pack(pady=20)

    # Save scores to CSV
    save_scores(correct_answers, total_time)

# Function to save scores to a CSV file
def save_scores(correct_answers, total_time):
    # Calculate success rate and average time
    success_rate = (correct_answers / num_questions) * 100
    average_time = total_time / num_questions if num_questions > 0 else 0
    with open("scores.csv", mode="a", newline='') as file:
        writer = csv.writer(file)
        writer.writerow([datetime.now(), f"{success_rate:.2f}%", f"{average_time:.2f} ms"])

# Function to display saved scores
def display_scores():
    scores_window = tk.Toplevel(root)
    scores_window.title("Saved Scores")
    scores_window.geometry("1000x600")  # Larger window to fit the graph
    scores_window.configure(bg="black")

    # Create a Treeview to display saved scores
    columns = ('Date', 'Success Rate', 'Avg Time (ms)')
    scores_table = ttk.Treeview(scores_window, columns=columns, show="headings", style="Custom.Treeview")

    # Set column widths
    scores_table.column('Date', width=150)
    scores_table.column('Success Rate', width=100)
    scores_table.column('Avg Time (ms)', width=100)

    scores_table.heading('Date', text='Date')
    scores_table.heading('Success Rate', text='Success Rate')
    scores_table.heading('Avg Time (ms)', text='Avg Time (ms)')

     # Variables to store data for the graph
    dates = []
    success_rates = []
    avg_times = []

    # Load scores from the CSV file and populate the table
    try:
        with open("scores.csv", mode="r") as file:
            reader = csv.reader(file)
            for row in reader:
                scores_table.insert("", "end", values=row)
                 # Collect data for the graph
                dates.append(row[0])  # Date
                success_rates.append(float(row[1].replace('%', '')))  # Success Rate (convert to float)
                avg_times.append(float(row[2].replace(' ms', '')))  # Avg Time (convert to float)
    except FileNotFoundError:
        pass  # If the file doesn't exist, we do nothing

    scores_table.pack(pady=20)

     # Create a figure and axis for the graph
    fig, ax1 = plt.subplots(figsize=(8, 4))

    # Plot success rate on the primary y-axis
    ax1.set_xlabel('Date')
    ax1.set_ylabel('Success Rate (%)', color='tab:blue')
    ax1.plot(dates, success_rates, color='tab:blue', marker='o', label='Success Rate')
    ax1.tick_params(axis='y', labelcolor='tab:blue')

    # Rotate the date labels on the x-axis
    plt.xticks(rotation=90)

    # Create a secondary y-axis for average response time
    ax2 = ax1.twinx()  # Instantiate a second y-axis sharing the same x-axis
    ax2.set_ylabel('Avg Time (ms)', color='tab:red')
    ax2.plot(dates, avg_times, color='tab:red', marker='x', label='Avg Time')
    ax2.tick_params(axis='y', labelcolor='tab:red')

    # Create a title and layout adjustments
    plt.title("Success Rate and Avg Time per Session")

    # Embed the plot in the Tkinter window
    canvas = FigureCanvasTkAgg(fig, master=scores_window)
    canvas.draw()
    canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)


# Function to adjust the number of questions
def settings():
    settings_window = tk.Toplevel(root)
    settings_window.title("Settings")
    settings_window.configure(bg="black") 


    def save_settings():
        global num_questions
        try:
            num_questions = int(question_entry.get())
            settings_window.destroy()
            # Adjust table height based on the new number of questions
            table.config(height=num_questions)
        except ValueError:
            # If the input is not valid, you could show a message or handle it appropriately
            question_entry.delete(0, tk.END)  # Clear the entry if invalid input

    question_label = tk.Label(settings_window, text="Number of questions:")
    question_label.pack(pady=10)
    question_label.configure(bg="black")
    question_label.configure(fg="white")

    question_entry = tk.Entry(settings_window)
    question_entry.pack(pady=10)
    question_entry.configure(bg="black")
    question_entry.configure(fg="white")
    question_entry.insert(0, str(num_questions))


    save_button = tk.Button(settings_window, text="Save", command=save_settings)
    save_button.pack(pady=10)
    save_button.configure(bg="black")
    save_button.configure(fg="white")

# Set up the main window
root = tk.Tk()
root.title("Mental Math Trainer")
root.geometry("600x400")
root.configure(bg="black") 

# Create a table (Treeview) to display problems
columns = ('Problem', 'Your Answer')
table = ttk.Treeview(root, columns=columns, show="headings", height=num_questions, style="Custom.Treeview")
table.column('Problem', width=100)
table.column('Your Answer', width=100)
table.heading('Problem', text='Problem')
table.heading('Your Answer', text='Your Answer')
table.pack(pady=20)

# Entry widget to input answers
entry = tk.Entry(root, bg="black", fg="white")
entry.bind('<space>', check_answer)  # Bind the spacebar for answer validation
entry.pack(pady=10)

# Settings button to adjust number of questions
settings_button = tk.Button(root, text="Settings", command=settings)
settings_button.pack(side=tk.LEFT, padx=10)
settings_button.configure(bg="black")
settings_button.configure(fg="white")

# Start button to begin the challenge
start_button = tk.Button(root, text="Start", command=start_challenge)
start_button.pack(side=tk.LEFT, padx=10)
start_button.configure(bg="black")
start_button.configure(fg="white")

# Score button to display saved scores
score_button = tk.Button(root, text="Scores", command=display_scores)
score_button.pack(side=tk.LEFT, padx=10)
score_button.configure(bg="black")
score_button.configure(fg="white")

# Run the application
root.mainloop()

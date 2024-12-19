import cohere
from datetime import datetime, timedelta
import tkinter as tk
from tkinter import messagebox, simpledialog
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
from reportlab.lib import colors

# Initialize Cohere client
api_key = "BOI7pYLeLilCROi5BUicZDejy9rk4ArpqsATrXOi"  # Replace with your Cohere API key
co = cohere.Client(api_key)

# Function to analyze goal
def analyze_goal(goal, deadline, available_days):
    response = co.generate(
        model='command-xlarge-nightly',
        prompt=f"Analyze the goal: '{goal}' with a deadline: {deadline}. Suggest if it's achievable in {available_days} days and propose alternatives if unrealistic.",
        max_tokens=100,
        temperature=0.7
    )
    return response.generations[0].text.strip()

# Function to estimate tasks for a goal
def estimate_tasks(goal, available_days):
    response = co.generate(
        model='command-xlarge-nightly',
        prompt=f"Estimate the tasks needed to achieve the goal: '{goal}' in {available_days} days. Provide a detailed task breakdown.",
        max_tokens=200,
        temperature=0.7
    )
    tasks_text = response.generations[0].text.strip()
    tasks = [task.strip() for task in tasks_text.split("\n") if task.strip()]
    return tasks

# Function to generate a schedule with AI-inferred times
def infer_schedule(goal, tasks, feeding_times, sleep_times, pre_committed_hours):
    response = co.generate(
        model='command-xlarge-nightly',
        prompt=(
            f"Create a detailed daily schedule for the goal: '{goal}', considering the tasks: {tasks}, "
            f"feeding times: {feeding_times}, sleep times: {sleep_times}, and pre-committed hours: {pre_committed_hours}. "
            f"Assign exact start and end times for each task, ensuring they align with energy levels and priorities. "
            f"Ensure the entire day from wake-up to bedtime is scheduled, including breaks and relaxation time. "
            f"Use a clear format like '<Time Range>: <Activity Description>' for each task."
        ),
        max_tokens=500,
        temperature=0.7
    )
    schedule_text = response.generations[0].text.strip()
    
    # Parse the response into a list of tasks with times
    schedule = []
    for line in schedule_text.split("\n"):
        if line.strip():
            parts = line.split(":")
            if len(parts) == 2:
                time_range = parts[0].strip()
                activity = parts[1].strip()
                schedule.append([time_range, activity])
    return schedule

# Function to export schedule as PDF
def export_to_pdf(schedule, filename="schedule.pdf"):
    pdf = SimpleDocTemplate(filename, pagesize=letter)
    table_data = [["Task", "Time"]] + schedule
    table = Table(table_data)
    
    # Add style to the table
    style = TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ])
    table.setStyle(style)
    pdf.build([table])
    messagebox.showinfo("Success", f"Schedule saved as {filename}")

# GUI submit_goal function with AI-inferred schedule
def submit_goal():
    goal = goal_entry.get()
    deadline = deadline_entry.get()

    try:
        deadline_date = datetime.strptime(deadline, "%Y-%m-%d")
        available_days = (deadline_date - datetime.now()).days

        if available_days <= 0:
            messagebox.showerror("Error", "The deadline must be a future date.")
            return

        # Analyze goal
        analysis = analyze_goal(goal, deadline, available_days)
        
        # Show analysis
        result_text.config(state=tk.NORMAL)
        result_text.delete(1.0, tk.END)
        result_text.insert(tk.END, f"Goal Analysis:\n{analysis}\n\n")

        # Estimate tasks
        tasks = estimate_tasks(goal, available_days)
        result_text.insert(tk.END, "Estimated Tasks:\n")
        for task in tasks:
            result_text.insert(tk.END, f"{task}\n")

        # Collect feeding, sleep, and pre-committed hours
        feeding_times = simpledialog.askstring("Feeding Times", "Enter feeding times (comma-separated, e.g., 08:00, 13:00, 19:00):")
        sleep_times = simpledialog.askstring("Sleep Times", "Enter sleep times (e.g., 23:00 to 07:00):")
        pre_committed_hours = simpledialog.askstring("Pre-Committed Hours", "Enter pre-committed hours (e.g., 10:00 to 12:00, 15:00 to 16:00):")

        # Infer schedule with AI
        schedule = infer_schedule(goal, tasks, feeding_times, sleep_times, pre_committed_hours)

        # Display schedule
        result_text.insert(tk.END, "Daily Schedule:\n")
        for item in schedule:
            result_text.insert(tk.END, f"{item[0]} - {item[1]}\n")
        
        # Export to PDF
        export_to_pdf(schedule)

    except ValueError:
        messagebox.showerror("Error", "Invalid date format. Please use YYYY-MM-DD.")

# Build GUI
root = tk.Tk()
root.title("Personal AI Scheduler")

# Goal Input
tk.Label(root, text="Enter Your Goal:").pack(pady=5)
goal_entry = tk.Entry(root, width=50)
goal_entry.pack(pady=5)

# Deadline Input
tk.Label(root, text="Enter Deadline (YYYY-MM-DD):").pack(pady=5)
deadline_entry = tk.Entry(root, width=20)
deadline_entry.pack(pady=5)

# Submit Button
submit_button = tk.Button(root, text="Submit", command=submit_goal)
submit_button.pack(pady=10)

# Result Display
tk.Label(root, text="Result:").pack(pady=5)
result_text = tk.Text(root, height=15, width=70, state=tk.DISABLED)
result_text.pack(pady=5)

# Start GUI Event Loop
root.mainloop()

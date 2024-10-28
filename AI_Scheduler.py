import json
import openai
import os
from fpdf import FPDF
from g4f.client import Client

# Save user data to a JSON file
def save_user_data_to_file(user_data, filename='user_data.json'):
    with open(filename, 'w') as f:
        json.dump(user_data, f, indent=4)
    print("User data saved.")

# Load user data from a JSON file
def load_user_data_from_file(filename='user_data.json'):
    try:
        with open(filename, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return None

# Collect time intervals (sleep, meals, pre-committed hours)
def collect_time_intervals():
    intervals = {
        "Sleep Hours": [],
        "Meal Hours": [],
        "Pre-committed Hours": []
    }
    
    def get_time_intervals(interval_name):
        print(f"Enter {interval_name} in 24-hour format (e.g., '22:00-06:00'). Type 'done' to finish: ")
        while True:
            interval = input(f"Enter {interval_name} (format HH:MM-HH:MM): ")
            if interval.lower() == 'done':
                break
            try:
                start, end = interval.split('-')
                intervals[interval_name].append({"start": start, "end": end})
            except ValueError:
                print("Invalid format. Please try again.")
    
    get_time_intervals('Sleep Hours')
    get_time_intervals('Meal Hours')
    get_time_intervals('Pre-committed Hours')

    return intervals


# Collect new goals from the user
def collect_goal_data():
    goals = []
    while True:
        goal_name = input("Enter goal name (or 'done' to finish): ")
        if goal_name == 'done':
            break

        tasks = []
        days_left = int(input(f"Enter number of days left for goal '{goal_name}': "))

        while True:
            task_name = input(f"Enter task for goal '{goal_name}' (or 'done' to finish): ")
            if task_name == 'done':
                break
            tasks.append({"task": task_name})

        goals.append({"goal": goal_name, "tasks": tasks, "days_left": days_left})
    return goals

# Function to update an existing goal's tasks or days left
def edit_existing_goal(goals):
    goal_names = [goal['goal'] for goal in goals]
    print("Existing goals: ", goal_names)
    
    goal_name = input("Enter the name of the goal you'd like to edit: ")
    goal_to_edit = next((goal for goal in goals if goal['goal'] == goal_name), None)
    
    if goal_to_edit:
        choice = input(f"Do you want to edit tasks or days left for goal '{goal_name}'? (tasks/days): ")
        if choice == 'tasks':
            print(f"Current tasks: {goal_to_edit['tasks']}")
            while True:
                task_name = input("Enter the task name you'd like to modify (or 'done' to finish): ")
                if task_name == 'done':
                    break
                existing_task = next((task for task in goal_to_edit['tasks'] if task['task'] == task_name), None)
                if existing_task:
                    print(f"Task '{task_name}' found. No duration to update since it was removed.")
                else:
                    print(f"Task '{task_name}' not found.")
        elif choice == 'days':
            new_days_left = int(input(f"Enter the new number of days left for goal '{goal_name}': "))
            goal_to_edit['days_left'] = new_days_left
            print(f"Days left for '{goal_name}' updated to {new_days_left}.")
    else:
        print(f"Goal '{goal_name}' not found.")

# Function to add new goals to existing goals
def add_new_goals(goals):
    new_goals = collect_goal_data()
    goals.extend(new_goals)
    return goals

# Function to restart with entirely new goals
def restart_with_new_goals():
    print("Restarting with a new set of goals.")
    return collect_goal_data()

# Function to print the schedule in a readable format
def print_schedule(schedule):
    print("\nGenerated Schedule:")
    schedule_entries = []

# Parse and save schedule lines
    for line in schedule:
       if ':' in line:  # Check if line contains `:`
        time_interval, task = line.split(':', 1)  # Split only at the first `:`
        time_interval = time_interval.strip()
        task = task.strip()
        schedule_entries.append({"time_interval": time_interval, "task": task})

# Save schedule to JSON file
    print("Schedule saved to schedule.json")
    output_data = {
    "schedule": schedule
}

    destination_file = 'schedule.json'
    with open(destination_file, 'w') as f:
        json.dump(output_data, f, indent=4)
    print(f"Schedule saved as {destination_file}")

    print(schedule)

    

# Save the schedule as a PDF
def save_schedule_to_pdf(schedule, filename='schedule.pdf'):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)

    margin = 10
    pdf.set_left_margin(margin)
    pdf.set_right_margin(margin)

    usable_width = pdf.w - 2 * margin
    
    pdf.cell(200, 10, txt="Generated Schedule", ln=True, align='C')

    schedule_lines = schedule.split('\n')
    for line in schedule_lines:
       if line.strip():  # Avoid empty lines
         pdf.multi_cell(usable_width, 10, txt=line, border=0, align='L')

    pdf.output(filename)
    print(f"Schedule saved as {filename}")

# Main function to load, modify, and save user data
def manage_goals():
    user_data = load_user_data_from_file() or {}
    
    if 'goals' not in user_data:
        user_data['goals'] = []
    if 'time_intervals' not in user_data:
        user_data['time_intervals'] = {}

    while True:
        print("\nOptions: ")
        print("1. Add new goals")
        print("2. Edit existing goals")
        print("3. Restart with entirely new set of goals")
        print("4. Enter or update sleep, meal, and pre-committed hours")
        print("5. Generate and view updated schedule")
        print("6. Exit")

        choice = input("Choose an option (1-6): ")

        if choice == '1':
            user_data['goals'] = add_new_goals(user_data['goals'])
            save_user_data_to_file(user_data)

        elif choice == '2':
            edit_existing_goal(user_data['goals'])
            save_user_data_to_file(user_data)

        elif choice == '3':
            user_data['goals'] = restart_with_new_goals()
            save_user_data_to_file(user_data)

        elif choice == '4':
            user_data['time_intervals'] = collect_time_intervals()
            save_user_data_to_file(user_data)

        elif choice == '5':
            print("Generating updated schedule...")
            updated_schedule = generate_ai_schedule(user_data)
            print_schedule(updated_schedule)
            save_schedule_to_pdf(updated_schedule)

        elif choice == '6':
            print("Exiting program.")
            break

        else:
            print("Invalid option. Please try again.")

# Function to generate a schedule using OpenAI API
def generate_ai_schedule(user_data):
    goals = user_data['goals']
    time_intervals = user_data['time_intervals']

    # Updated prompt with energy analysis
    prompt = f"""
    I am working towards several goals, each with specific tasks and deadlines. Here are my goals and associated tasks, along with the number of days left to complete each:

    {goals}

    Additionally, I have designated time intervals for my daily routine, including sleep, meals, and other pre-committed hours:

    {time_intervals}

    Please perform the following:
    1. **Analyze my energy levels** based on the provided sleep and meal intervals, considering factors like duration and timing.
    2. **Design a detailed daily schedule** that optimally assigns my tasks to available time slots, taking into account my estimated energy levels throughout the day. 
    3. Ensure that tasks requiring higher concentration and energy are scheduled during peak energy times, while less demanding tasks are allocated to lower energy periods.
    4. **Format the output clearly**, indicating each time interval, the assigned task, and an explanation of how energy levels influenced the scheduling decisions.

    The goal is to create a realistic and effective daily schedule that aligns with my energy patterns and helps me achieve my objectives efficiently.
    """
    client = Client()
    try:
        # New API method
        chat_completion = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}]
        )
        # Extract the content from the response
        response_content = chat_completion.choices[0].message.content
        return response_content
    except Exception as e:
        print(f"Error generating schedule: {e}")
        return None

# Run the program
if __name__ == "__main__":
    manage_goals()
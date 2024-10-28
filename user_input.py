import json
import openai
import os


# Save user data to a JSON file
def save_user_data_to_file(user_data, filename='user_data.json'):
    with open(filename, 'w') as f:
        json.dump(user_data, f, indent=4)
    print("User data saved.")


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

# Main function to load, modify, and save user data
def manage_goals():
    source_file = 'user_data.json'
    with open(source_file, 'r') as file:
      user_data = json.load(file)or {}
    
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
        print("5. Exit")

        choice = input("Choose an option (1-5): ")

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
            print("Exiting program.")
            break

        else:
            print("Invalid option. Please try again.")

# Run the program
if __name__ == "__main__":
    manage_goals()
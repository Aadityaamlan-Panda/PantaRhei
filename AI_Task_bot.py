import json
import os
from fpdf import FPDF
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox, QTextEdit, QInputDialog, QFileDialog
from PyQt5.QtCore import Qt
from g4f.client import Client

# Save user data to a JSON file
def save_user_data_to_file(user_data, filename='user_data.json'):
    with open(filename, 'w') as f:
        json.dump(user_data, f, indent=4)

# Load user data from a JSON file
def load_user_data_from_file(filename='user_data.json'):
    try:
        with open(filename, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return None

class GoalManagerApp(QWidget):
    def __init__(self):
        super().__init__()
        self.user_data = load_user_data_from_file() or {'goals': [], 'time_intervals': {}}
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Goal Manager')
        layout = QVBoxLayout()

        # Menu label
        self.menu_label = QLabel("Choose an option:\n1. Add new goals\n2. Edit existing goals\n3. Restart with new goals\n4. Enter/Update time intervals\n5. Generate schedule\n6. Exit")
        layout.addWidget(self.menu_label)

        # Input for option choice
        self.option_input = QLineEdit(self)
        self.option_input.setPlaceholderText("Enter option (1-6)")
        layout.addWidget(self.option_input)

        # Submit button
        self.submit_button = QPushButton("Submit", self)
        self.submit_button.clicked.connect(self.handle_option)
        layout.addWidget(self.submit_button)

        # Display output
        self.output_display = QTextEdit(self)
        self.output_display.setReadOnly(True)
        layout.addWidget(self.output_display)

        self.setLayout(layout)

    def handle_option(self):
        choice = self.option_input.text()
        if choice == '1':
            self.add_new_goals()
        elif choice == '2':
            self.edit_existing_goal()
        elif choice == '3':
            self.restart_with_new_goals()
        elif choice == '4':
            self.collect_time_intervals()
        elif choice == '5':
            self.generate_schedule()
        elif choice == '6':
            QApplication.instance().quit()
        else:
            self.show_message("Invalid option. Please enter a number between 1 and 6.")

    def add_new_goals(self):
        goals = []
        while True:
            goal_name, ok = QInputDialog.getText(self, 'Add Goal', 'Enter goal name:')
            if not ok or not goal_name:
                break

            days_left, ok = QInputDialog.getInt(self, 'Days Left', f"Enter days left for '{goal_name}':")
            if not ok:
                break

            tasks = []
            while True:
                task_name, ok = QInputDialog.getText(self, 'Task', f"Enter task for '{goal_name}' (or leave blank to finish):")
                if not ok or not task_name:
                    break
                tasks.append({"task": task_name})

            goals.append({"goal": goal_name, "tasks": tasks, "days_left": days_left})
        self.user_data['goals'].extend(goals)
        save_user_data_to_file(self.user_data)
        self.show_message("Goals added successfully.")

    def edit_existing_goal(self):
        goal_names = [goal['goal'] for goal in self.user_data['goals']]
        goal_name, ok = QInputDialog.getItem(self, 'Edit Goal', 'Select goal to edit:', goal_names, editable=False)
        if ok:
            goal_to_edit = next((goal for goal in self.user_data['goals'] if goal['goal'] == goal_name), None)
            if goal_to_edit:
                option, ok = QInputDialog.getItem(self, 'Edit Option', 'Edit tasks or days?', ['tasks', 'days'], editable=False)
                if option == 'tasks':
                    self.edit_tasks(goal_to_edit)
                elif option == 'days':
                    new_days_left, ok = QInputDialog.getInt(self, 'Days Left', f"Enter new days for '{goal_name}':")
                    if ok:
                        goal_to_edit['days_left'] = new_days_left
                        save_user_data_to_file(self.user_data)
                        self.show_message("Days left updated successfully.")
            else:
                self.show_message(f"Goal '{goal_name}' not found.")

    def edit_tasks(self, goal_to_edit):
        task_names = [task['task'] for task in goal_to_edit['tasks']]
        task_name, ok = QInputDialog.getItem(self, 'Edit Task', 'Select task to edit:', task_names, editable=False)
        if ok and task_name in task_names:
            task_index = task_names.index(task_name)
            new_task_name, ok = QInputDialog.getText(self, 'Edit Task', 'Enter new task name:')
            if ok:
                goal_to_edit['tasks'][task_index]['task'] = new_task_name
                save_user_data_to_file(self.user_data)
                self.show_message("Task updated successfully.")

    def restart_with_new_goals(self):
        self.user_data['goals'] = []
        save_user_data_to_file(self.user_data)
        self.show_message("Restarted with new goals.")

    def collect_time_intervals(self):
        intervals = {"Sleep Hours": [], "Meal Hours": [], "Pre-committed Hours": []}

        def get_intervals(interval_name):
            while True:
                interval, ok = QInputDialog.getText(self, interval_name, f"Enter {interval_name} in HH:MM-HH:MM format or leave blank to finish:")
                if not ok or not interval:
                    break
                start, end = interval.split('-')
                intervals[interval_name].append({"start": start, "end": end})

        for name in intervals.keys():
            get_intervals(name)

        self.user_data['time_intervals'] = intervals
        save_user_data_to_file(self.user_data)
        self.show_message("Time intervals updated.")

    def generate_schedule(self):
        client = Client()
        try:
            goals = self.user_data['goals']
            time_intervals = self.user_data['time_intervals']
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
            chat_completion = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}]
            )
            schedule = chat_completion.choices[0].message.content
            self.output_display.setText(schedule)
            save_schedule_to_pdf(schedule)
            self.show_message("Schedule generated and saved.")
        except Exception as e:
            self.show_message(f"Error generating schedule: {e}")

    def show_message(self, message):
        QMessageBox.information(self, 'Info', message)

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
        if line.strip():
            pdf.multi_cell(usable_width, 10, txt=line, border=0, align='L')
    pdf.output(filename)

if __name__ == "__main__":
    app = QApplication([])
    window = GoalManagerApp()
    window.show()
    app.exec_()

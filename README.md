# Goal Manager App

The Goal Manager App is a desktop application designed to help users set, manage, and track goals with specific tasks and deadlines. It enables users to add new goals, edit existing ones, specify daily time intervals (sleep, meals, and other commitments), and generate an optimized daily schedule based on available time and estimated energy levels. The schedule is generated using an AI model and saved as a PDF for easy reference.

## Features

- **Goal Management**: Add, edit, or reset goals with deadlines and associated tasks.
- **Time Intervals Setup**: Define daily routines, such as sleep, meal, and other pre-committed hours.
- **AI-Powered Schedule Generation**: Creates a detailed daily schedule that maximizes productivity by aligning tasks with estimated energy levels.
- **PDF Export**: Generates a PDF version of the schedule for offline access.

## Requirements

- Python 3.7+
- Required packages:
  - `PyQt5`
  - `FPDF`
  - `g4f` (for GPT model integration)
  
- Install these packages using:
bash
pip install PyQt5 fpdf g4f
Usage
Run the application:

bash
Copy code
AI_Task_bot.py
Menu Options:

1. Add new goals: Add goals with deadlines and individual tasks.
2. Edit existing goals: Modify goal tasks or adjust deadlines.
3. Restart with new goals: Clear all current goals and start fresh.
4. Enter/Update time intervals: Specify daily time intervals for sleep, meals, and other commitments.
5. Generate schedule: Generate an optimized schedule based on goals and time intervals. The generated schedule is also saved as a PDF.
6. Exit: Exit the application.
Output Schedule: The schedule is displayed in the app and saved as schedule.pdf in the project directory.

## File Structure
goal_manager_app.py: Main application file.
user_data.json: JSON file to save user goals and time intervals.
schedule.pdf: PDF file containing the generated schedule.

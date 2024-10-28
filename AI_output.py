from g4f.client import Client
import json
from fpdf import FPDF

# Define the file paths
source_file = 'user_data.json'

# Step 1: Read data from the source JSON file
with open(source_file, 'r') as file:
    user_data = json.load(file)

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
response = client.chat.completions.create(
    model="gpt-3.5-turbo",
    messages=[{"role": "user", "content": prompt}],
    # Add any other necessary parameters
)

response_content = response.choices[0].message.content

output_data = {
    "schedule": response_content
}

destination_file = 'schedule.json'
with open(destination_file, 'w') as f:
    json.dump(output_data, f, indent=4)
print(f"Schedule saved as {destination_file}")

print(response_content)

filename='Generated_schedule.pdf'
pdf = FPDF()
pdf.add_page()
pdf.set_font("Arial", size=12)
pdf.cell(200, 10, txt="Generated Schedule", ln=True, align='C')

schedule_lines = response_content.split('\n')
for line in schedule_lines:
    if line.strip():  # Avoid empty lines
        pdf.cell(200, 10, txt=line, ln=True)

pdf.output(filename)
print(f"Schedule saved as {filename}")

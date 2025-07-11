import tkinter as tk
from tkinter import messagebox, simpledialog
from tkcalendar import Calendar
import datetime
import json
import re # Import regex for time validation
from plyer import notification # Add this line for native notifications

# --- Configuration for saving ---
SAVE_FILE_NAME = 'tasks_data.json' # The name of the file where tasks will be saved

class TodoCalendarApp:
    def __init__(self, master):
        self.master = master
        master.title("Calendar To-Do App (File Saved, Edit & Reminders)")
        master.geometry("750x650") # Slightly increased size for new elements
        master.resizable(False, False)

        self.selected_date = datetime.date.today()
        self.tasks = self.load_tasks()
        self.editing_task_index = None # To store the index of the task being edited
        self.reminded_tasks = set() # To keep track of tasks for which reminders have been shown

        self.create_widgets()
        self.update_task_list()

        # Bind the window closing event to our saving function
        self.master.protocol("WM_DELETE_WINDOW", self.on_closing)

        # Start the reminder checking loop
        self.check_reminders()

    def create_widgets(self):
        # --- Left Frame: Calendar ---
        calendar_frame = tk.Frame(self.master, padx=10, pady=10, bd=2, relief="groove")
        calendar_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=False)

        tk.Label(calendar_frame, text="Select a Date:", font=('Arial', 14, 'bold')).pack(pady=5)

        self.cal = Calendar(
            calendar_frame,
            selectmode='day',
            date_pattern='yyyy-mm-dd',
            font='Arial 12',
            background='lightgray',
            foreground='black',
            normalbackground='white',
            bordercolor='gray',
            headersbackground='lightblue',
            headersforeground='black',
            selectbackground='blue',
            selectforeground='white',
            tooltipbackground='yellow'
        )
        self.cal.pack(pady=10)
        self.cal.bind("<<CalendarSelected>>", self.on_date_selected)

        # --- Right Frame: Task Management ---
        task_frame = tk.Frame(self.master, padx=10, pady=10, bd=2, relief="groove")
        task_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        self.date_display_label = tk.Label(task_frame, text=f"Tasks for: {self.selected_date.strftime('%Y-%m-%d')}", font=('Arial', 14, 'bold'))
        self.date_display_label.pack(pady=5)

        # Task Entry
        tk.Label(task_frame, text="Task Description:", font=('Arial', 12)).pack(anchor='w', pady=(10, 0))
        self.task_entry = tk.Entry(task_frame, width=40, font=('Arial', 12))
        self.task_entry.pack(fill='x', pady=5)
        self.task_entry.bind("<Return>", lambda event: self.save_or_update_task())

        # Time Entry
        tk.Label(task_frame, text="Time (HH:MM, optional):", font=('Arial', 12)).pack(anchor='w', pady=(5, 0))
        self.time_entry = tk.Entry(task_frame, width=10, font=('Arial', 12))
        self.time_entry.pack(anchor='w', pady=5)
        self.time_entry.insert(0, "00:00") # Default time
        self.time_entry.bind("<FocusIn>", self.clear_default_time)
        self.time_entry.bind("<FocusOut>", self.set_default_time_if_empty)

        # Add/Update Task Button
        self.add_update_button = tk.Button(task_frame, text="Add Task for Selected Date", command=self.save_or_update_task, font=('Arial', 12), bg='#4CAF50', fg='white')
        self.add_update_button.pack(fill='x', pady=5)

        tk.Label(task_frame, text="Tasks:", font=('Arial', 12)).pack(anchor='w', pady=(10, 0))
        self.task_listbox = tk.Listbox(task_frame, height=15, font=('Arial', 12), selectmode=tk.SINGLE, bd=2, relief="sunken")
        self.task_listbox.pack(fill=tk.BOTH, expand=True, pady=5)

        scrollbar = tk.Scrollbar(self.task_listbox, orient="vertical", command=self.task_listbox.yview)
        self.task_listbox.config(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")

        button_row_frame = tk.Frame(task_frame)
        button_row_frame.pack(fill='x', pady=5)

        mark_complete_button = tk.Button(button_row_frame, text="Mark Complete", command=self.mark_selected_task_complete, font=('Arial', 10), bg='#2196F3', fg='white')
        mark_complete_button.pack(side=tk.LEFT, expand=True, padx=2)

        edit_button = tk.Button(button_row_frame, text="Edit Task", command=self.edit_selected_task, font=('Arial', 10), bg='#FFC107', fg='black')
        edit_button.pack(side=tk.LEFT, expand=True, padx=2)

        delete_button = tk.Button(button_row_frame, text="Delete Task", command=self.delete_selected_task, font=('Arial', 10), bg='#F44336', fg='white')
        delete_button.pack(side=tk.RIGHT, expand=True, padx=2)

    # New methods for time entry behavior
    def clear_default_time(self, event):
        """Clears the default '00:00' when the time entry gets focus."""
        if self.time_entry.get() == "00:00":
            self.time_entry.delete(0, tk.END)

    def set_default_time_if_empty(self, event):
        """Sets '00:00' if the time entry is empty when it loses focus."""
        if not self.time_entry.get().strip():
            self.time_entry.insert(0, "00:00")

    def on_date_selected(self, event):
        """Handles date selection from the calendar."""
        selected_date_str = self.cal.get_date()
        self.selected_date = datetime.datetime.strptime(selected_date_str, '%Y-%m-%d').date()
        self.date_display_label.config(text=f"Tasks for: {self.selected_date.strftime('%Y-%m-%d')}")
        self.update_task_list()
        self.reset_task_entry_and_button()

    # Method for time validation
    def validate_time_format(self, time_str):
        """Validates if the time string is in HH:MM format."""
        return re.fullmatch(r'^(?:2[0-3]|[01]?[0-9]):[0-5][0-9]$', time_str)

    # Handles both add and update
    def save_or_update_task(self):
        """Adds a new task or updates an existing one based on editing_task_index."""
        task_text = self.task_entry.get().strip()
        time_text = self.time_entry.get().strip()
        task_time = None

        if time_text and time_text != "00:00":
            if self.validate_time_format(time_text):
                task_time = time_text
            else:
                messagebox.showwarning("Input Error", "Please enter time in HH:MM format (e.g., 09:30).")
                return

        if not task_text:
            messagebox.showwarning("Input Error", "Please enter a task description.")
            return

        date_key = self.selected_date.strftime('%Y-%m-%d')
        if date_key not in self.tasks:
            self.tasks[date_key] = []

        if self.editing_task_index is not None:
            # Update existing task
            current_tasks = self.tasks.get(date_key, [])
            if 0 <= self.editing_task_index < len(current_tasks):
                current_tasks[self.editing_task_index]['text'] = task_text
                current_tasks[self.editing_task_index]['time'] = task_time
                messagebox.showinfo("Task Updated", "Task has been updated successfully.")
            else:
                messagebox.showerror("Error", "Could not find task to update.")
        else:
            # Add new task
            self.tasks[date_key].append({'text': task_text, 'completed': False, 'time': task_time})
            messagebox.showinfo("Task Added", "New task added successfully.")

        self.reset_task_entry_and_button()
        self.update_task_list()
        self.save_tasks() # Save after any modification

    # Edit Task function
    def edit_selected_task(self):
        """Puts the selected task into editing mode."""
        selected_indices = self.task_listbox.curselection()
        if not selected_indices:
            messagebox.showwarning("Selection Error", "Please select a task to edit.")
            return

        selected_index = selected_indices[0]
        date_key = self.selected_date.strftime('%Y-%m-%d')
        tasks_on_date = self.tasks.get(date_key, [])

        if 0 <= selected_index < len(tasks_on_date):
            task_item = tasks_on_date[selected_index]
            self.task_entry.delete(0, tk.END)
            self.task_entry.insert(0, task_item['text'])
            self.time_entry.delete(0, tk.END)
            # Handle None or empty string for time when loading
            self.time_entry.insert(0, task_item.get('time', '00:00') or '00:00')

            self.editing_task_index = selected_index
            self.add_update_button.config(text="Update Task")
        else:
            messagebox.showerror("Error", "Task not found for editing.")

    # Reset entry and button
    def reset_task_entry_and_button(self):
        """Resets the task entry field and button text after adding/updating/changing date."""
        self.task_entry.delete(0, tk.END)
        self.time_entry.delete(0, tk.END)
        self.time_entry.insert(0, "00:00")
        self.editing_task_index = None
        self.add_update_button.config(text="Add Task for Selected Date")

    # Updates the listbox display
    def update_task_list(self):
        """Updates the listbox with tasks for the selected date."""
        self.task_listbox.delete(0, tk.END)
        date_key = self.selected_date.strftime('%Y-%m-%d')
        tasks_for_selected_date = self.tasks.get(date_key, [])

        for i, task_item in enumerate(tasks_for_selected_date):
            status = '[X]' if task_item['completed'] else '[ ]'
            time_str = f" ({task_item['time']})" if task_item.get('time') else "" # Include time if present
            display_text = f"{status} {task_item['text']}{time_str}"
            self.task_listbox.insert(tk.END, display_text)
            if task_item['completed']:
                self.task_listbox.itemconfig(tk.END, {'fg': 'gray'})

    def get_selected_task_index(self):
        """Helper to get the index of the selected task."""
        try:
            return self.task_listbox.curselection()[0]
        except IndexError:
            messagebox.showwarning("Selection Error", "Please select a task from the list.")
            return None

    def mark_selected_task_complete(self):
        """Toggles the completion status of the selected task."""
        selected_index = self.get_selected_task_index()
        if selected_index is not None:
            date_key = self.selected_date.strftime('%Y-%m-%d')
            tasks_on_date = self.tasks.get(date_key)

            if tasks_on_date and 0 <= selected_index < len(tasks_on_date):
                tasks_on_date[selected_index]['completed'] = not tasks_on_date[selected_index]['completed']
                self.update_task_list()
                self.save_tasks() # Save after any modification
            else:
                messagebox.showerror("Error", "Task not found for toggling completion.")

    def delete_selected_task(self):
        """Deletes the selected task."""
        selected_index = self.get_selected_task_index()
        if selected_index is not None:
            date_key = self.selected_date.strftime('%Y-%m-%d')
            tasks_on_date = self.tasks.get(date_key)

            if tasks_on_date and 0 <= selected_index < len(tasks_on_date):
                if messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this task?"):
                    # Remove the task from the set of reminded tasks if it was there
                    task_id = (date_key, tasks_on_date[selected_index]['text'], tasks_on_date[selected_index].get('time'))
                    self.reminded_tasks.discard(task_id)

                    del tasks_on_date[selected_index]
                    if not tasks_on_date: # If the last task for a day is deleted, remove the date key
                        del self.tasks[date_key]
                    self.update_task_list()
                    self.save_tasks() # Save after any modification
                    self.reset_task_entry_and_button() # Reset editing state after deletion
            else:
                messagebox.showerror("Error", "Task not found for deletion.")

    # --- Persistence Methods ---
    def load_tasks(self):
        """Loads tasks from the JSON file."""
        try:
            with open(SAVE_FILE_NAME, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return {}
        except json.JSONDecodeError:
            messagebox.showwarning("Data Error", "Could not read tasks file. Starting fresh.")
            return {}
        except Exception as e:
            messagebox.showerror("Error", f"An unexpected error occurred while loading tasks: {e}")
            return {}

    def save_tasks(self):
        """Saves current tasks to the JSON file."""
        try:
            with open(SAVE_FILE_NAME, 'w') as f:
                json.dump(self.tasks, f, indent=4)
        except Exception as e:
            messagebox.showerror("Save Error", f"Could not save tasks: {e}")

    def on_closing(self):
        """Called when the window is closed. Saves tasks before quitting."""
        self.save_tasks()
        self.master.destroy()

    # Reminder System (now using plyer for native notifications)
    def check_reminders(self):
        """Checks for upcoming tasks and shows native desktop reminders."""
        now = datetime.datetime.now()
        current_date_str = now.strftime('%Y-%m-%d')

        tasks_today = self.tasks.get(current_date_str, [])

        for task_item in tasks_today:
            task_time = task_item.get('time')
            task_text = task_item['text']
            task_completed = task_item['completed']

            if task_time and not task_completed:
                # Create a unique identifier for the task to prevent repeated reminders
                task_id = (current_date_str, task_text, task_time)

                try:
                    # Parse task time and create a datetime object for comparison
                    task_dt = datetime.datetime.strptime(f"{current_date_str} {task_time}", '%Y-%m-%d %H:%M')

                    # Check if the task is due within a specific window (e.g., 1 minute before or after) or overdue but not yet reminded
                    if (task_dt - datetime.timedelta(minutes=1) <= now <= task_dt + datetime.timedelta(minutes=1)) and task_id not in self.reminded_tasks:
                        notification.notify(
                            title="Task Reminder",
                            message=f"'{task_text}' is due now!",
                            app_name="Calendar To-Do",
                            timeout=10 # Notification stays for 10 seconds
                        )
                        self.reminded_tasks.add(task_id) # Mark as reminded
                    elif now > task_dt and task_id not in self.reminded_tasks:
                        # If it's past the time and hasn't been reminded, show a late reminder
                        notification.notify(
                            title="Overdue Task",
                            message=f"'{task_text}' was due at {task_time}!",
                            app_name="Calendar To-Do",
                            timeout=15 # Notification stays for 15 seconds
                        )
                        self.reminded_tasks.add(task_id) # Mark as reminded
                except ValueError:
                    print(f"Warning: Invalid time format for task '{task_text}': {task_time}")
                    pass

        # Schedule the next check in 60 seconds (1 minute)
        self.master.after(60000, self.check_reminders)

# --- Main Application Execution ---
if __name__ == "__main__":
    root = tk.Tk()
    app = TodoCalendarApp(root)
    root.mainloop()
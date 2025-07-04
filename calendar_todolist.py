# todo_calendar_app.py (JSON File Persistence Version)
import tkinter as tk
from tkinter import messagebox
from tkcalendar import Calendar
import datetime
import json # Import the JSON module

# --- Configuration for saving ---
SAVE_FILE_NAME = 'tasks_data.json' # The name of the file where tasks will be saved

class TodoCalendarApp:
    def __init__(self, master):
        self.master = master
        master.title("Calendar To-Do App (File Saved)")
        master.geometry("700x600")
        master.resizable(False, False)

        self.selected_date = datetime.date.today()
        # Load tasks from file when the app starts
        self.tasks = self.load_tasks()

        self.create_widgets()
        self.update_task_list()

        # Bind the window closing event to our saving function
        self.master.protocol("WM_DELETE_WINDOW", self.on_closing)

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

        tk.Label(task_frame, text="New Task:", font=('Arial', 12)).pack(anchor='w', pady=(10, 0))
        self.task_entry = tk.Entry(task_frame, width=40, font=('Arial', 12))
        self.task_entry.pack(fill='x', pady=5)
        self.task_entry.bind("<Return>", lambda event: self.add_new_task())

        add_button = tk.Button(task_frame, text="Add Task for Selected Date", command=self.add_new_task, font=('Arial', 12), bg='#4CAF50', fg='white')
        add_button.pack(fill='x', pady=5)

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

        delete_button = tk.Button(button_row_frame, text="Delete Task", command=self.delete_selected_task, font=('Arial', 10), bg='#F44336', fg='white')
        delete_button.pack(side=tk.RIGHT, expand=True, padx=2)

    def on_date_selected(self, event):
        selected_date_str = self.cal.get_date()
        self.selected_date = datetime.datetime.strptime(selected_date_str, '%Y-%m-%d').date()
        self.date_display_label.config(text=f"Tasks for: {self.selected_date.strftime('%Y-%m-%d')}")
        self.update_task_list()

    def add_new_task(self):
        task_text = self.task_entry.get().strip()
        if task_text:
            date_key = self.selected_date.strftime('%Y-%m-%d')
            if date_key not in self.tasks:
                self.tasks[date_key] = []
            self.tasks[date_key].append({'text': task_text, 'completed': False})
            self.task_entry.delete(0, tk.END)
            self.update_task_list()
            # self.save_tasks() # Option 1: Save immediately after modification
        else:
            messagebox.showwarning("Input Error", "Please enter a task description.")

    def update_task_list(self):
        self.task_listbox.delete(0, tk.END)
        date_key = self.selected_date.strftime('%Y-%m-%d')
        tasks_for_selected_date = self.tasks.get(date_key, [])

        for i, task_item in enumerate(tasks_for_selected_date):
            display_text = f"{'[X]' if task_item['completed'] else '[ ]'} {task_item['text']}"
            self.task_listbox.insert(tk.END, display_text)
            if task_item['completed']:
                self.task_listbox.itemconfig(tk.END, {'fg': 'gray'})

    def get_selected_task_index(self):
        try:
            return self.task_listbox.curselection()[0]
        except IndexError:
            messagebox.showwarning("Selection Error", "Please select a task from the list.")
            return None

    def mark_selected_task_complete(self):
        selected_index = self.get_selected_task_index()
        if selected_index is not None:
            date_key = self.selected_date.strftime('%Y-%m-%d')
            tasks_on_date = self.tasks.get(date_key)

            if tasks_on_date and 0 <= selected_index < len(tasks_on_date):
                tasks_on_date[selected_index]['completed'] = not tasks_on_date[selected_index]['completed']
                self.update_task_list()
                # self.save_tasks() # Option 1: Save immediately after modification
            else:
                messagebox.showerror("Error", "Task not found for toggling completion.")

    def delete_selected_task(self):
        selected_index = self.get_selected_task_index()
        if selected_index is not None:
            date_key = self.selected_date.strftime('%Y-%m-%d')
            tasks_on_date = self.tasks.get(date_key)

            if tasks_on_date and 0 <= selected_index < len(tasks_on_date):
                if messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this task?"):
                    del tasks_on_date[selected_index]
                    if not tasks_on_date: # If the last task for a day is deleted, remove the date key
                        del self.tasks[date_key]
                    self.update_task_list()
                    # self.save_tasks() # Option 1: Save immediately after modification
            else:
                messagebox.showerror("Error", "Task not found for deletion.")

    # --- New Persistence Methods ---
    def load_tasks(self):
        """Loads tasks from the JSON file."""
        try:
            with open(SAVE_FILE_NAME, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            # If the file doesn't exist yet, return an empty dictionary
            return {}
        except json.JSONDecodeError:
            # Handle cases where the file might be empty or corrupted
            messagebox.showwarning("Data Error", "Could not read tasks file. Starting fresh.")
            return {}
        except Exception as e:
            messagebox.showerror("Error", f"An unexpected error occurred while loading tasks: {e}")
            return {}

    def save_tasks(self):
        """Saves current tasks to the JSON file."""
        try:
            with open(SAVE_FILE_NAME, 'w') as f:
                json.dump(self.tasks, f, indent=4) # indent for pretty printing the JSON
        except Exception as e:
            messagebox.showerror("Save Error", f"Could not save tasks: {e}")

    def on_closing(self):
        """Called when the window is closed. Saves tasks before quitting."""
        self.save_tasks()
        self.master.destroy() # Destroy the window and quit the application


# --- Main Application Execution ---
if __name__ == "__main__":
    root = tk.Tk()
    app = TodoCalendarApp(root)
    root.mainloop()
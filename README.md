# Calendar To-Do App

A simple desktop Calendar and To-Do List application built with Python and Tkinter. This application allows users to manage tasks associated with specific dates, set reminders with specific times, and receive native desktop notifications for upcoming or overdue tasks while the app is running.

## Features

* **Date Selection:** Easily select any date from the calendar to view or manage tasks.
* **Task Management:**
    * Add new tasks with a description and an optional specific time (HH:MM).
    * Edit existing tasks to update their description or time.
    * Mark tasks as complete or incomplete.
    * Delete tasks from a selected date.
* **Task Persistence:** All tasks are automatically saved to `tasks_data.json` and loaded when the application starts, so your data is never lost.
* **Time-Based Reminders:** Set specific times for your tasks, and the app will track them.
* **Native Desktop Notifications:** Receive pop-up reminders directly on your desktop for tasks that are due or overdue (notifications appear when the app is open and running).
* **User-Friendly Interface:** Clean and intuitive graphical user interface.

## How to Run the Source Code

This section is for users who want to run the application directly from its Python source code.

### Prerequisites

Make sure you have Python installed on your system (Python 3.x is recommended). Tkinter, the GUI library, typically comes pre-installed with standard Python distributions.

### Installation

1.  **Clone or download** the project files to your local machine.
2.  **Navigate** to the project directory in your terminal or command prompt.
    ```bash
    cd your_project_directory
    ```
3.  **Install the required Python libraries** using pip:
    ```bash
    pip install tkcalendar plyer
    ```

### Running the Python Script

After installing the prerequisites, you can run the application by executing the main Python script:

```bash
python todo_calendar_app.py
```
## Running the Application (.exe)

This section is specifically for running the compiled `.exe` file without needing to install Python or any libraries.

### Installation

1.  **Download the provided `.zip` file** containing the application from the GitHub repository:
    * First, click on the folder named `calendar todolist application file`.
    * Then, click on the `calendar_todolist.zip` file.
    * Finally, click on the "View raw" button (it might be on the right side of the page) to start the download.
2.  **Unzip the file** to a location on your computer (e.g., your Desktop or Documents folder).
    * **On Windows:** Right-click the downloaded `.zip` file, select "Extract All...", and follow the prompts.
    * **On macOS:** Simply double-click the downloaded `.zip` file, and it will automatically unzip.

### Usage

1. Navigate to the unzipped folder.
2. Double-click `todo_calendar_app.exe` to launch the application.
3. The application will start with a fresh task list. Any tasks you add will be saved in `tasks_data.json` in the same folder.

---

## Usage (for Both Versions)

- **Select a Date**  
  Use the calendar on the left to pick a date.

- **Add a Task**
  1. Enter the task description in the "Task Description" field.
  2. (Optional) Enter a specific time in `"HH:MM"` format (e.g., `09:30`) in the "Time" field.
  3. Click **"Add Task for Selected Date"**.

- **Edit a Task**
  1. Select an existing task from the list.
  2. Click the **"Edit Task"** button. The task's details will appear in the input fields.
  3. Modify the description or time as needed.
  4. Click **"Update Task"** (the button text will change) to save your changes.

- **Mark Complete/Incomplete**  
  Select a task and click **"Mark Complete"**.

- **Delete a Task**  
  Select a task and click **"Delete Task"**.

- **Reminders**  
  If you set a time for a task, you will receive a desktop notification when that time arrives (as long as the app is open and running).


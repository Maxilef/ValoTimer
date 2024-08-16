# ValoTimer

ValoTimer is a training tool designed to help you improve your performance in the Valorant shooting range. The application allows you to time your performance during different types of training sessions and provides a graphical representation of your progress over time. Additionally, you can record your training sessions to analyze your performance.

## Features

- **Timer**: Accurately time your training sessions.
- **Results Tracking**: The last 10 results are displayed, along with your best score.
- **Graphical Analysis**: View a graph of your performance over time.
- **Recording**: Record your training sessions for later analysis.

## Installation and Build Instructions

### Prerequisites

Ensure you have the following installed on your system:

- Python 3.x
- Required Python packages: `tkinter`, `pynput`, `subprocess`, `pygetwindow`, `datetime`, `matplotlib`, `pandas`

### Building the Application

To build the application into a standalone executable, follow these steps:

1. Open a terminal or command prompt.
2. Navigate to the directory containing your `main.py` script.
3. Run the following command to create the executable:

    ```bash
    pyinstaller --onefile --add-data "C:\\Users\\maxim\\IdeaProjects\\ValoTimer\\icon.ico;." --hidden-import pandas --additional-hooks-dir=hooks main.py
    ```

This command will generate a single executable file that you can distribute and run on other systems.

### Executing the Application

After building the application, you can run the executable by navigating to the `dist` directory and executing the following command:

```bash
dist/main.exe

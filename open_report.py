from flask import Flask, send_from_directory
import webbrowser
import os
import threading
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()
BASE_DIR = '/app/project'
app = Flask(__name__)

# Get PROJECT_PATH from environment variables
project_path = os.getenv('PROJECT_PATH')

# Define paths for report generation
report_directory = os.path.join(project_path, 'Report')
os.makedirs(report_directory, exist_ok=True)  # Create Report directory if it doesn't exist
report_path = os.path.join(report_directory, 'emissions_report.html')
print(f"Report path: {report_path}")
@app.route('/report.html')
def serve_report():
    return send_from_directory(report_directory, 'emissions_report.html')

def open_report():
    # Construct the file URL for the report on the host
    host_report_path = "file:///" + os.path.abspath(report_path).replace("\\", "/")
    webbrowser.open_new_tab(host_report_path)

if __name__ == '__main__':
    # Start a thread to open the report after starting the server
    threading.Thread(target=open_report).start()
    app.run(host='0.0.0.0', port=5001)
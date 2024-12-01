from flask import Flask, render_template, request, redirect, url_for, Response, stream_with_context, send_from_directory, jsonify, send_file, abort
from dotenv import set_key, load_dotenv
from flask_socketio import SocketIO, emit
import os
import subprocess
import threading
import time
import re
from flask import render_template


app = Flask(__name__)
socketio = SocketIO(app)
process_running = False
lock = threading.Lock()

BASE_DIR = '/app/project'
# Load environment variables
env_path = '/app/.env'
load_dotenv(dotenv_path=env_path, verbose=True, override=True)

# Helper function to format paths for Windows
def format_path(path):
    return path.replace("/", "\\").replace("\\", "\\")

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/save', methods=['POST'])
def save_config():
    try:
        azure_model = request.form.get('azure_model', 'GPT4o')  # Default value if not provided
        project_path = request.form.get('project_path').strip()  # Strip extra spaces or hidden characters

        # Save to .env
        set_key(env_path, "AZURE_MODEL", azure_model)
        
        # Save the project path with set_key
        set_key(env_path, "PROJECT_PATH", project_path)
        print("PROJECT_PATH saved to .env:", project_path)
        # After saving, we manually remove quotes from the PROJECT_PATH in the .env file
        with open(env_path, 'r') as f:
            lines = f.readlines()
        
        # Remove quotes from PROJECT_PATH
        with open(env_path, 'w') as f:
            for line in lines:
                if line.startswith("PROJECT_PATH"):
                    # Strip any single quotes around the path
                    line = line.replace("'", "")
                f.write(line)         
        # Prompts configuration
        prompts = {
            "PROMPT_1": request.form.get('prompt_1', 'n'),
            "PROMPT_2": request.form.get('prompt_2', 'n'),
            "PROMPT_3": request.form.get('prompt_3', 'n'),
            "PROMPT_4": request.form.get('prompt_4', 'n'),
            "PROMPT_5": request.form.get('prompt_5', 'n'),
            "PROMPT_6": request.form.get('prompt_6', 'n'),
            "PROMPT_7": request.form.get('prompt_7', 'n'),
            "PROMPT_GENERATE_TESTCASES": request.form.get('prompt_generate_testcases', 'n')
        }
        
        # Save prompt configurations
        for prompt, value in prompts.items():
            env_value = os.getenv(prompt, "")
            prompt_text = env_value.split(",")[0] if env_value else "Default Text"
            set_key(env_path, prompt, f"{prompt_text}, {value}")

        return redirect(url_for('index'))
    
    except Exception as e:
        # Log the error for debugging
        print("Error in save_config:", str(e))
        return "Error saving configuration. Please check server logs.", 500

@app.route('/run', methods=['POST'])
def run_code_refiner():
    global process_running
    with lock:
        if process_running:
            return "Error: Process is already running.", 400  # Prevent concurrent runs

        # Signal the entrypoint script to start running
        with open('/app/run_scripts.flag', 'w') as f:
            f.write('run')

        process_running = True

    # Reload environment variables to reflect any changes made in /save
    load_dotenv(dotenv_path=env_path, override=True)

    # Fetch the project path from the .env file
    project_path = os.getenv("PROJECT_PATH", "")
    print("Project path:", project_path)  # Debugging to check if it's fetched correctly

    # Construct the URL for the emissions_report.html
    if project_path:
        report_path = os.path.join(project_path, "Report", "emissions_report.html")
        # Format the report path for URL (escape spaces and special characters)
        report_url = "file:///" + report_path.replace(" ", "%20").replace("\\", "/")
    else:
        report_url = None

    # Pass the report URL to the running.html page
    return render_template("running.html", report_url=report_url)


@app.route('/stream')
def stream():
    """
    Stream the logs of the entrypoint script execution.
    """
    def generate():
        with subprocess.Popen(
            ["/bin/bash", "/app/entrypoint.sh"],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1
        ) as process:
            for line in iter(process.stdout.readline, ''):
                yield f"data: {line}\n\n"
            process.stdout.close()
            process.wait()

    return Response(generate(), mimetype='text/event-stream')

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)

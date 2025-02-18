import modal
import os
import pathlib
import shlex
import subprocess

GRADIO_PORT = 8000

app = modal.App("gradio-app")

# Use absolute path
current_dir = os.path.dirname(os.path.abspath(__file__))
fname = "gradio_app.py"
gradio_script_local_path = os.path.join(current_dir, fname)
gradio_script_remote_path = "/root/gradio_app.py"

# Define src directory paths
src_dir_local = os.path.join(current_dir, "src")
src_dir_remote = "/root/src"

if not os.path.exists(gradio_script_local_path):
    raise RuntimeError(f"{fname} not found at {gradio_script_local_path}! Place the script with your gradio app in the same directory.")

if not os.path.exists(src_dir_local):
    raise RuntimeError(f"src directory not found at {src_dir_local}!")

# Path to requirements file
requirements_path = os.path.join(current_dir, "requirements.txt")

# Create the image with all needed files and dependencies
image = (modal.Image.debian_slim(python_version="3.11")
        .pip_install("gradio")
        .pip_install_from_requirements(requirements_path)
        .add_local_file(local_path=gradio_script_local_path, 
                        remote_path=gradio_script_remote_path)
        .add_local_dir(local_path=src_dir_local,
                       remote_path=src_dir_remote))

@app.function(
    image=image,
    allow_concurrent_inputs=100,
    concurrency_limit=1,
)
@modal.web_server(GRADIO_PORT, startup_timeout=60)
def web_app():
    target = shlex.quote(gradio_script_remote_path)
    cmd = f"python {target} --host 0.0.0.0 --port {GRADIO_PORT}"
    subprocess.Popen(cmd, shell=True)
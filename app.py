import os
import subprocess
from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/cr2_to_png')
def cr2_to_png():
    return render_template('cr2_to_png.html')


@app.route('/convert_cr2_to_png', methods=['POST'])
def convert_cr2_to_png():
    folder_path = request.form['folder']

    if os.path.isdir(folder_path):
        # Iterate through each CR2 file in the folder
        for filename in os.listdir(folder_path):
            if filename.lower().endswith('.cr2'):
                cr2_file = os.path.join(folder_path, filename)
                png_file = os.path.join(folder_path, f"{os.path.splitext(filename)[0]}.png")

                # Run darktable-cli command to convert CR2 to PNG
                subprocess.run(['darktable-cli', cr2_file, png_file])

        return f"All CR2 files in {folder_path} have been converted to PNG!"
    else:
        return "Invalid folder selected. Please try again."


# Route to display the NurfStudio page
@app.route('/nurfstudio')
def nurfstudio():
    return render_template('nurfstudio.html')


# Route to handle the form submission and run the command
@app.route('/run_nurfstudio', methods=['POST'])
def run_nurfstudio():
    cuda_device = request.form.get('cuda_device')
    websocket_port = request.form.get('websocket_port', 5000)
    max_iterations = request.form.get('max_iterations', 30000)
    downscale_factor = request.form.get('downscale_factor', 1)

    # Construct the command with the provided inputs
    command = (
        f"CUDA_VISIBLE_DEVICES={cuda_device} ns-train splatfacto-big "
        f"--viewer.websocket-port {websocket_port} "
        f"--max-num-iterations {max_iterations} "
        "--pipeline.datamanager.cache-images gpu --data . colmap "
        f"--downscale-factor {downscale_factor}"
    )

    # Run the command
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        return f"<pre>{result.stdout}</pre><br><pre>{result.stderr}</pre>"
    except Exception as e:
        return f"Error running the command: {str(e)}"


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)

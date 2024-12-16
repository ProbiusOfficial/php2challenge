from flask import Flask, request, jsonify, render_template_string
import os
import shutil
import subprocess
import random
import string
import json
import requests


app = Flask(__name__)

# ------------------ Configuration ------------------
DOCKER_TEMPLATE_DIR = "docker-template"  # Path to Docker templates
OUTPUT_DIR = "generated_projects"        # Path to store generated projects
os.makedirs(OUTPUT_DIR, exist_ok=True)

def random_string(length=8):
    """Generate a random string for file naming."""
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

# ------------------ Web UI ------------------
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>CTF PHP Challenge Builder</title>
    <style>
        body {
            background-color: #1e1e2e;
            color: #cdd6f4;
            font-family: 'Arial', sans-serif;
            margin: 0;
            padding: 0;
            display: flex;
            justify-content: center;
            align-items: center;
            min-height: 100vh;
        }

        .container {
            max-width: 1200px;
            margin: 20px auto;
            background-color: #313244;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.5);
        }

        h1 {
            text-align: center;
            margin-bottom: 20px;
            color: #89b4fa;
        }

        form {
            display: grid;
            grid-template-columns: 2fr 1fr;
            gap: 20px;
        }

        .form-left, .form-right {
            display: flex;
            flex-direction: column;
        }

        .form-group {
            margin-bottom: 15px;
        }

        label {
            margin-bottom: 5px;
            font-weight: bold;
        }

        textarea, input, select {
            width: 96.5%;
            padding: 10px;
            background-color: #45475a;
            color: #cdd6f4;
            border: none;
            border-radius: 4px;
        }

        textarea {
            height: 250px;
        }

        button {
            grid-column: 1 / -1;
            background-color: #89b4fa;
            color: #1e1e2e;
            border: none;
            padding: 15px;
            border-radius: 4px;
            font-weight: bold;
            cursor: pointer;
            transition: background-color 0.3s ease;
        }

        button:hover {
            background-color: #74c7ec;
        }

        pre {
            margin: 20px 0;
            padding: 20px;
            background-color: #45475a;
            color: #f38ba8;
            border-radius: 8px;
            overflow-x: auto;
        }
    </style>
</head>
<body>
    <!-- Container -->
    <div class="container">
        <!-- Title -->
        <h1>快速生成与部署工具</h1>
        <!-- Form -->
        <form method="POST" action="/build">
            <!-- Form Left -->
            <div class="form-left">
                <!-- PHP Code Group -->
                <div class="form-group">
                    <label for="php_code">在此处粘贴PHP代码:</label>
                    <textarea id="php_code" name="php_code" required></textarea>
                </div>
                <!-- PHP Version Group -->
                <div class="form-group">
                    <label for="php_version">PHP版本选择:</label>
                    <select id="php_version" name="php_version">
                        <option value="7.3">7.3</option>
                        <option value="8.0">8.0</option>
                        <option value="8.1">8.1</option>
                    </select>
                </div>
            </div>

            <!-- Form Right -->
            <div class="form-right">
                <!-- Title Group -->
                <div class="form-group">
                    <label for="title">题目名称:</label>
                    <input type="text" id="title" name="title" required>
                </div>
                <!-- Container Name Group -->
                <div class="form-group">
                    <label for="container_name">容器名称:</label>
                    <input type="text" id="container_name" name="container_name" required>
                </div>
                <!-- Memory Requirement Group -->
                <div class="form-group">
                    <label for="memory">内存需求(:MB):</label>
                    <input type="text" id="memory" name="memory" required>
                </div>
            </div>

            <!-- Submit Button -->
            <button type="submit">点击构建</button>
        </form>

        <!-- Result Display -->
        {% if result %}
        <h2 style="text-align: center; color: #f38ba8;">构建结果:</h2>
        <pre>{{ result }}</pre>
        {% endif %}
    </div>
</body>
</html>
"""

# ------------------ Helper Functions ------------------
def prepare_project(title, php_version, container_name, memory, php_code):
    """Prepare the project directory and Dockerfile."""
    project_folder = os.path.join(OUTPUT_DIR, title)
    os.makedirs(project_folder, exist_ok=True)
    
    version_folder = os.path.join(DOCKER_TEMPLATE_DIR, php_version)
    if not os.path.exists(version_folder):
        raise ValueError("Unsupported PHP version template not found")
    
    shutil.copytree(version_folder, project_folder, dirs_exist_ok=True)
    
    src_folder = os.path.join(project_folder, "./")
    os.makedirs(src_folder, exist_ok=True)
    index_file = os.path.join(src_folder, "index.php")
    with open(index_file, "w") as f:
        f.write(php_code)
    
    dockerfile_path = project_folder
    build_command = [
        "docker", "build",
        "-t", container_name,
        dockerfile_path
    ]
    process = subprocess.Popen(build_command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    logs = []
    for line in process.stdout:
        print(line, end="")  # Print to terminal (real-time)
        logs.append(line)
    process.wait()
    if process.returncode != 0:
        raise Exception("Docker build failed")

    # Return project metadata and logs
    
    return {
        "题目名称": title,
        "容器名称": container_name,
        "内存需求": memory,
        "构建日志": logs
    }
    
# ------------------ 平台相关参数以及功能函数 ------------------
GZCTF_Token="YOUR_TOKEN"
GZCTF_URL = "http://demo.hello-ctf.com"
GAME_ID = "1" # 该场比赛的ID
cookies = {
    'GZCTF_Token': GZCTF_Token
}

def get_challenge_id(title, container_name, memory):
    
    API_URL = GZCTF_URL + f"/api/edit/games/{GAME_ID}/challenges"
    print(API_URL)
    json_data = {
    'title': title,
    'tag': 'Web',
    'type': 'DynamicContainer',
}   
    print("[working] get_challenge_id")
    response = requests.post(API_URL, json=json_data, cookies=cookies)
    print(response.json())
    if response.status_code != 200:
        raise Exception("Failed to create challenge")
    challenge_id = response.json()["id"]
    return challenge_id

def deploy_challenge(challenge_id,title, container_name, memory):
    API_URL = GZCTF_URL + f"/api/edit/games/{GAME_ID}/challenges/{challenge_id}"
    json_data = {
  "id": challenge_id,
  "title": title,
  "content": "",
  "tag": "Web",
  "type": "DynamicContainer",
  "hints": [],
  "flagTemplate": None,
  "acceptedCount": 0,
  "fileName": "attachment",
  "attachment": None,
  "testContainer": None,
  "flags": [],
  "containerImage": container_name,
  "memoryLimit": memory,
  "cpuCount": 1,
  "storageLimit": 256,
  "containerExposePort": 80,
  "enableTrafficCapture": False,
  "originalScore": 1000,
  "minScoreRate": 0.25,
  "difficulty": 5
}
    print(f"[working] deploy_challenge:{API_URL}")
    response = requests.put(API_URL, json=json_data, cookies=cookies)
    print 
    print(response.json())
    if response.status_code != 200:
        raise Exception("Failed to deploy challenge")
    return response.json()

# ------------------ Routes ------------------
@app.route('/', methods=['GET'])
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/build', methods=['POST'])
def build():
    try:
        php_code = request.form['php_code']
        title = request.form['title']
        php_version = request.form['php_version']
        container_name = request.form['container_name']
        memory = request.form['memory']
        
        result = prepare_project(title, php_version, container_name, memory, php_code)

        logs = result["构建日志"]
        logs = "\n".join(logs)


        challenge_id = get_challenge_id(title, container_name, memory)

        deploy_result = deploy_challenge(challenge_id, title, container_name, memory)

        print_content = f"完成题目{title}的构建与部署\n，构建日志如下：\n{logs}\n部署结果如下：\n{deploy_result}"

        return render_template_string(HTML_TEMPLATE, result=print_content)
    except Exception as e:
        return render_template_string(HTML_TEMPLATE, result=f"Error: {str(e)}")

# ------------------ Run Server ------------------
if __name__ == '__main__':
    app.run(debug=True)

import yaml
import json
import requests

# ------------------ 配置参数 ------------------
GZCTF_Token = "YOUR_TOKEN"              # GZCTF平台的Token
GZCTF_URL = "d" # GZCTF平台的URL
GAME_ID = "1"                           # 比赛ID

def get_challenge_id(title):
    """创建题目并获取题目ID"""
    API_URL = GZCTF_URL + f"/api/edit/games/{GAME_ID}/challenges"
    headers = {
        'Content-Type': 'application/json'
    }
    json_data = {
        'title': title,
        'tag': 'Web',
        'type': 'DynamicContainer',
    }
    response = requests.post(
        API_URL, 
        json=json_data,  # 使用json参数而不是data
        headers=headers,
        cookies={'GZCTF_Token': GZCTF_Token}
    )
    if response.status_code != 200:
        raise Exception(f"创建题目失败: {response.text}")
    return response.json()["id"]

def deploy_challenge(challenge_id, title, container_name, memory=512):
    """部署题目"""
    API_URL = GZCTF_URL + f"/api/edit/games/{GAME_ID}/challenges/{challenge_id}"
    headers = {
        'Content-Type': 'application/json'
    }
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
    response = requests.put(
        API_URL, 
        json=json_data,  # 使用json参数而不是data
        headers=headers,
        cookies={'GZCTF_Token': GZCTF_Token}
    )
    if response.status_code != 200:
        raise Exception(f"部署题目失败: {response.text}")
    return response.json()

def main():
    # 读取docker-compose.yml文件
    with open("docker-compose.yml", "r", encoding="utf-8") as f:
        compose_data = yaml.safe_load(f)
    
    # 遍历所有服务
    for service_name, service_config in compose_data['services'].items():
        try:
            print(f"正在处理题目: {service_name}")
            
            # 从compose配置中获取镜像名称
            container_name = service_config.get('image')
            if not container_name:
                print(f"跳过 {service_name}: 未找到镜像名称")
                continue
            
            # 创建题目并获取ID
            challenge_id = get_challenge_id(service_name)
            
            # 部署题目
            deploy_result = deploy_challenge(
                challenge_id,
                service_name,
                container_name
            )
            
            print(f"题目 {service_name} 部署成功!")
            print("部署结果:", json.dumps(deploy_result, indent=2, ensure_ascii=False))
            
        except Exception as e:
            print(f"处理题目 {service_name} 时出错: {str(e)}")

if __name__ == "__main__":
    main()
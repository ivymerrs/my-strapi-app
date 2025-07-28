# my-project/app.py

from flask import Flask, render_template, request, jsonify, g
import requests
import random
import os
from child_main import ChildInteractionSimulator
from flask_cors import CORS # 确保已安装 pip install Flask-Cors
from dotenv import load_dotenv
load_dotenv()

# --- Flask 应用初始化 ---
app = Flask(__name__, template_folder='templates', static_folder='static')
CORS(app) # 启用 CORS

# --- 全局变量：用于存储模拟器实例和 Strapi 数据缓存 ---
global_simulator_instance = None # 存储 ChildInteractionSimulator 的一个实例
global_strapi_data_cache = {
    'personalities': [],
    'trait_expressions': [],
    'scenario_instances': [], # 具体的场景
    'daily_challenges': [], # 【新增】大主题挑战
    'evaluation_rules': []
}

# --- 全局变量：评估规则缓存 ---
EVALUATION_RULES_CACHE = []

# --- 全局变量：阿里云 DashScope API 配置 ---
ALIYUN_DASHSCOPE_API_KEY = os.getenv('ALIYUN_DASHSCOPE_API_KEY')
if not ALIYUN_DASHSCOPE_API_KEY:
    print("警告: 未设置 ALIYUN_DASHSCOPE_API_KEY 环境变量。LLM 功能可能无法工作。")

# --- 辅助函数：从 Strapi 获取数据 ---
# 这个函数应该在所有需要使用它的函数之前定义
def _get_entity_data_from_strapi(api_uid, populate_all=False):
    strapi_url = os.getenv('STRAPI_URL', 'http://localhost:1337')
    api_token = os.getenv('STRAPI_API_TOKEN')

    if not api_token:
        print("警告: 未设置 STRAPI_API_TOKEN 环境变量。某些功能可能无法工作。")
        return []

    headers = {
        'Authorization': f'Bearer {api_token}',
        'Content-Type': 'application/json'
    }

    populate_param = "populate=*" if populate_all else ""
    url = f"{strapi_url}/api/{api_uid}?{populate_param}"
    
    print(f"DEBUG: 正在请求 Strapi API: {url}")

    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status() # 对 4xx 或 5xx 状态码抛出 HTTPError
        data = response.json()

        if 'data' in data and isinstance(data['data'], list):
            extracted_data = []
            for item in data['data']:
                # --- 【新增调试打印】查看原始 item 结构 ---
                print(f"DEBUG: Strapi 原始 Item ({api_uid}): {item}")
                print(f"DEBUG: Item ID: {item.get('id')}")
                print(f"DEBUG: Item Attributes: {item.get('attributes')}")
                # --- 结束新增调试打印 ---

                extracted_item = {
                    'id': item.get('id')
                }
                # 遍历 item 字典中的所有键值对，将它们直接添加到 extracted_item 中
                # 排除可能不是我们直接想要的复杂嵌套结构，或按需选择
                for key, value in item.items():
                    # 排除 'id' 和 'attributes' (因为它不存在了)
                    # 排除嵌套对象和列表，除非你希望直接平铺它们（对于 name/description 这种简单字段是没问题的）
                    # 对于 'name', 'description', 'createdAt', 'updatedAt', 'publishedAt' 等简单字段，可以直接提取
                    # 对于关联字段 (如 'dialogue_scenarios', 'core_needs')，如果需要，可能需要更复杂的递归处理
                    if key not in ['id', 'attributes']: # 确保不重复添加id，且忽略attributes
                        # 简单的平铺，直接提取顶层字段
                        extracted_item[key] = value
                
                # 如果你只关心 'id' 和 'name' 并且其他字段是可选的，可以简化成这样：
                # extracted_item = {
                #     'id': item.get('id'),
                #     'name': item.get('name') # 直接从 item 中获取 'name'
                # }

                extracted_data.append(extracted_item)

                # ⚠️ 之前关于 'name' 缺失的警告可以保留，但现在应该不会再触发了，因为直接从 item 中获取了
                if 'name' not in extracted_item:
                     print(f"警告: Strapi实体 {api_uid} (ID: {item.get('id')}) 缺少 'name' 属性。原始 Item: {item}")
            return extracted_data
        else:
            print(f"警告: Strapi API '{api_uid}' 返回的数据结构不符合预期或无数据: {data}")
            return []
    except requests.exceptions.RequestException as e:
        print(f"错误: 访问 Strapi API '{api_uid}' 失败: {e}")
        return []

# --- 加载评估规则 ---
def load_evaluation_rules_from_strapi():
    global EVALUATION_RULES_CACHE
    try:
        # 确保 populate=* 获取所有关系字段，特别是 applies_to_personality/challenge/scenario 的 name
        rules_data = _get_entity_data_from_strapi("responses", populate_all=True)
        
        parsed_rules = []
        for rule_entry in rules_data:
            attrs = rule_entry.get('attributes', {})
            rule = {
                'id': rule_entry.get('id'),
                'rulename': attrs.get('rulename'),
                'parent_keywords': attrs.get('parent_keywords', []), # 假设现在是JSON Array，直接解析为Python list
                'evaluation_grade': attrs.get('evaluation_grade'),
                'reason_analysis': attrs.get('reason_analysis'),
                'suggestion_encouragement': attrs.get('suggestion_encouragement'), # 新增字段
                'applies_to_personality_name': attrs.get('applies_to_personality', {}).get('data', {}).get('attributes', {}).get('name') if attrs.get('applies_to_personality') and attrs.get('applies_to_personality').get('data') else None,
                'applies_to_challenge_name': attrs.get('applies_to_challenge', {}).get('data', {}).get('attributes', {}).get('name') if attrs.get('applies_to_challenge') and attrs.get('applies_to_challenge').get('data') else None,
                'applies_to_scenario_name': attrs.get('applies_to_scenario', {}).get('data', {}).get('attributes', {}).get('name') if attrs.get('applies_to_scenario') and attrs.get('applies_to_scenario').get('data') else None,
            }
            parsed_rules.append(rule)
        EVALUATION_RULES_CACHE = parsed_rules
        print(f"--- 成功从 Strapi 加载并缓存 {len(EVALUATION_RULES_CACHE)} 条评估规则 ---")
    except Exception as e: # 捕获更广泛的异常，包括解析错误
        print(f"ERROR: 无法从Strapi加载或解析评估规则: {e}")
        EVALUATION_RULES_CACHE = []

# --- 加载所有模拟器所需数据 (人格、特质表达、情境实例) ---
def load_all_required_strapi_data():
    global global_strapi_data_cache
    print("--- 正在从 Strapi 加载所有所需数据 (人格、特质表达、情境实例、评估规则) ---")
    try:
        # 加载人格数据
        global_strapi_data_cache['personalities'] = _get_entity_data_from_strapi("personality-traits", populate_all=True)
        # 加载特质表达数据（API ID: trait-expression）
        global_strapi_data_cache['trait_expressions'] = _get_entity_data_from_strapi("trait-expressions", populate_all=True)
        # 加载情境实例数据（API ID: dialogue-scenario）
        global_strapi_data_cache['scenario_instances'] = _get_entity_data_from_strapi("dialogue-scenarios", populate_all=True)
        # 【新增】加载日常挑战
        global_strapi_data_cache['daily_challenges'] = _get_entity_data_from_strapi("daily-challenges", populate_all=True)
        # 加载评估规则（假设之前 load_evaluation_rules_from_strapi 已经处理了 'responses'）
        print("--- 成功加载所有所需数据 ---")
        
        # --- 添加这些打印语句 ---
        print("\n--- DEBUG: Cache Contents After Setup ---")
        print(f"Personalities loaded: {len(global_strapi_data_cache['personalities'])} items")
        if global_strapi_data_cache['personalities']:
            print(f"First personality item: {global_strapi_data_cache['personalities'][0]}")
        
        print(f"Trait Expressions loaded: {len(global_strapi_data_cache['trait_expressions'])} items")
        if global_strapi_data_cache['trait_expressions']:
            print(f"First trait expression item: {global_strapi_data_cache['trait_expressions'][0]}")
            
        print(f"Scenario Instances loaded: {len(global_strapi_data_cache['scenario_instances'])} items")
        if global_strapi_data_cache['scenario_instances']:
            print(f"First scenario instance item: {global_strapi_data_cache['scenario_instances'][0]}")
            
        print(f"Daily Challenges loaded: {len(global_strapi_data_cache['daily_challenges'])} items")
        if global_strapi_data_cache['daily_challenges']:
            print(f"First daily challenge item: {global_strapi_data_cache['daily_challenges'][0]}")
        print("--- END DEBUG Cache Contents ---\n")
        # --- 结束添加的打印语句 ---
    except Exception as e:
        print(f"ERROR: 无法从Strapi加载所有所需数据: {e}")
        raise

# --- 应用启动时初始化所有数据和模拟器实例的函数 ---
def setup_application_data_and_simulator():
    global global_simulator_instance
    
    # 1. 加载所有 Strapi 数据（包括模拟器和评估规则所需的）
    load_all_required_strapi_data()
    load_evaluation_rules_from_strapi() # 单独调用，因为 EVALUATION_RULES_CACHE 是独立的

    # 2. 实例化 ChildInteractionSimulator
    try:
        global_simulator_instance = ChildInteractionSimulator(
            personality_data=global_strapi_data_cache['personalities'],
            trait_expression_data=global_strapi_data_cache['trait_expressions'],
            scenario_instance_data=global_strapi_data_cache['scenario_instances'],
            daily_challenges_data=global_strapi_data_cache['daily_challenges']
        )
        print("--- ChildInteractionSimulator 实例化成功 ---")
    except Exception as e:
        print(f"ERROR: ChildInteractionSimulator 实例化失败: {e}")
        raise # 重新抛出异常以阻止应用在模拟器无法实例化时运行


# --- Flask 路由定义 ---
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/get_personalities', methods=['GET'])
def get_personalities():
    """获取所有人格特质的名称和 ID，用于前端下拉菜单"""
    # 直接从已缓存的全局数据中返回，无需再次请求 Strapi
    # 确保这里的返回格式是前端期望的 [{id: x, name: 'y'}]
    return jsonify([{'id': p.get('id'), 'name': p.get('name')} for p in global_strapi_data_cache['personalities']])


@app.route('/get_daily_challenges', methods=['GET'])
def get_daily_challenges():
    """获取所有日常挑战的名称和 ID，用于前端下拉菜单"""
    # 【修改】从 daily_challenges 缓存中获取数据
    challenges_for_frontend = [
        {'id': c.get('id'), 'name': c.get('name')}
        for c in global_strapi_data_cache['daily_challenges']
        if c.get('id') and c.get('name') # 确保 ID 和 name 存在
    ]
    print(f"DEBUG: Preparing daily challenges for frontend: {challenges_for_frontend}")
    return jsonify(challenges_for_frontend)


@app.route('/get_scenarios_by_challenge_id/<int:challenge_id>', methods=['GET'])
def get_scenarios_by_challenge_id(challenge_id):
    filtered_scenarios = []
    # 遍历所有情境实例，找到与给定挑战ID匹配的
    for scenario in global_strapi_data_cache['scenario_instances']:
        # 检查 scenario 是否有关联的 daily_challenge
        if 'daily_challenge' in scenario and scenario['daily_challenge'] and scenario['daily_challenge'].get('id') == challenge_id:
            filtered_scenarios.append({
                'id': scenario.get('id'),
                'name': scenario.get('name'),
                'description': scenario.get('description') # 可以添加更多你想传给前端的字段
            })
    print(f"DEBUG: Filtered scenarios for challenge {challenge_id}: {filtered_scenarios}")
    return jsonify(filtered_scenarios)


@app.route('/simulate_dialogue', methods=['POST'])
def simulate_dialogue():
    data = request.json
    parent_utterance = data.get('parent_utterance')
    personality_id = data.get('personality_id')
    daily_challenge_id = data.get('daily_challenge_id')

    if not all([parent_utterance, personality_id, daily_challenge_id]):
        return jsonify({'error': '缺少必要的参数'}), 400

    print(f"DEBUG: 收到 simulate_dialogue 请求 - 父级输入: '{parent_utterance}', 人格ID: {personality_id}, 挑战ID: {daily_challenge_id}")

    # 根据 ID 从全局缓存中获取名称
    selected_personality_name = None
    selected_challenge_name = None

    for p in global_strapi_data_cache['personalities']:
        if str(p.get('id')) == str(personality_id):
            selected_personality_name = p.get('name')
            break
    
    for c in global_strapi_data_cache['daily_challenges']:
        if str(c.get('id')) == str(daily_challenge_id):
            selected_challenge_name = c.get('name')
            break

    if not selected_personality_name or not selected_challenge_name:
        return jsonify({'error': '无效的人格或挑战ID'}), 400

    try:
        # 使用在应用启动时已经实例化好的全局模拟器
        if global_simulator_instance is None:
            # 理论上不会发生，因为 setup_application_data_and_simulator 应该已在应用启动时运行
            raise Exception("ChildInteractionSimulator 未初始化！请检查应用启动日志。")
        
        result = global_simulator_instance.simulate_dialogue(parent_utterance, selected_personality_name, selected_challenge_name)
        
        return jsonify(result)
    except Exception as e:
        print(f"ERROR: 模拟对话过程中发生错误: {e}")
        return jsonify({'error': f'模拟对话失败: {str(e)}'}), 500


# --- 应用启动入口 ---
if __name__ == '__main__':
    # 在应用上下文内调用设置函数，确保所有 Flask 相关操作都能正常进行
    with app.app_context():
        setup_application_data_and_simulator()
    
    # 获取端口号，优先使用环境变量，否则使用默认值
    port = int(os.environ.get('PORT', 5000))
    
    # 运行 Flask 应用
    app.run(debug=False, host='0.0.0.0', port=port)
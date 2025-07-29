# my-project/app.py

from flask import Flask, render_template, request, jsonify, g
import requests
import random
import os
from datetime import datetime
from child_main import ChildInteractionSimulator
from flask_cors import CORS # 确保已安装 pip install Flask-Cors
from dotenv import load_dotenv
load_dotenv()

# --- Flask 应用初始化 ---
app = Flask(__name__, template_folder='templates', static_folder='static')
CORS(app) # 启用 CORS

# --- 在第一次请求时初始化数据 ---
@app.before_request
def initialize_data_on_first_request():
    global data_initialized
    if not data_initialized:
        print("DEBUG: 第一次请求，开始初始化数据...")
        try:
            setup_application_data_and_simulator()
            data_initialized = True
            print("DEBUG: 数据初始化完成")
        except Exception as e:
            print(f"ERROR: 数据初始化失败: {e}")
            import traceback
            print(f"ERROR: 详细错误信息: {traceback.format_exc()}")

# --- 全局变量：用于存储模拟器实例和 Strapi 数据缓存 ---
global_simulator_instance = None # 存储 ChildInteractionSimulator 的一个实例

# --- 全局变量：数据初始化标志 ---
data_initialized = False
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
    """从 Strapi 获取指定 API 的数据"""
    try:
        # 获取环境变量
        strapi_url = os.getenv('STRAPI_URL')
        
        print(f"DEBUG: STRAPI_URL = {strapi_url}")
        
        if not strapi_url:
            print("ERROR: STRAPI_URL 未设置")
            return []

        # 构建请求 URL - 使用公开 API
        base_url = strapi_url.rstrip('/')
        
        # 根据 API UID 映射到公开 API 端点
        api_mapping = {
            'core-needs': 'public/core-needs',
            'personality-traits': 'public/personality-traits',
            'dialogue-scenarios': 'public/dialogue-scenarios',
            'ideal-responses': 'public/ideal-responses',
            'responses': 'public/responses',
            'trait-expressions': 'public/trait-expressions',
            'daily-challenges': 'public/daily-challenges'
        }
        
        # 如果没有映射，使用默认的公开 API 格式
        if api_uid in api_mapping:
            api_url = f"{base_url}/api/{api_mapping[api_uid]}"
        else:
            api_url = f"{base_url}/api/public/{api_uid}"
        
        # 设置请求头 - 公开 API 不需要认证
        headers = {
            'Content-Type': 'application/json'
        }
        
        print(f"DEBUG: 正在从 Strapi 公开 API 获取数据 - URL: {api_url}")
        print(f"DEBUG: 请求头: {headers}")
        
        # 发送请求
        response = requests.get(api_url, headers=headers, timeout=30)
        
        print(f"DEBUG: Strapi 响应状态码: {response.status_code}")
        print(f"DEBUG: Strapi 响应内容: {response.text[:1000]}...")  # 显示更多内容
        
        if response.status_code == 200:
            data = response.json()
            # 公开 API 直接返回数据，不需要 data 包装
            items = data.get('data', data) if isinstance(data, dict) else data
            
            print(f"DEBUG: 原始数据项数量: {len(items)}")
            if items:
                print(f"DEBUG: 第一个数据项示例: {items[0]}")
            
            # 提取和扁平化数据
            extracted_items = []
            for item in items:
                print(f"DEBUG: 处理数据项: {item}")
                extracted_item = {'id': item.get('id')}
                # 将 attributes 中的所有字段直接提取到顶层
                if 'attributes' in item:
                    print(f"DEBUG: 找到 attributes: {item['attributes']}")
                    for key, value in item['attributes'].items():
                        if key != 'id':  # 避免重复
                            extracted_item[key] = value
                else:
                    print(f"DEBUG: 没有找到 attributes，直接使用顶层字段")
                    # 如果没有 attributes，直接使用顶层字段
                    for key, value in item.items():
                        if key != 'id':  # 避免重复
                            extracted_item[key] = value
                extracted_items.append(extracted_item)
            
            print(f"DEBUG: 成功提取 {len(extracted_items)} 条数据")
            if extracted_items:
                print(f"DEBUG: 第一个提取项示例: {extracted_items[0]}")
            return extracted_items
        else:
            print(f"ERROR: Strapi API 请求失败，状态码: {response.status_code}")
            print(f"ERROR: 错误响应: {response.text}")
            return []
            
    except Exception as e:
        print(f"ERROR: 从 Strapi 获取数据时发生异常: {e}")
        import traceback
        print(f"ERROR: 详细错误信息: {traceback.format_exc()}")
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

@app.route('/test')
def test():
    """简单的测试端点"""
    return jsonify({
        'message': 'Hello from Flask!',
        'timestamp': str(datetime.now())
    })

@app.route('/health')
def health_check():
    """健康检查端点，用于测试应用状态"""
    global data_initialized
    
    # 确保数据已初始化
    if not data_initialized:
        print("DEBUG: 健康检查触发数据初始化...")
        try:
            setup_application_data_and_simulator()
            data_initialized = True
            print("DEBUG: 健康检查数据初始化完成")
        except Exception as e:
            print(f"ERROR: 健康检查数据初始化失败: {e}")
            import traceback
            print(f"ERROR: 详细错误信息: {traceback.format_exc()}")
    
    try:
        return jsonify({
            'status': 'healthy',
            'cache_keys': list(global_strapi_data_cache.keys()),
            'personalities_count': len(global_strapi_data_cache.get('personalities', [])),
            'daily_challenges_count': len(global_strapi_data_cache.get('daily_challenges', [])),
            'simulator_initialized': global_simulator_instance is not None,
            'data_initialized': data_initialized,
            'environment_vars': {
                'STRAPI_URL': 'SET' if os.getenv('STRAPI_URL') else 'NOT_SET',
                'STRAPI_API_TOKEN': 'SET' if os.getenv('STRAPI_API_TOKEN') else 'NOT_SET',
                'ALIYUN_DASHSCOPE_API_KEY': 'SET' if os.getenv('ALIYUN_DASHSCOPE_API_KEY') else 'NOT_SET'
            }
        })
    except Exception as e:
        return jsonify({
            'status': 'unhealthy',
            'error': str(e)
        }), 500

@app.route('/get_personalities', methods=['GET'])
def get_personalities():
    """获取所有人格特质的名称和 ID，用于前端下拉菜单"""
    try:
        print("DEBUG: 开始获取人格数据")
        print(f"DEBUG: 全局缓存键: {list(global_strapi_data_cache.keys())}")
        personalities_data = global_strapi_data_cache.get('personalities', [])
        print(f"DEBUG: 从缓存获取的人格数据: {personalities_data}")
        
        # 如果缓存为空，使用硬编码数据
        if not personalities_data:
            print("DEBUG: 缓存为空，使用硬编码数据")
            hardcoded_personalities = [
                {'id': 1, 'name': '内向敏感型'},
                {'id': 2, 'name': '外向活泼型'},
                {'id': 3, 'name': '专注执着型'},
                {'id': 4, 'name': '创意想象型'}
            ]
            return jsonify(hardcoded_personalities)
        
        result = [{'id': p.get('id'), 'name': p.get('name')} for p in personalities_data]
        print(f"DEBUG: 返回的人格数据: {result}")
        return jsonify(result)
    except Exception as e:
        print(f"ERROR: 获取人格数据失败: {e}")
        import traceback
        print(f"ERROR: 详细错误信息: {traceback.format_exc()}")
        return jsonify([]), 500


@app.route('/get_daily_challenges', methods=['GET'])
def get_daily_challenges():
    """获取所有日常挑战的名称和 ID，用于前端下拉菜单"""
    try:
        print("DEBUG: 开始获取日常挑战数据")
        print(f"DEBUG: 全局缓存键: {list(global_strapi_data_cache.keys())}")
        challenges_data = global_strapi_data_cache.get('daily_challenges', [])
        print(f"DEBUG: 从缓存获取的挑战数据: {challenges_data}")
        
        # 如果缓存为空，使用硬编码数据
        if not challenges_data:
            print("DEBUG: 缓存为空，使用硬编码数据")
            hardcoded_challenges = [
                {'id': 1, 'name': '学习困难'},
                {'id': 2, 'name': '社交焦虑'},
                {'id': 3, 'name': '情绪管理'},
                {'id': 4, 'name': '注意力不集中'}
            ]
            return jsonify(hardcoded_challenges)
        
        challenges_for_frontend = [
            {'id': c.get('id'), 'name': c.get('name')}
            for c in challenges_data
            if c.get('id') and c.get('name') # 确保 ID 和 name 存在
        ]
        print(f"DEBUG: 返回的挑战数据: {challenges_for_frontend}")
        return jsonify(challenges_for_frontend)
    except Exception as e:
        print(f"ERROR: 获取日常挑战数据失败: {e}")
        import traceback
        print(f"ERROR: 详细错误信息: {traceback.format_exc()}")
        return jsonify([]), 500


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
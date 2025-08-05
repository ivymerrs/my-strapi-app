# my-project/app.py
import os
import json
import requests
import random
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import sys

app = Flask(__name__)
CORS(app)

# 设置静态文件缓存控制
@app.after_request
def add_header(response):
    if 'Cache-Control' not in response.headers:
        response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    return response

# 全局数据缓存
global_strapi_data_cache = {}

# 优先从环境变量加载，如果没有设置则使用 None，而不是本地地址
ALIYUN_DASHSCOPE_API_KEY = os.environ.get("ALIYUN_DASHSCOPE_API_KEY", "")
# 支持两种环境变量名称：STRAPI_API_URL 和 STRAPI_URL
STRAPI_API_URL = os.environ.get("STRAPI_API_URL") or os.environ.get("STRAPI_URL")

# 添加详细的环境变量调试信息
print("=== 环境变量调试信息 ===", file=sys.stderr)
print(f"STRAPI_API_URL 环境变量值: {os.environ.get('STRAPI_API_URL', '未设置')}", file=sys.stderr)
print(f"STRAPI_URL 环境变量值: {os.environ.get('STRAPI_URL', '未设置')}", file=sys.stderr)
print(f"ALIYUN_DASHSCOPE_API_KEY 环境变量值: {os.environ.get('ALIYUN_DASHSCOPE_API_KEY', '未设置')}", file=sys.stderr)

# 如果没有设置环境变量，则打印警告并使用本地地址作为备选
if not STRAPI_API_URL:
    STRAPI_API_URL = "http://localhost:1337"
    print(f"WARNING: STRAPI_API_URL 和 STRAPI_URL 环境变量都未设置，使用默认地址: {STRAPI_API_URL}", file=sys.stderr)
else:
    print(f"INFO: 环境变量已设置，使用地址: {STRAPI_API_URL}", file=sys.stderr)


class ChildInteractionSimulator:
    def __init__(self, personalities, trait_expressions, scenario_instances, daily_challenges, evaluation_rules):
        self.personalities = personalities
        self.trait_expressions = trait_expressions
        self.scenario_instances = scenario_instances
        self.daily_challenges = daily_challenges
        self.evaluation_rules = evaluation_rules
        self.qwen_model_name = "qwen-turbo"
        self.api_key = ALIYUN_DASHSCOPE_API_KEY

    def _get_entity_data_from_strapi(self, entity_name):
        """从 Strapi API 获取数据，并增加错误处理"""
        url = f"{STRAPI_API_URL}/api/{entity_name}?populate=*"
        print(f"DEBUG: 尝试从 {url} 获取数据...")
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            data = response.json()
            return data.get('data', [])
        except requests.exceptions.Timeout:
            print(f"ERROR: 从 Strapi 获取 {entity_name} 数据超时。")
        except requests.exceptions.ConnectionError as e:
            print(f"ERROR: 无法连接到 Strapi 服务器，请检查 Strapi 是否已运行在 {STRAPI_API_URL}。错误: {e}")
        except requests.exceptions.RequestException as e:
            print(f"ERROR: 从 Strapi 获取 {entity_name} 数据失败。错误: {e}")
        return []

    def _call_qwen_model(self, prompt_messages):
        """封装调用阿里云通义千问模型的逻辑，增加错误处理"""
        if not self.api_key:
            print("ERROR: ALIYUN_DASHSCOPE_API_KEY 未设置。", file=sys.stderr)
            return None

        try:
            headers = {
                'Authorization': f'Bearer {self.api_key}',
                'Content-Type': 'application/json'
            }
            payload = {
                "model": self.qwen_model_name,
                "input": {
                    "messages": prompt_messages
                },
                "parameters": {
                    "result_format": "message"
                }
            }
            response = requests.post('https://dashscope.aliyuncs.com/api/v1/services/aigc/text-generation/generation', headers=headers, json=payload, timeout=20)
            response.raise_for_status()
            result = response.json()
            return result['output']['choices'][0]['message']['content']
        except requests.exceptions.RequestException as e:
            print(f"ERROR: 调用大模型失败。请检查 API 密钥是否有效或网络连接。错误: {e}", file=sys.stderr)
        except (KeyError, IndexError) as e:
            print(f"ERROR: 大模型返回的数据格式不正确。错误: {e}", file=sys.stderr)
        return None

    def _generate_child_response_with_qwen(self, parent_input, selected_personality, selected_scenario):
        """根据人格和情境生成孩子的回应"""
        try:
            # 处理人格数据
            if 'attributes' in selected_personality:
                personality_name = selected_personality['attributes']['name']
                personality_desc = selected_personality['attributes']['description']
            else:
                personality_name = selected_personality.get('name', '未知人格')
                personality_desc = selected_personality.get('description', '')
            
            # 处理情境数据
            if 'attributes' in selected_scenario:
                scenario_name = selected_scenario['attributes']['name']
                scenario_desc = selected_scenario['attributes']['description']
            else:
                scenario_name = selected_scenario.get('name', '默认情境')
                scenario_desc = selected_scenario.get('description', '')

            prompt_messages = [
                {"role": "system", "content": f"你正在扮演一个拥有人格特质为'{personality_name}'的孩子。他的特质是：'{personality_desc}'。当前情境是：'{scenario_name}'，情境描述：'{scenario_desc}'。请根据这些信息，给出一个符合孩子身份的回应，并保持简短。"},
                {"role": "user", "content": parent_input}
            ]
            return self._call_qwen_model(prompt_messages)
        except Exception as e:
            print(f"ERROR: 生成孩子回应失败: {e}", file=sys.stderr)
            return "对不起，我现在有点困惑，能请你再说一遍吗？"

    def _evaluate_response(self, parent_input, child_response, selected_personality, selected_scenario):
        """评估家长输入，并返回包含评分、分值和情绪分析的结构化数据。"""
        # 处理人格数据
        if 'attributes' in selected_personality:
            personality_name = selected_personality['attributes']['name']
            personality_desc = selected_personality['attributes']['description']
        else:
            personality_name = selected_personality.get('name', '未知人格')
            personality_desc = selected_personality.get('description', '')
        
        # 处理情境数据
        if 'attributes' in selected_scenario:
            scenario_name = selected_scenario['attributes']['name']
            scenario_desc = selected_scenario['attributes']['description']
        else:
            scenario_name = selected_scenario.get('name', '默认情境')
            scenario_desc = selected_scenario.get('description', '')

        # 构建评估规则提示
        evaluation_rules_text = ""
        if self.evaluation_rules:
            evaluation_rules_text = "\n\n评估规则参考：\n"
            for rule in self.evaluation_rules:
                if 'attributes' in rule:
                    rule_name = rule['attributes'].get('rule_name', '')
                    rule_desc = rule['attributes'].get('rule_description', '')
                    trigger_condition = rule['attributes'].get('trigger_condition', '')
                    score_impact = rule['attributes'].get('score_impact', 0)
                    evaluation_rules_text += f"- {rule_name}: {rule_desc}\n  触发条件: {trigger_condition}\n  分数影响: {score_impact}\n"
                else:
                    rule_name = rule.get('rule_name', '')
                    rule_desc = rule.get('rule_description', '')
                    trigger_condition = rule.get('trigger_condition', '')
                    score_impact = rule.get('score_impact', 0)
                    evaluation_rules_text += f"- {rule_name}: {rule_desc}\n  触发条件: {trigger_condition}\n  分数影响: {score_impact}\n"

        evaluation_prompt_messages = [
            {"role": "system", "content": "你是一个专业的亲子沟通AI，请根据家长和孩子的对话，结合评估规则，分析家长的沟通方式并给出评价。"},
            {"role": "user", "content": f"""
            当前情境名称: {scenario_name}
            情境描述: {scenario_desc}
            孩子的人格特质名称: {personality_name}
            孩子的人格特质描述: {personality_desc}
            
            家长说: "{parent_input}"
            孩子回应: "{child_response}"
            {evaluation_rules_text}
            
            请结合上述评估规则，从以下几个方面进行分析，并以JSON格式返回，不要有其他任何文字：
            1. **grade**: 根据家长的沟通效果，给出A (优秀), B (良好), 或 C (有待改进)的评级。
            2. **score**: 给出一个具体的数字分数，A=10, B=5, C=-5。
            3. **reasonAnalysis**: 简要分析给这个评级的原因，特别说明哪些评估规则被触发。
            4. **suggestionEncouragement**: 给出具体的沟通建议或鼓励的话语。
            5. **parent_mood**: 分析家长的输入情绪，是'positive' (积极), 'neutral' (中性), 还是'negative' (负面)。
            6. **triggered_rules**: 列出被触发的评估规则名称。
            """}
        ]
        
        try:
            llm_response = self._call_qwen_model(evaluation_prompt_messages)
            evaluation_data = json.loads(llm_response)
            
            # 如果没有触发规则字段，添加默认值
            if 'triggered_rules' not in evaluation_data:
                evaluation_data['triggered_rules'] = []
                
            return evaluation_data
        except json.JSONDecodeError as e:
            print(f"ERROR: 大模型返回的JSON格式不正确。错误: {e}. 原始回应: {llm_response}", file=sys.stderr)
            return {
                "grade": "C",
                "score": -5,
                "reasonAnalysis": "AI评价系统出错，无法解析大模型回应。",
                "suggestionEncouragement": "请重试或检查后端日志。",
                "parent_mood": "unknown",
                "triggered_rules": []
            }

    def _generate_expert_guidance(self, dialogue_log, selected_personality):
        """根据完整的对话历史生成专家指导"""
        try:
            personality_name = selected_personality.get('attributes', {}).get('name', '未知人格')
            
            formatted_dialogue = "\n".join([
                f"家长说: \"{d.get('parent_input', '')}\"\n孩子回应: \"{d.get('child_response', '')}\"\n评价: {d.get('evaluation', {}).get('reasonAnalysis', '无评价')}\n触发规则: {d.get('evaluation', {}).get('triggered_rules', [])}"
                for d in dialogue_log
            ])

            # 构建评估规则参考
            evaluation_rules_text = ""
            if self.evaluation_rules:
                evaluation_rules_text = "\n\n评估规则参考：\n"
                for rule in self.evaluation_rules:
                    if 'attributes' in rule:
                        rule_name = rule['attributes'].get('rule_name', '')
                        rule_desc = rule['attributes'].get('rule_description', '')
                        evaluation_rules_text += f"- {rule_name}: {rule_desc}\n"
                    else:
                        rule_name = rule.get('rule_name', '')
                        rule_desc = rule.get('rule_description', '')
                        evaluation_rules_text += f"- {rule_name}: {rule_desc}\n"

            guidance_prompt_messages = [
                {"role": "system", "content": "你是一个专业的亲子沟通专家，请根据以下对话历史和评估规则，给家长提供一份全面而有针对性的指导和鼓励。"},
                {"role": "user", "content": f"""
                以下是家长与扮演'{personality_name}'孩子的AI的对话历史:
                {formatted_dialogue}
                {evaluation_rules_text}

                请结合评估规则，根据以上对话，以JSON格式返回以下内容，不要有其他任何文字：
                1. **guidance**: 给出针对性的沟通建议，指明具体哪里做得好，哪里可以改进，特别关注评估规则的运用。
                2. **encouragement**: 给出对家长的肯定和鼓励。
                3. **totalScore**: 本次对话的总分是多少？
                4. **ruleInsights**: 分析哪些评估规则在对话中被频繁触发或忽略。
                """}
            ]
            
            llm_response = self._call_qwen_model(guidance_prompt_messages)
            if not llm_response:
                raise ValueError("大模型回应为空")
                
            guidance_data = json.loads(llm_response)
            return guidance_data
        except (json.JSONDecodeError, ValueError) as e:
            print(f"ERROR: 专家指导的LLM回应解析失败。错误: {e}. 原始回应: {llm_response}", file=sys.stderr)
            return {
                "guidance": "抱歉，专家指导生成失败，请稍后重试。",
                "encouragement": "你的尝试本身就非常棒，加油！",
                "totalScore": 0,
                "ruleInsights": "无法分析评估规则"
            }
        except Exception as e:
            print(f"ERROR: 生成专家指导失败: {e}", file=sys.stderr)
            return {
                "guidance": "抱歉，生成专家指导时出现错误。",
                "encouragement": "请继续尝试与孩子沟通。",
                "totalScore": 0,
                "ruleInsights": "无法分析评估规则"
            }

    def simulate_dialogue(self, parent_input, personality_id, daily_challenge_theme_id):
        """模拟一轮对话，返回一个元组(response, error)"""
        selected_personality = next((p for p in self.personalities if str(p.get('id')) == str(personality_id)), None)
        selected_challenge = next((c for c in self.daily_challenges if str(c.get('id')) == str(daily_challenge_theme_id)), None)

        if not selected_personality or not selected_challenge:
            return None, "无效的人格或挑战主题ID。"

        selected_scenario = self._find_matching_scenario(selected_challenge)
        if not selected_scenario:
            return None, "无法找到匹配的具体情境。"
        
        child_response = self._generate_child_response_with_qwen(parent_input, selected_personality, selected_scenario)
        if not child_response:
            return None, "大模型生成回应失败。"
        
        evaluation_result = self._evaluate_response(parent_input, child_response, selected_personality, selected_scenario)
        if not evaluation_result:
            return None, "大模型评估失败。"
            
        return jsonify({
            "response": child_response,
            "evaluation": evaluation_result
        }), None

    def _find_matching_scenario(self, challenge):
        """从挑战主题中随机选择一个情境实例"""
        try:
            # 检查是否有Strapi格式的数据结构
            if 'attributes' in challenge and 'dialogue_scenarios' in challenge['attributes']:
                scenarios = challenge['attributes']['dialogue_scenarios']['data']
                if scenarios:
                    return random.choice(scenarios)
            
            # 检查是否有scenario字段（默认数据格式）
            if 'scenario' in challenge and challenge['scenario']:
                return challenge['scenario']
            
            # 如果没有找到情境，创建一个默认情境
            return {
                'id': 1,
                'attributes': {
                    'name': '默认情境',
                    'description': '这是一个默认的情境，用于测试对话功能。'
                }
            }
        except Exception as e:
            print(f"ERROR: 查找匹配情境失败: {e}", file=sys.stderr)
            # 返回默认情境
            return {
                'id': 1,
                'attributes': {
                    'name': '默认情境',
                    'description': '这是一个默认的情境，用于测试对话功能。'
                }
            }

# 路由部分
@app.route('/')
def index():
    """渲染主页"""
    return render_template('index.html')

@app.route('/test')
def test_guidance():
    """测试专家指导功能"""
    return render_template('test_guidance.html')

@app.route('/get_personalities', methods=['GET'])
def get_personalities():
    """获取所有孩子人格"""
    return jsonify(global_strapi_data_cache.get('personalities', []))

@app.route('/get_daily_challenges', methods=['GET'])
def get_daily_challenges():
    """获取所有日常挑战主题"""
    return jsonify(global_strapi_data_cache.get('daily-challenges', []))

@app.route('/simulate_dialogue', methods=['POST'])
def simulate_dialogue_route():
    """处理一轮对话模拟"""
    data = request.get_json()
    parent_input = data.get('parent_input')
    personality_id = data.get('personality_id')
    daily_challenge_theme_id = data.get('daily_challenge_id')
    
    # 增加更详细的参数检查和日志
    if not parent_input:
        print("ERROR: simulate_dialogue request is missing 'parent_input'", file=sys.stderr)
        return jsonify({"error": "缺少必要的对话参数: parent_input。"}), 400
    if not personality_id:
        print("ERROR: simulate_dialogue request is missing 'personality_id'", file=sys.stderr)
        return jsonify({"error": "缺少必要的对话参数: personality_id。"}), 400
    if not daily_challenge_theme_id:
        print("ERROR: simulate_dialogue request is missing 'daily_challenge_id'", file=sys.stderr)
        return jsonify({"error": "缺少必要的对话参数: daily_challenge_id。"}), 400

    simulator = ChildInteractionSimulator(
        global_strapi_data_cache.get('personalities', []),
        global_strapi_data_cache.get('trait-expressions', []),
        global_strapi_data_cache.get('scenario-instances', []),
        global_strapi_data_cache.get('daily-challenges', []),
        global_strapi_data_cache.get('evaluation-rules', [])
    )
    
    result, error = simulator.simulate_dialogue(parent_input, personality_id, daily_challenge_theme_id)
    if error:
        return jsonify({"error": error}), 500
    
    return result

@app.route('/get_expert_guidance', methods=['POST'])
def get_expert_guidance():
    """处理专家指导请求"""
    data = request.get_json()
    dialogue_log = data.get('dialogue_log')
    personality_id = data.get('personality_id')
    
    # 增加更详细的参数检查和日志
    if not dialogue_log:
        print("ERROR: get_expert_guidance request is missing 'dialogue_log'", file=sys.stderr)
        return jsonify({"error": "缺少必要的参数: dialogue_log。"}), 400
    if not personality_id:
        print("ERROR: get_expert_guidance request is missing 'personality_id'", file=sys.stderr)
        return jsonify({"error": "缺少必要的参数: personality_id。"}), 400

    simulator = ChildInteractionSimulator(
        global_strapi_data_cache.get('personalities', []),
        global_strapi_data_cache.get('trait-expressions', []),
        global_strapi_data_cache.get('scenario-instances', []),
        global_strapi_data_cache.get('daily-challenges', []),
        global_strapi_data_cache.get('evaluation-rules', [])
    )

    selected_personality = next((p for p in simulator.personalities if str(p.get('id')) == str(personality_id)), None)
    if not selected_personality:
        return jsonify({"error": "无效的人格ID。"}), 400
        
    guidance = simulator._generate_expert_guidance(dialogue_log, selected_personality)
    
    return jsonify(guidance)


def load_strapi_data():
    """
    加载 Strapi 中的所有数据，并在应用启动时运行
    """
    global global_strapi_data_cache
    
    print("INFO: 正在尝试从 Strapi 加载数据...", file=sys.stderr)
    simulator = ChildInteractionSimulator([], [], [], [], [])
    
    try:
        # 使用 STRAPI_API_URL 变量
        personalities_data = simulator._get_entity_data_from_strapi("personality-traits")
        daily_challenges_data = simulator._get_entity_data_from_strapi("daily-challenges")
        evaluation_rules_data = simulator._get_entity_data_from_strapi("evaluation-rules")

        # 处理人格数据
        if not personalities_data:
            print("WARNING: 无法从Strapi加载人格数据，使用默认数据", file=sys.stderr)
            personalities_data = [
                {
                    'id': 1,
                    'attributes': {
                        'name': '慢能量孩子',
                        'description': '性格内向，反应较慢，需要更多时间思考和回应'
                    }
                },
                {
                    'id': 2,
                    'attributes': {
                        'name': '破能量孩子',
                        'description': '性格外向，反应较快，容易冲动'
                    }
                }
            ]
        
        # 处理挑战数据
        if not daily_challenges_data:
            print("WARNING: 无法从Strapi加载挑战数据，使用默认数据", file=sys.stderr)
            daily_challenges_data = [
                {
                    'id': 1,
                    'attributes': {
                        'name': '学习与成长',
                        'description': '与孩子的学习习惯、作业、考试等相关的挑战'
                    }
                },
                {
                    'id': 2,
                    'attributes': {
                        'name': '情绪管理',
                        'description': '孩子在表达、理解和控制自己情绪方面的挑战'
                    }
                }
            ]
        
        # 处理评估规则数据
        if not evaluation_rules_data:
            print("WARNING: 无法从Strapi加载评估规则数据，使用默认数据", file=sys.stderr)
            evaluation_rules_data = []
        
        # 存储到全局缓存
        global_strapi_data_cache['personalities'] = personalities_data
        global_strapi_data_cache['daily-challenges'] = daily_challenges_data
        global_strapi_data_cache['evaluation-rules'] = evaluation_rules_data
        
        print("INFO: Strapi数据加载完成.", file=sys.stderr)
        print(f"INFO: 加载了 {len(global_strapi_data_cache['personalities'])} 个人格.", file=sys.stderr)
        print(f"INFO: 加载了 {len(global_strapi_data_cache['daily-challenges'])} 个挑战主题.", file=sys.stderr)

    except Exception as e:
        print(f"WARNING: 无法从Strapi加载数据，使用默认数据. 错误: {e}", file=sys.stderr)
        # 如果加载失败，使用默认数据
        global_strapi_data_cache['personalities'] = [
            {
                'id': 1,
                'attributes': {
                    'name': '慢能量孩子',
                    'description': '性格内向，反应较慢，需要更多时间思考和回应'
                }
            },
            {
                'id': 2,
                'attributes': {
                    'name': '破能量孩子',
                    'description': '性格外向，反应较快，容易冲动'
                }
            }
        ]
        global_strapi_data_cache['daily-challenges'] = [
            {
                'id': 1,
                'attributes': {
                    'name': '学习与成长',
                    'description': '与孩子的学习习惯、作业、考试等相关的挑战'
                }
            },
            {
                'id': 2,
                'attributes': {
                    'name': '情绪管理',
                    'description': '孩子在表达、理解和控制自己情绪方面的挑战'
                }
            }
        ]
        global_strapi_data_cache['evaluation-rules'] = []
        print("INFO: 使用默认数据完成初始化.", file=sys.stderr)

# 在应用启动时加载数据
load_strapi_data()

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)






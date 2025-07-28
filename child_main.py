import json
import random
import requests
import uuid
import os
from dotenv import load_dotenv

# 移除不必要的导入，因为我们使用直接的 HTTP 请求
# from api_llm_caller import call_llm_placeholder
# from my_prompts import GENERATE_CHILD_RESPONSE_PROMPT, EVALUATE_CHILD_RESPONSE_PROMPT

# 加载环境变量
load_dotenv()

# --- Strapi 配置 ---
STRAPI_BASE_URL = "http://127.0.0.1:1337"
STRAPI_API_PERSONALITY_PATH = "personality-traits" # 确保与 Strapi Collection Type API ID 一致
STRAPI_API_SCENARIO_PATH = "dialogue-scenarios"

class ChildInteractionSimulator:
    def __init__(self, personality_data, trait_expression_data, scenario_instance_data, daily_challenges_data):
        # 1. 基础验证：确保传入的数据列表存在（可以为空，但不能为None）
        if personality_data is None or trait_expression_data is None or scenario_instance_data is None or daily_challenges_data is None:
            raise ValueError("初始化ChildInteractionSimulator需要完整的人格、特质表现、情境实例和日常挑战数据。")

        # 2. 将从 app.py 接收到的所有数据列表存储为实例变量
        self.personalities = personality_data or []
        self.trait_expressions = trait_expression_data or []
        self.scenario_instances = scenario_instance_data or []
        self.daily_challenges = daily_challenges_data or []
        
        # 3. 打印初始化信息
        print(f"ChildInteractionSimulator initialized with:")
        print(f"  - Personalities: {len(self.personalities)} items")
        print(f"  - Trait expressions: {len(self.trait_expressions)} items")
        print(f"  - Scenario instances: {len(self.scenario_instances)} items")
        print(f"  - Daily challenges: {len(self.daily_challenges)} items")

        # --- 【关键修改】移除所有试图在 __init__ 中直接从列表提取单个属性的代码 ---
        # 您之前可能有的类似如下的行，都应该被删除或注释掉：
        # self.personality_name = self.personality_data.get('attributes', {}).get('name', '未知人格') # 这是上次的错误
        # self.personality_desc = self.personality_data.get('attributes', {}).get('description', '') # 这是当前错误的来源
        # self.key_characteristic = self.personality_data.get('attributes', {}).get('keycharacteristic', [])
        # self.core_need = self.personality_data.get('attributes', {}).get('core_need', '')
        # self.initial_dialogue_starter = self.scenario_instance_data.get('attributes', {}).get('initial_dialogue_starter', '')
        # self.default_trait_expression = self.trait_expression_data.get('attributes', {}).get('default_expression', '')

        # 【在这里初始化您的 LLM 模型，如果它需要通用数据】
        # 例如：self.llm_model = YourActualLLMModel(config_params)
        # 确保您已经导入了 LLM 相关的库
        # self.llm_model = MockLLM() # 这是一个占位符，您需要替换为您的实际LLM初始化

        print("ChildInteractionSimulator initialized with all data lists.")

    def clean_markdown_content(self, content):
        """
        清理 AI 模型输出中的 Markdown 代码块标记
        
        Args:
            content (str): 包含 Markdown 标记的内容
            
        Returns:
            str: 清理后的内容
        """
        if not content:
            return content
            
        # 移除 ```json 和 ``` 标记
        content = content.strip()
        
        # 移除开头的 ```json 或 ``` 标记
        if content.startswith('```json'):
            content = content[7:].strip()
        elif content.startswith('```'):
            content = content[3:].strip()
            
        # 移除结尾的 ``` 标记
        if content.endswith('```'):
            content = content[:-3].strip()
            
        # 移除可能的语言标识符（如 ```python, ```javascript 等）
        lines = content.split('\n')
        if lines and lines[0].startswith('```'):
            lines = lines[1:]
        if lines and lines[-1].startswith('```'):
            lines = lines[:-1]
            
        return '\n'.join(lines).strip()

    def call_qwen_api(self, prompt, model="qwen-turbo", temperature=0.7, max_tokens=1000):
        """
        调用阿里云千问 API
        
        Args:
            prompt (str): 输入提示
            model (str): 模型名称，默认为 qwen-turbo
            temperature (float): 温度参数，控制随机性
            max_tokens (int): 最大输出 token 数
            
        Returns:
            str: API 响应内容
        """
        api_key = os.getenv('ALIYUN_DASHSCOPE_API_KEY')
        if not api_key:
            raise ValueError("未设置 ALIYUN_DASHSCOPE_API_KEY 环境变量")
        
        # 阿里云 DashScope API 端点
        url = "https://dashscope.aliyuncs.com/api/v1/services/aigc/text-generation/generation"
        
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": model,
            "input": {
                "messages": [
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            },
            "parameters": {
                "temperature": temperature,
                "max_tokens": max_tokens,
                "top_p": 0.8,
                "result_format": "message"
            }
        }
        
        try:
            print(f"DEBUG: 正在调用千问 API，模型: {model}")
            response = requests.post(url, headers=headers, json=payload, timeout=30)
            response.raise_for_status()
            
            result = response.json()
            print(f"DEBUG: 千问 API 响应: {result}")
            
            # 提取响应内容
            if 'output' in result and 'choices' in result['output']:
                content = result['output']['choices'][0]['message']['content']
                # 清理 Markdown 标记
                cleaned_content = self.clean_markdown_content(content)
                print(f"DEBUG: 原始 API 响应: {content}")
                print(f"DEBUG: 清理后的内容: {cleaned_content}")
                return cleaned_content
            else:
                raise ValueError(f"千问 API 响应格式异常: {result}")
                
        except requests.exceptions.RequestException as e:
            print(f"ERROR: 调用千问 API 失败: {e}")
            raise
        except Exception as e:
            print(f"ERROR: 处理千问 API 响应失败: {e}")
            raise

    def build_child_response_prompt(self, parent_utterance, personality_data, challenge_data):
        """
        构建生成孩子回应的提示
        
        Args:
            parent_utterance (str): 父级输入
            personality_data (dict): 人格数据
            challenge_data (dict): 挑战数据
            
        Returns:
            str: 构建的提示
        """
        personality_name = personality_data.get('name', '未知人格')
        personality_desc = personality_data.get('description', '无描述')
        key_characteristics = personality_data.get('keycharacteristic', [])
        core_need = personality_data.get('core_need_description', '无')
        
        challenge_name = challenge_data.get('name', '未知挑战')
        challenge_desc = challenge_data.get('description', '无描述')
        
        # 构建特征字符串
        characteristics_str = "、".join(key_characteristics) if key_characteristics else "无特殊特征"
        
        prompt = f"""你是一个{personality_name}的孩子，正在经历{challenge_name}这个挑战。

人格特征：
- 人格名称：{personality_name}
- 人格描述：{personality_desc}
- 关键特征：{characteristics_str}
- 核心需求：{core_need}

当前挑战：
- 挑战名称：{challenge_name}
- 挑战描述：{challenge_desc}

现在，你的父母对你说："{parent_utterance}"

请以{personality_name}的人格特征，在{challenge_name}的挑战下，给出一个自然、真实的回应。回应应该：
1. 符合你的人格特征
2. 反映你的核心需求
3. 在给定挑战下是合理的
4. 语言自然，像真实的孩子说话

请直接给出回应，不要添加任何解释或前缀："""

        return prompt

    def build_evaluation_prompt(self, parent_utterance, child_response, personality_data, challenge_data):
        """
        构建评估父级输入的提示
        
        Args:
            parent_utterance (str): 父级输入
            child_response (str): 孩子回应
            personality_data (dict): 人格数据
            challenge_data (dict): 挑战数据
            
        Returns:
            str: 构建的提示
        """
        personality_name = personality_data.get('name', '未知人格')
        personality_desc = personality_data.get('description', '无描述')
        key_characteristics = personality_data.get('keycharacteristic', [])
        core_need = personality_data.get('core_need_description', '无')
        
        challenge_name = challenge_data.get('name', '未知挑战')
        challenge_desc = challenge_data.get('description', '无描述')
        
        characteristics_str = "、".join(key_characteristics) if key_characteristics else "无特殊特征"
        
        prompt = f"""请严格评估以下亲子沟通的质量。评分标准如下：

【评分标准】
- 90-100分：完美沟通，完全理解孩子需求，表达恰当，给予充分支持
- 80-89分：良好沟通，基本理解孩子需求，表达较恰当
- 70-79分：一般沟通，部分理解孩子需求，表达有待改进
- 60-69分：较差沟通，缺乏对孩子需求的理解，表达不当
- 50-59分：差沟通，忽视孩子需求，表达伤害性
- 40-49分：很差沟通，完全忽视孩子需求，表达极具伤害性
- 30-39分：极差沟通，对孩子造成心理伤害

【扣分项】
- 指责、批评：-15分
- 忽视孩子人格特质：-10分
- 忽视核心需求：-10分
- 命令式语气：-8分
- 缺乏同理心：-8分
- 过度控制：-5分
- 情绪化表达：-5分

孩子人格信息：
- 人格名称：{personality_name}
- 人格描述：{personality_desc}
- 关键特征：{characteristics_str}
- 核心需求：{core_need}

当前挑战：
- 挑战名称：{challenge_name}
- 挑战描述：{challenge_desc}

对话内容：
- 父母说："{parent_utterance}"
- 孩子回应："{child_response}"

请严格按照评分标准进行评估，并以JSON格式返回结果：

{{
    "evaluation_score": 75,
    "reason_analysis": "详细分析父母回应的质量，包括扣分原因和改进建议",
    "parent_input_analysis": {{
        "recognized_trait": "识别到的人格特质",
        "recognized_need": "识别到的核心需求",
        "communication_style": "沟通风格",
        "positive_aspects": ["积极方面1", "积极方面2"],
        "areas_for_improvement": ["需要改进的方面1", "需要改进的方面2"]
    }},
    "child_desired_response": "孩子理想回应的示例",
    "child_desired_response_inner_monologue": "孩子内心独白"
}}

【评估要求】
1. 严格按评分标准打分，不要过于温和
2. 明确指出父母的错误和不足
3. 分析是否理解孩子的人格特质和核心需求
4. 评估沟通方式是否恰当
5. 提供具体的改进建议

请确保返回的是有效的JSON格式："""

        return prompt

    def simulate_dialogue(self, parent_utterance, selected_personality_name, selected_challenge_name):
        # 这个方法接收到选定的人格名称和挑战名称
        # 首先，从存储的列表中查找对应的完整数据对象

        current_personality = next(
            (p for p in self.personalities if p.get('name') == selected_personality_name),
            None
        )
        if not current_personality:
            raise ValueError(f"模拟对话失败: 找不到指定的人格 '{selected_personality_name}'。")

        # 从 daily_challenges 中查找挑战数据
        current_challenge = next(
            (c for c in self.daily_challenges if c.get('name') == selected_challenge_name),
            None
        )
        if not current_challenge:
            raise ValueError(f"模拟对话失败: 找不到指定的挑战 '{selected_challenge_name}'。")

        # 现在，您有了 `current_personality` 和 `current_challenge` 这两个字典，
        # 它们包含了选定人格和挑战的所有详细信息。
        # 您可以从这里安全地访问它们的属性，例如：
        personality_description = current_personality.get('description', '无描述')
        challenge_name = current_challenge.get('name', '无挑战名称')
        # ... 以及其他您需要的人格或挑战属性

        # --- 【在这里集成您的 LLM 模型和模拟逻辑】 ---
        # 以下是模拟输出的占位符，您需要用实际的 LLM 调用和处理逻辑来替换它。
        # 这将是您核心模拟逻辑的地方，需要结合 personality, trait_expressions, scenario_instances,
        # 以及 parent_utterance 和 LLM 来生成 child_response 和评估。

        print(f"DEBUG: 正在模拟对话。父级输入: '{parent_utterance}', 选定人格: '{current_personality.get('name')}', 选定挑战: '{current_challenge.get('name')}'")
        
        try:
            # 1. 构建孩子回应的提示
            child_prompt = self.build_child_response_prompt(parent_utterance, current_personality, current_challenge)
            print(f"DEBUG: 孩子回应提示: {child_prompt}")
            
            # 2. 调用千问 API 生成孩子回应
            child_response = self.call_qwen_api(child_prompt, temperature=0.8, max_tokens=500)
            print(f"DEBUG: 生成的孩子回应: {child_response}")
            
            # 3. 构建评估提示
            evaluation_prompt = self.build_evaluation_prompt(parent_utterance, child_response, current_personality, current_challenge)
            print(f"DEBUG: 评估提示: {evaluation_prompt}")
            
            # 4. 调用千问 API 进行评估
            evaluation_response = self.call_qwen_api(evaluation_prompt, temperature=0.3, max_tokens=800)
            print(f"DEBUG: 评估响应: {evaluation_response}")
            
            # 5. 解析评估结果
            try:
                evaluation_data = json.loads(evaluation_response)
                result = {
                    "child_response": child_response,
                    "evaluation_score": evaluation_data.get("evaluation_score", 75),
                    "reason_analysis": evaluation_data.get("reason_analysis", "评估分析"),
                    "parent_input_analysis": evaluation_data.get("parent_input_analysis", {
                        "recognized_trait": "无",
                        "recognized_need": "无",
                        "communication_style": "未知",
                        "positive_aspects": ["无"],
                        "areas_for_improvement": ["无"]
                    }),
                    "child_desired_response": evaluation_data.get("child_desired_response", "理想回应"),
                    "child_desired_response_inner_monologue": evaluation_data.get("child_desired_response_inner_monologue", "内心独白")
                }
                print(f"DEBUG: 内心独白字段值: {result['child_desired_response_inner_monologue']}")
            except json.JSONDecodeError as e:
                print(f"WARNING: 无法解析评估JSON，使用默认值: {e}")
                # 如果JSON解析失败，使用默认值
                result = {
                    "child_response": child_response,
                    "evaluation_score": 65,
                    "reason_analysis": "父母回应需要改进，缺乏对孩子人格特质和核心需求的深入理解",
                    "parent_input_analysis": {
                        "recognized_trait": current_personality.get('keycharacteristic', ['无'])[0] if current_personality.get('keycharacteristic') else '无',
                        "recognized_need": current_personality.get('core_need_description', '无'),
                        "communication_style": "一般询问式",
                        "positive_aspects": ["尝试沟通"],
                        "areas_for_improvement": ["需要更好地理解孩子的人格特质", "缺乏针对性的回应", "沟通方式需要改进"]
                    },
                    "child_desired_response": "理想回应",
                    "child_desired_response_inner_monologue": f"（内心独白）作为{current_personality.get('name', '孩子')}，我希望父母能更好地理解我的{current_personality.get('core_need_description', '需求')}。"
                }
            
            return result
            
        except Exception as e:
            print(f"ERROR: 调用千问 API 失败，使用模拟响应: {e}")
            # 如果 API 调用失败，返回模拟响应
            mock_response = {
                "child_response": f"（孩子作为'{current_personality.get('name')}'人格，在'{current_challenge.get('name')}'挑战下回应）我听到了你的话，我需要一点时间来思考一下。",
                "evaluation_score": random.randint(50, 75),
                "reason_analysis": "父母回应需要改进，缺乏对孩子人格特质和核心需求的深入理解。沟通方式有待提升。",
                "parent_input_analysis": {
                    "recognized_trait": current_personality.get('keycharacteristic', ['无'])[0] if current_personality.get('keycharacteristic') else '无',
                    "recognized_need": current_personality.get('core_need_description', '无'),
                    "communication_style": "一般询问式，缺乏针对性",
                    "positive_aspects": ["尝试沟通"],
                    "areas_for_improvement": ["需要更好地理解孩子的人格特质", "缺乏针对性的回应", "沟通方式需要改进", "需要更有同理心"]
                },
                "child_desired_response": "（理想回应）谢谢你，妈妈/爸爸，给我点时间，我很快就会告诉你我的想法。",
                "child_desired_response_inner_monologue": f"（内心独白）作为{current_personality.get('name', '孩子')}，我希望父母能更好地理解我的{current_personality.get('core_need_description', '需求')}。"
            }
            print(f"DEBUG: 模拟响应内心独白字段值: {mock_response['child_desired_response_inner_monologue']}")
            return mock_response

    # 您可能需要添加其他辅助方法，例如 _prepare_llm_input 和 _parse_llm_output
    # def _prepare_llm_input(self, parent_utterance, personality_data, challenge_data, trait_expressions):
    #     # 根据数据构建给LLM的提示
    #     pass

    # def _parse_llm_output(self, llm_raw_output):
    #     # 解析LLM的原始输出，提取所需信息
    #     pass

    def to_json(self):
        return json.dumps({
            "session_id": self.session_id,
            "dialogue_history": self.dialogue_history,
            "child_personality": self.child_personality,
            "core_need": self.core_need,
            "current_scenario": self.current_scenario,
        })

    @classmethod
    def from_json(cls, json_str):
        data = json.loads(json_str)
        simulator = cls(
            personality_name=data.get("child_personality", {}).get("name", ""),
            scenario_title=data.get("current_scenario", {}).get("name", ""),
            session_id=data.get("session_id")
        )
        simulator.dialogue_history = data.get("dialogue_history", [])
        simulator.child_personality = data.get("child_personality", {})
        simulator.core_need = data.get("core_need", {})
        simulator.current_scenario = data.get("current_scenario", {})
        return simulator

    def initialize_child_and_scenario(self, personality_name, scenario_title):
        print(f"--- 尝试初始化：人格名称='{personality_name}', 情境标题='{scenario_title}' ---")
        try:
            # --- 人格初始化 ---
            personality_url = f"{STRAPI_BASE_URL}/api/{STRAPI_API_PERSONALITY_PATH}?filters[name][$eq]={personality_name}"
            print(f"DEBUG: 正在请求人格URL: {personality_url}")
            personality_response = requests.get(personality_url)
            print(f"DEBUG: 人格请求状态码: {personality_response.status_code}")
            print(f"DEBUG: 人格请求响应文本: {personality_response.text[:1000]}...")

            personality_response.raise_for_status()
            personality_data = personality_response.json().get('data', [])

            if personality_data:
                self.child_personality = personality_data[0] # 直接使用这个字典
                self.core_need = {"description": self.child_personality.get('core_need_description', '无核心需求')}

                print(f"--- 孩子人格初始化成功: {self.child_personality.get('name')} ---")
                print(f"DEBUG: 孩子人格详细数据（部分）: {json.dumps(self.child_personality, indent=2)[:1000]}...")
                print(f"DEBUG: 孩子核心需求: {self.core_need}")
            else:
                print(f"!!! 警告: 未找到指定的人格: '{personality_name}' (Strapi返回数据为空或不存在) !!!")
                self.child_personality = {"name": "默认孩子", "description": "无描述"}
                self.core_need = {"description": "无核心需求"}

            # --- 情境初始化 ---
            scenario_url = f"{STRAPI_BASE_URL}/api/{STRAPI_API_SCENARIO_PATH}?filters[name][$eq]={scenario_title}"
            print(f"DEBUG: 正在请求情境URL: {scenario_url}")
            scenario_response = requests.get(scenario_url)
            print(f"DEBUG: 情境请求状态码: {scenario_response.status_code}")
            print(f"DEBUG: 情境请求响应文本: {scenario_response.text[:1000]}...")

            scenario_response.raise_for_status()
            scenario_data = scenario_response.json().get('data', [])

            if scenario_data:
                self.current_scenario = scenario_data[0] # 直接使用这个字典
                print(f"--- 情境初始化成功: {self.current_scenario.get('name')} ---")
                print(f"DEBUG: 情境详细数据（部分）: {json.dumps(self.current_scenario, indent=2)[:1000]}...")
            else:
                print(f"!!! 警告: 未找到指定的情境: '{scenario_title}' (Strapi返回数据为空或不存在) !!!")
                self.current_scenario = {"name": "默认情境", "description": "无描述"}

        except requests.exceptions.ConnectionError as e:
            print(f"!!! 错误: 无法连接到Strapi服务器！请检查Strapi是否运行，地址是否正确: {e} !!!")
            self.child_personality = {"name": "默认孩子", "description": "无描述"}
            self.core_need = {"description": "无核心需求"}
            self.current_scenario = {"name": "默认情境", "description": "无描述"}
        except requests.exceptions.HTTPError as e:
            print(f"!!! 错误: 从Strapi获取数据时遇到HTTP错误: {e.response.status_code} - {e.response.text} !!!")
            self.child_personality = {"name": "默认孩子", "description": "无描述"}
            self.core_need = {"description": "无核心需求"}
            self.current_scenario = {"name": "默认情境", "description": "无描述"}
        except json.JSONDecodeError as e:
            print(f"!!! 错误: 解析Strapi响应为JSON失败: {e} !!!")
            problematic_text = "N/A"
            if 'personality_response' in locals():
                problematic_text = personality_response.text[:1000]
            elif 'scenario_response' in locals():
                problematic_text = scenario_response.text[:1000]
            print(f"DEBUG: 导致JSON解析错误的文本: {problematic_text}...")
            self.child_personality = {"name": "默认孩子", "description": "无描述"}
            self.core_need = {"description": "无核心需求"}
            self.current_scenario = {"name": "默认情境", "description": "无描述"}
        except Exception as e:
            print(f"!!! 发生未知错误: {e} !!!")
            self.child_personality = {"name": "默认孩子", "description": "无描述"}
            self.core_need = {"description": "无核心需求"}
            self.current_scenario = {"name": "默认情境", "description": "无描述"}

    def _build_llm_prompt(self, parent_input):
        # 将列表形式的特征拼接成字符串，方便LLM理解
        personality_key_chars_str = "\n- " + "\n- ".join(self.personality_key_chars) if self.personality_key_chars else "无"
        child_behaviors_str = ", ".join(self.child_typical_behavior) if self.child_typical_behavior else "无"
        parent_emotions_str = ", ".join(self.parent_typical_emotion) if self.parent_typical_emotion else "无"
        root_causes_str = ", ".join(self.potential_root_causes) if self.potential_root_causes else "无"

        # 预设回应匹配
        matched_preset_response = None
        matched_follow_up_hint = None
        parent_input_lower = parent_input.lower()
        for preset_map in self.parent_inputs_map:
            keywords = preset_map.get('parent_keywords', [])
            child_resp_template = preset_map.get('child_response_template')
            follow_up_hint = preset_map.get('follow_up_prompt_hint')
            if any(keyword.lower() in parent_input_lower for keyword in keywords):
                matched_preset_response = child_resp_template
                matched_follow_up_hint = follow_up_hint
                break

        if matched_preset_response:
            prompt_parts = [
                f"你是一个模拟孩子，你的名字是【{self.personality_name}】。",
                f"家长对你说：“{parent_input}”",
                f"根据预设，你应该回复：“{matched_preset_response}”",
                f"请你以【{self.personality_name}】的性格特点回复家长，注意保持预设内容不变，但可以稍微调整语气使其更自然。",
                f"你的性格特点：{self.personality_desc}",
                f"核心需求：{self.personality_core_need}",
                f"关键行为模式：{personality_key_chars_str}",
                f"当前具体情境名称：{self.scenario_name}",
                f"情境描述：{self.scenario_desc}",
                f"孩子典型表现：{child_behaviors_str}",
                f"家长可能情绪：{parent_emotions_str}",
                f"可能根本原因：{root_causes_str}",
            ]
            if matched_follow_up_hint:
                prompt_parts.append(f"请特别注意后续对话的微调提示：{matched_follow_up_hint}")
            return "\n".join(prompt_parts)
        else:
            prompt = f"""
            你是一个模拟孩子。
            你的性格特征是：{self.personality_desc}
            你的核心需求是：{self.personality_core_need}
            你的关键行为模式包括：
            {personality_key_chars_str}

            当前情境是：“{self.scenario_name}”
            情境描述：{self.scenario_desc}
            在这个情境下，孩子通常的表现是：{child_behaviors_str}
            家长此刻可能感到：{parent_emotions_str}
            可能的根本原因包括：{root_causes_str}

            请你作为【{self.personality_name}】这个孩子，结合你的性格特征、核心需求和当前情境的详细信息，以及以下通用指导，给出自然、真实的回复。回复要符合孩子的年龄特点和情绪状态。
            
            通用回复指导：{self.general_response_guidance}

            家长对你说：“{parent_input}”

            你的回复：
            """
            return prompt

    def _call_llm(self, prompt_type: str, prompt_content: str):
        return call_llm_placeholder(prompt_type, prompt_content)

    def _get_formatted_dialogue_history(self) -> str:
        if not self.dialogue_history:
            return "无"
        return "\n".join([f"{'家长' if entry['role']=='parent' else '孩子'}: {entry['content']}" for entry in self.dialogue_history])

    # 删除 _generate_evaluation_prompt 方法，无需保留任何内容

    def run_simulation(self):
        print("欢迎来到模拟儿童对话模拟器！\n")
        print("人格画像：\n", self.child_personality.strip())
        print("场景描述：\n", self.current_scenario.strip())
        print("核心需求：\n", self.core_need.strip())
        print("\n请输入您对孩子说的话（输入 '退出' 可结束对话）")

        while True:
            parent_utterance = input("\n您对孩子说：")
            if parent_utterance.lower() == "退出":
                print("模拟对话结束。")
                break

            # 步骤 1：生成孩子回应
            prompt = GENERATE_CHILD_RESPONSE_PROMPT.format(
                child_personality_profile=self.child_personality,
                scenario_description=self.current_scenario,
                dialogue_history=self._get_formatted_dialogue_history(),
                parent_utterance=parent_utterance
            )
            child_response = self._call_llm("CHILD_RESPONSE", prompt)
            if not child_response:
                print("⚠️ 无法生成孩子回应。")
                continue
            print(f"\n孩子回应：{child_response}")
            self.dialogue_history += [
                {"role": "parent", "content": parent_utterance},
                {"role": "child", "content": child_response}
            ]

            # 步骤 2：生成回应评价
            eval_prompt = EVALUATE_CHILD_RESPONSE_PROMPT.format(
                child_personality_profile=self.child_personality,
                scenario_description=self.current_scenario,
                parent_utterance=parent_utterance,
                child_response=child_response
            )
            eval_json_str = self._call_llm("EVALUATION", eval_prompt)
            if not eval_json_str:
                print("⚠️ 无法生成回应评价。")
                continue

            try:
                evaluation = json.loads(eval_json_str)
                print("\n--- 回应评价 ---")
                print(f"综合评价：{evaluation.get('Evaluation')}")
                print(f"原因分析：{evaluation.get('ReasonAnalysis')}")

                if evaluation.get("Evaluation", "").upper() != "A":
                    self.non_a_eval_count += 1
                    if self.non_a_eval_count >= 3:
                        print("\n💡 连续三轮非A回应，孩子心声如下：")
                        print(f"理想回应：{evaluation.get('ChildDesiredResponse')}")
                        print(f"内心独白：{evaluation.get('ChildDesiredResponseInnerMonologue')}")
                        self.non_a_eval_count = 0
                else:
                    self.non_a_eval_count = 0

            except json.JSONDecodeError:
                print("⚠️ 返回数据不是有效的 JSON 格式：", eval_json_str)

    def get_child_response(self, parent_input):
        print(f"DEBUG (child_main): Parent input received: {parent_input}")
        prompt = self._build_llm_prompt(parent_input)
        print(f"DEBUG (child_main): LLM Prompt:\n{prompt}")
        try:
            if "根据预设，你应该回复：" in prompt:
                start_idx = prompt.find("根据预设，你应该回复：") + len("根据预设，你应该回复：") + 1
                end_idx = prompt.find("”", start_idx)
                if start_idx != -1 and end_idx != -1:
                    child_response = prompt[start_idx:end_idx] + "（预设回复）"
                else:
                    child_response = "（未能提取预设回复，请检查Prompt）"
            else:
                child_response = "（未触发预设，LLM将自由回复）"
            print(f"DEBUG (child_main): Child response: {child_response}")
            return child_response
        except Exception as e:
            print(f"ERROR (child_main): 调用LLM失败: {e}")
            return f"孩子暂时无法回应，请稍后再试。（LLM错误：{e}）"

def get_all_evaluation_rules_from_strapi():
    """
    从 Strapi 拉取所有评估规则，返回规则列表。
    """
    import requests
    STRAPI_BASE_URL = "http://localhost:1337"
    STRAPI_API_PATH = "responses"
    try:
        response = requests.get(f"{STRAPI_BASE_URL}/api/{STRAPI_API_PATH}?populate=*")
        response.raise_for_status()
        data = response.json()
        rules = []
        for item in data.get('data', []):
            attrs = item.get('attributes', {})
            # 解析 parentKeywords 字段为列表
            if 'parentKeywords' in attrs and isinstance(attrs['parentKeywords'], str):
                import json
                try:
                    attrs['parentKeywords'] = json.loads(attrs['parentKeywords'])
                except Exception:
                    attrs['parentKeywords'] = []
            rules.append(attrs)
        return rules
    except Exception as e:
        print(f"[get_all_evaluation_rules_from_strapi] 拉取评估规则失败: {e}")
        return []

# 程序入口
# if __name__ == "__main__":
#     try:
#         simulator = ChildInteractionSimulator(
#             personality_name="慢能量孩子",
#             scenario_title="沉浸在自己世界"
#         )
#         simulator.run_simulation()
#     except Exception as e:
#         print(f"\n❌ 启动模拟器失败：{e}")


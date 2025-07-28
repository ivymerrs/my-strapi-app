# api_llm_caller.py


import os
import json
from dashscope import Generation # 导入 DashScope SDK

# 从环境变量获取阿里云 DashScope API Key
# 强烈建议将 API Key 设置为环境变量，不要直接写在代码中
# 例如：export DASHSCOPE_API_KEY="sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
DASHSCOPE_API_KEY = os.getenv("DASHSCOPE_API_KEY")
if not DASHSCOPE_API_KEY:
    print("错误：未设置 DASHSCOPE_API_KEY 环境变量。请在运行前设置。")
    # 为了测试方便，这里也可以设置一个默认值，但在生产环境中不推荐
    # DASHSCOPE_API_KEY = "YOUR_DASHSCOPE_API_KEY_HERE"

# 定义要使用的模型名称
# Qwen/qwen-turbo 适用于轻量级和快速响应
# Qwen/qwen-plus 适用于更强大的能力
# Qwen/qwen-max 适用于最强能力（可能费用更高）
DASHSCOPE_MODEL_NAME = os.getenv("DASHSCOPE_MODEL_NAME", "qwen-turbo") # 默认使用 qwen-turbo

def call_dashscope_llm(system_prompt: str, user_prompt: str, model_name: str = DASHSCOPE_MODEL_NAME):
    """
    调用阿里云 DashScope LLM 服务生成文本。
    system_prompt: 系统的角色设定或指导。
    user_prompt: 用户的输入或主要指令。
    model_name: 要使用的模型名称。
    """
    if not DASHSCOPE_API_KEY:
        print("错误：DASHSCOPE_API_KEY 未设置，无法调用 DashScope API。")
        return None

    try:
        # 构建 messages 列表，使用字典格式
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
        print(f"准备调用 DashScope，system_prompt: {system_prompt}, user_prompt: {user_prompt}")
        response = Generation.call(
            model=model_name,
            messages=messages,
            api_key=DASHSCOPE_API_KEY,
            result_format='message'
        )
        print(f"DashScope 返回: {response}")
        if response.status_code == 200 and response.output and response.output.choices:
            # 兼容字典格式的返回
            return response.output.choices[0]['message']['content'].strip()
        else:
            print(f"警告: DashScope 响应结果不成功或格式不符。状态码: {response.status_code}, 错误信息: {getattr(response, 'message', None)}, 完整响应: {response}")
            return None
    except Exception as e:
        print(f"调用 DashScope LLM 发生异常: {e}")
        return None

# 为了兼容 child_main.py 中的 call_llm_placeholder 命名
def call_llm_placeholder(prompt_type: str, prompt_content: str):
    """
    兼容原有的 call_llm_placeholder 接口，实际调用 DashScope 模型。
    我们将 prompt_content 作为一个整体的 user_prompt 传入。
    针对不同的 prompt_type，设置不同的 system_prompt。
    """
    if prompt_type == "CHILD_RESPONSE":
        system_prompt = "你是一个正在模拟特定儿童人格的AI助手，你的任务是根据给定的儿童人格特点、当前场景和对话历史，以该儿童的口吻，生成一句自然的回应。回应必须符合儿童的年龄和认知水平，并体现其独特的人格特征。在回应中不要添加任何解释性文字或括号内的备注（例如“轻轻点头”），只给出孩子会说或会做的话。语言要儿童化，自然，不生硬。"
    elif prompt_type == "EVALUATION":
        # 评估 Prompt 对格式要求严格，所以 system_prompt 要强调
        system_prompt = "你是一个专业的儿童心理和行为评估专家。你的任务是根据一个模拟儿童的人格画像、其核心需求、当前情境，以及一段家长与孩子的对话，对模拟孩子的表现进行客观、深入的评估。同时，更重要的是，你需要为家长提供积极的反馈和具体的、可操作的改进建议。你的回应必须严格遵循指定的 JSON 格式，不包含任何额外文本或Markdown代码块。"
    else:
        system_prompt = "你是一个通用的AI助手。"

    print(f"--- DEBUGGING LLM CALLER: Function '{prompt_type}' entered ---")
    print(f"--- DEBUGGING LLM CALLER: API Key is {'Set' if DASHSCOPE_API_KEY else 'NOT Set'} ---")
    # 直接调用 call_dashscope_llm，避免 messages 未定义错误
    return call_dashscope_llm(system_prompt, prompt_content)

if __name__ == '__main__':
    # 确保您在运行此测试之前设置了环境变量 DASHSCOPE_API_KEY
    # export DASHSCOPE_API_KEY="sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
    print("测试 DashScope LLM API...")
    test_system_prompt = "你是一个有帮助的AI助手。"
    test_user_prompt = "你好，请简单介绍一下你自己。"
    response_content = call_dashscope_llm(test_system_prompt, test_user_prompt)
    if response_content:
        print(f"DashScope 回应: {response_content}")
    else:
        print("未收到 DashScope 回应。")
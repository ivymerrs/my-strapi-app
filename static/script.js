document.addEventListener('DOMContentLoaded', () => {
    // 获取新的 HTML 元素
    const parentInput = document.getElementById('parent-input');
    const simulateBtn = document.getElementById('simulate-btn');
    const spinner = document.getElementById('spinner');
    const childResponse = document.getElementById('child-response');
    const evaluationResult = document.getElementById('evaluation-result');
    const rawOutputPre = document.getElementById('raw-output-pre');
    const rawOutputContainer = document.getElementById('raw-llm-output-container');

    // 新增：下拉框元素
    const personalitySelect = document.getElementById('personality-select');
    const dailyChallengeSelect = document.getElementById('daily-challenge-select'); // 修改 ID

    // 移除不再需要的元素引用，因为新的 HTML 结构更简化

    // API Endpoint (确保 Flask 服务器正在运行在 5000 端口)
    const API_URL = '/simulate_dialogue';

    // 新增：加载人格列表
    fetch('/get_personalities')
        .then(response => response.json())
        .then(personalities => {
            console.log("DEBUG (Frontend): 接收到的人格原始数据:", personalities); // 保留调试信息

            // 修正这里：确保从每个对象中提取 'name' 字段
            personalities.forEach(p => { // p 现在是 {'id': ..., 'name': '...'} 对象
                const option = document.createElement('option');
                option.value = p.id; // value 使用 ID，发送给后端
                option.textContent = p.name; // textContent 显示 name
                personalitySelect.appendChild(option);
            });
            // 默认选中第一个（如果有数据的话）
            if (personalities.length > 0) {
                personalitySelect.value = personalities[0].id; // 默认选中第一个的ID
            }
        })
        .catch(error => console.error('Error loading personalities:', error));

    // 加载大类挑战列表
    fetch('/get_daily_challenges') // 修改请求路由
        .then(response => response.json())
        .then(data => {
            console.log("DEBUG (Frontend): 接收到的挑战原始数据:", data); // 保留调试信息
            data.forEach(c => {
                const option = document.createElement('option');
                option.value = c.id; // value 使用 ID，发送给后端
                option.textContent = c.name; // textContent 显示 name
                dailyChallengeSelect.appendChild(option); // 修改 ID
            });
            // 默认选中第一个（如果有数据的话）
            if (data.length > 0) {
                dailyChallengeSelect.value = data[0].id;
            }
        })
        .catch(error => console.error('Error loading daily challenges:', error));

    // 简化的渲染函数
    const renderResults = (childResponseText, evaluationData) => {
        // 显示孩子回应
        childResponse.textContent = `孩子回应: ${childResponseText}`;
        
        // 调试信息
        console.log("DEBUG: evaluationData:", evaluationData);
        console.log("DEBUG: child_desired_response_inner_monologue:", evaluationData?.child_desired_response_inner_monologue);
        
        // 显示评估结果
        if (evaluationData && evaluationData.evaluation_score) {
            const score = evaluationData.evaluation_score;
            const reason = evaluationData.reason_analysis || '无详细分析';
            const innerMonologue = evaluationData.child_desired_response_inner_monologue || '无内心独白';
            
            console.log("DEBUG: innerMonologue value:", innerMonologue);
            
            // 提取父级输入分析信息
            const parentAnalysis = evaluationData.parent_input_analysis || {};
            const recognizedTrait = parentAnalysis.recognized_trait || '未识别';
            const recognizedNeed = parentAnalysis.recognized_need || '未识别';
            const communicationStyle = parentAnalysis.communication_style || '未分析';
            const positiveAspects = parentAnalysis.positive_aspects || [];
            const areasForImprovement = parentAnalysis.areas_for_improvement || [];
            
            evaluationResult.innerHTML = `
                <div class="evaluation-section">
                    <h3>沟通评估</h3>
                    <p><strong>评价得分:</strong> ${score}</p>
                    <p><strong>分析理由:</strong> ${reason}</p>
                </div>
                
                <div class="parent-analysis-section">
                    <h3>父级输入分析</h3>
                    <p><strong>识别到的人格特质:</strong> ${recognizedTrait}</p>
                    <p><strong>识别到的核心需求:</strong> ${recognizedNeed}</p>
                    <p><strong>沟通风格:</strong> ${communicationStyle}</p>
                </div>
                
                <div class="positive-aspects-section">
                    <h3>积极方面</h3>
                    ${positiveAspects.length > 0 ? 
                        `<ul>${positiveAspects.map(aspect => `<li>${aspect}</li>`).join('')}</ul>` : 
                        '<p>无特别突出的积极方面</p>'
                    }
                </div>
                
                <div class="improvement-section">
                    <h3>需要改进的方面</h3>
                    ${areasForImprovement.length > 0 ? 
                        `<ul>${areasForImprovement.map(area => `<li>${area}</li>`).join('')}</ul>` : 
                        '<p>无特别需要改进的方面</p>'
                    }
                </div>
                
                <div class="inner-monologue-section">
                    <h3>孩子内心独白</h3>
                    <p>${innerMonologue}</p>
                </div>
            `;
        } else {
            evaluationResult.textContent = '评价: 暂无评估数据';
        }
    };

    simulateBtn.addEventListener('click', async () => {
        const parentUtterance = parentInput.value.trim();
        if (!parentUtterance) {
            alert('请输入您想对孩子说的话。');
            return;
        }

        // 获取当前选择的人格和大主题挑战的 ID
        const selectedPersonalityId = personalitySelect ? personalitySelect.value : '';
        const selectedDailyChallengeId = dailyChallengeSelect ? dailyChallengeSelect.value : '';

        // 显示加载动画
        spinner.style.display = 'block';
        rawOutputContainer.style.display = 'none'; // Hide raw output initially
        
        try {
            const response = await fetch(API_URL, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ 
                    parent_utterance: parentUtterance,
                    // 将发送的参数改为 ID
                    personality_id: selectedPersonalityId, // 修改为 personality_id
                    daily_challenge_id: selectedDailyChallengeId // 修改为 daily_challenge_id
                })
            });

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.error || `HTTP 错误！状态码: ${response.status}`);
            }

            const data = await response.json();
            console.log("API Response:", data); // Log the full response for debugging

            // 精确提取孩子回应
            const childResponseText = data.child_response || '未收到孩子回应。';

            // 精确提取评估信息 - 后端返回的是扁平结构，不是嵌套的 evaluation 对象
            const evaluation = {
                evaluation_score: data.evaluation_score,
                reason_analysis: data.reason_analysis,
                parent_input_analysis: data.parent_input_analysis,
                child_desired_response_inner_monologue: data.child_desired_response_inner_monologue
            };
            
            // 调试信息
            console.log("DEBUG: 原始数据:", data);
            console.log("DEBUG: 提取的评估数据:", evaluation);
            console.log("DEBUG: 内心独白原始值:", data.child_desired_response_inner_monologue);

            // 渲染结果
            renderResults(childResponseText, evaluation);

            // Display raw JSON response for debugging
            rawOutputPre.textContent = JSON.stringify(data, null, 2);
            rawOutputContainer.style.display = 'block';

            parentInput.value = ''; // Clear input field
        } catch (error) {
            console.error("发送请求失败:", error);
            alert(`发生错误: ${error.message || '未知错误'}`);
        } finally {
            spinner.style.display = 'none';
        }
    });
});

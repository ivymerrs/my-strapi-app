// my-project/static/script.js

document.addEventListener('DOMContentLoaded', function() {
    // UI 元素
    const initialSetupScreen = document.querySelector('.initial-setup');
    const startBtn = document.getElementById('start-btn');
    const personalitySelect = document.getElementById('personality-select');
    const challengeSelect = document.getElementById('daily-challenge-select');
    
    const chatContainer = document.querySelector('.chat-container');
    const chatBox = document.getElementById('chat-box');
    const parentInput = document.getElementById('parent-input');
    const sendBtn = document.getElementById('send-btn');
    const guidanceBtn = document.getElementById('guidance-btn');
    const totalScoreSpan = document.getElementById('total-score');
    
    // 增加防御性检查：如果核心元素不存在，打印错误并停止脚本
    if (!initialSetupScreen || !startBtn || !personalitySelect || !challengeSelect || !chatContainer || !chatBox || !parentInput || !sendBtn || !guidanceBtn || !totalScoreSpan) {
        console.error('ERROR: 缺少必要的UI元素。请确保您的templates/index.html文件是最新版本，它包含了所有必需的ID。');
        return; // 中断脚本执行
    }
    
    const guidanceModal = document.getElementById('guidance-modal');
    // 在获取子元素之前，先检查模态框元素是否存在
    let guidanceContent = null;
    if (guidanceModal) {
        guidanceContent = guidanceModal.querySelector('.guidance-content');
        if (!guidanceContent) {
            console.error('ERROR: 找不到 .guidance-content 元素。专家指导功能将无法使用。');
        }
    } else {
        console.error('ERROR: 找不到 #guidance-modal 元素。专家指导功能将无法使用。请确保您的templates/index.html文件是最新版本。');
    }

    // 游戏状态
    let dialogueLog = []; // 存储所有对话的完整历史
    let totalScore = 0;
    let consecutiveNegativeCount = 0;
    let isDialogueActive = false;

    // 事件监听器
    startBtn.addEventListener('click', startDialogue);
    sendBtn.addEventListener('click', handleParentInput);
    if (guidanceBtn) { // 确保元素存在再添加监听器
        guidanceBtn.addEventListener('click', handleGuidanceRequest);
    }
    
    parentInput.addEventListener('keydown', (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            if (isDialogueActive) {
                handleParentInput();
            }
        }
    });

    // 初始化加载人格和挑战主题
    populatePersonalities();
    populateDailyChallenges();

    // 辅助函数
    function addMessageToChat(sender, text, score=null) {
        const messageDiv = document.createElement('div');
        messageDiv.classList.add('message', sender === 'parent' ? 'parent-message' : 'child-message');

        const messageContentDiv = document.createElement('div');
        messageContentDiv.classList.add('message-content');
        
        const bubbleDiv = document.createElement('div');
        bubbleDiv.classList.add('bubble');
        bubbleDiv.innerHTML = text; // 使用 innerHTML 支持换行符
        
        if (sender === 'child' && score !== null) {
            // 如果是孩子回应，并且有分数，把分数标签放在气泡左侧
            const scoreTag = document.createElement('span');
            scoreTag.classList.add('score-tag');
            scoreTag.textContent = `${score > 0 ? '+' : ''}${score}`;
            scoreTag.classList.add(`score-${score > 0 ? (score >= 8 ? 'a' : 'b') : 'c'}`);
            messageContentDiv.appendChild(scoreTag);
        }
        
        messageContentDiv.appendChild(bubbleDiv);
        
        messageDiv.appendChild(messageContentDiv);

        chatBox.appendChild(messageDiv);
        chatBox.scrollTop = chatBox.scrollHeight; // 滚动到底部
    }

    function addLoadingMessage() {
        const loadingDiv = document.createElement('div');
        loadingDiv.classList.add('loading-message');
        loadingDiv.id = 'loading-message';
        loadingDiv.textContent = '孩子正在思考...';
        chatBox.appendChild(loadingDiv);
        chatBox.scrollTop = chatBox.scrollHeight;
    }

    function removeLoadingMessage() {
        const loadingDiv = document.getElementById('loading-message');
        if (loadingDiv) {
            loadingDiv.remove();
        }
    }

    // 核心逻辑函数
    function startDialogue() {
        const personality_id = personalitySelect.value;
        const daily_challenge_id = challengeSelect.value;
        
        if (!initialSetupScreen) {
            console.error('DEBUG: initialSetupScreen 元素不存在');
            return;
        }

        if (!personality_id || !daily_challenge_id) {
            alert('请选择人格和挑战主题！');
            return;
        }

        // 隐藏初始设置，显示聊天框
        initialSetupScreen.style.display = 'none';
        chatContainer.style.display = 'flex';
        guidanceBtn.style.display = 'inline-block';
        isDialogueActive = true;

        // 欢迎语
        addMessageToChat('child', '你好，爸爸/妈妈，准备好和我对话了吗？');
    }

    async function populatePersonalities() {
        try {
            const response = await fetch('/get_personalities');
            const data = await response.json();
            console.log("DEBUG: 接收到的人格数据:", data);

            personalitySelect.innerHTML = '<option value="">选择人格</option>';
            data.forEach(p => {
                const option = document.createElement('option');
                option.value = p.id;
                // 处理不同的数据格式
                if (p.attributes && p.attributes.name) {
                    option.textContent = p.attributes.name;
                } else if (p.name) {
                    option.textContent = p.name;
                } else {
                    console.warn('无法获取人格名称:', p);
                    return;
                }
                personalitySelect.appendChild(option);
                console.log(`DEBUG: 添加人格选项: ${option.textContent} (值: ${option.value})`);
            });
            console.log("DEBUG: 人格数据加载完成，选项数量:", personalitySelect.options.length);
        } catch (error) {
            console.error('获取人格失败:', error);
        }
    }

    async function populateDailyChallenges() {
        try {
            const response = await fetch('/get_daily_challenges');
            const data = await response.json();
            console.log("DEBUG: 接收到的挑战主题数据:", data);

            challengeSelect.innerHTML = '<option value="">选择挑战主题</option>';
            data.forEach(challenge => {
                const option = document.createElement('option');
                option.value = challenge.id;
                // 处理不同的数据格式
                if (challenge.attributes && challenge.attributes.name) {
                    option.textContent = challenge.attributes.name;
                } else if (challenge.name) {
                    option.textContent = challenge.name;
                } else {
                    console.warn('无法获取挑战主题名称:', challenge);
                    return;
                }
                challengeSelect.appendChild(option);
                console.log(`DEBUG: 添加挑战主题选项: ${option.textContent} (值: ${option.value})`);
            });
            console.log("DEBUG: 挑战主题数据加载完成，选项数量:", challengeSelect.options.length);
        } catch (error) {
            console.error('获取日常挑战主题失败:', error);
        }
    }

    async function handleParentInput() {
        const parent_input = parentInput.value.trim();
        const personality_id = personalitySelect.value;
        const daily_challenge_id = challengeSelect.value;

        if (!parent_input) return;

        addMessageToChat('parent', parent_input);
        
        parentInput.value = '';
        addLoadingMessage();
        parentInput.disabled = true;
        sendBtn.disabled = true;
        guidanceBtn.disabled = true;

        try {
            const response = await fetch('/simulate_dialogue', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    parent_input: parent_input,
                    personality_id: personality_id,
                    daily_challenge_id: daily_challenge_id
                })
            });

            const data = await response.json();
            
            removeLoadingMessage();
            parentInput.disabled = false;
            sendBtn.disabled = false;
            guidanceBtn.disabled = false;

            if (response.ok) {
                console.log("DEBUG: 收到对话响应:", data);
                
                // 检查响应数据结构
                const childResponse = data.child_response || data.response;
                const evaluation = data.evaluation || {};
                const score = evaluation.score || evaluation.evaluation_score || 0;
                
                addMessageToChat('child', childResponse, score);
                
                totalScore += score;
                totalScoreSpan.textContent = `总分: ${totalScore}`;
                dialogueLog.push({
                    parent_input: parent_input,
                    child_response: childResponse,
                    evaluation: evaluation
                });
            } else {
                console.error("DEBUG: API错误:", data);
                addMessageToChat('child', '系统错误: ' + (data.error || '未知错误'));
            }
        } catch (error) {
            console.error('模拟对话请求失败:', error);
            removeLoadingMessage();
            parentInput.disabled = false;
            sendBtn.disabled = false;
            guidanceBtn.disabled = false;
            addMessageToChat('child', '错误: 请求失败，请检查网络。');
        }
    }

    async function handleGuidanceRequest() {
        if (!isDialogueActive || dialogueLog.length === 0) {
            alert('请先进行对话！');
            return;
        }

        // 在调用前再次检查模态框元素是否存在
        if (!guidanceModal) {
            console.error('ERROR: 专家指导模态框元素不存在。请确保您的templates/index.html文件是最新版本。');
            alert('专家指导功能不可用：模态框元素不存在。请刷新页面重试。');
            return;
        }
        
        if (!guidanceContent) {
            console.error('ERROR: 专家指导内容元素不存在。请确保您的templates/index.html文件是最新版本。');
            alert('专家指导功能不可用：内容元素不存在。请刷新页面重试。');
            return;
        }

        parentInput.disabled = true;
        sendBtn.disabled = true;
        guidanceBtn.disabled = true;
        addLoadingMessage();

        try {
            const response = await fetch('/get_expert_guidance', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    dialogue_log: dialogueLog,
                    personality_id: personalitySelect.value
                })
            });

            const data = await response.json();
            removeLoadingMessage();
            
            if (response.ok) {
                showGuidanceModal(data);
                isDialogueActive = false;
            } else {
                alert('获取专家指导失败：' + (data.error || '未知错误'));
                parentInput.disabled = false;
                sendBtn.disabled = false;
                guidanceBtn.disabled = false;
            }
        } catch (error) {
            console.error('获取专家指导请求失败:', error);
            removeLoadingMessage();
            alert('获取专家指导失败，请检查网络。');
            parentInput.disabled = false;
            sendBtn.disabled = false;
            guidanceBtn.disabled = false;
        }
    }
    
    function showGuidanceModal(data) {
        const html = `
            <h3>对话总结与专家指导</h3>
            <p><strong>本次对话总分:</strong> <span style="font-size: 1.2rem; font-weight: bold;">${totalScore}</span></p>
            <p><strong>指导建议:</strong><br>${data.guidance}</p>
            <p><strong>鼓励与肯定:</strong><br>${data.encouragement}</p>
            <button onclick="window.location.reload()">重新开始</button>
        `;
        guidanceContent.innerHTML = html;
        guidanceModal.style.display = 'flex';
    }

    if (guidanceModal) { // 确保模态框存在
        guidanceModal.addEventListener('click', (e) => {
            if (e.target === guidanceModal) {
                guidanceModal.style.display = 'none';
            }
        });
    }
});

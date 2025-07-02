// 导航栏隐藏/显示逻辑
let lastScroll = 0;
const navbar = document.getElementById('navbar');

window.addEventListener('scroll', () => {
  const currentScroll = window.pageYOffset;
  if (currentScroll > lastScroll) {
    navbar.style.top = '-80px'; // 向下滚动隐藏
  } else {
    navbar.style.top = '0'; // 向上滚动显示
  }
  lastScroll = currentScroll;
});

// 滑入动画
const observer = new IntersectionObserver((entries) => {
  entries.forEach(entry => {
    if (entry.isIntersecting) {
      entry.target.classList.add('visible');
    }
  });
});

document.querySelectorAll('.fade-in-left, .fade-in-right').forEach(el => {
  observer.observe(el);
});
// 题库逻辑
function loadQuiz() {
  return fetch('/whitelist/quiz')
    .then(response => {
      if (!response.ok) throw new Error('题库加载失败');
      return response.json();
    });
}

// 渲染题目
function renderQuiz(quizData) {
  const quizContainer = document.getElementById('quiz-container');
  quizContainer.innerHTML = '';
  
  quizData.questions.forEach(q => {
    const questionDiv = document.createElement('div');
    questionDiv.className = 'question-card';
    questionDiv.dataset.id = q.id;
    questionDiv.innerHTML = `
      <h3>问题 ${q.id + 1}: ${q.text}</h3>
      ${q.options.map((opt, i) => `
        <label><input type="radio" name="q${q.id}" value="${i}" required> ${opt}</label><br>
      `).join('')}
    `;
    quizContainer.appendChild(questionDiv);
  });
}

// 初始化加载
loadQuiz()
  .then(renderQuiz)
  .catch(error => {
    const quizContainer = document.getElementById('quiz-container');
    quizContainer.innerHTML = `<p class="error">${error.message}，请刷新页面重试</p>`;
  });
  
// 提交处理
document.getElementById('submit-btn').addEventListener('click', () => {
  // 收集所有答案
  const questions = document.querySelectorAll('.question-card');
  const answers = Array.from(questions).map(qCard => {
    const selected = qCard.querySelector('input[type="radio"]:checked');
    return {
      id: parseInt(qCard.dataset.id),
      value: selected ? parseInt(selected.value) : -1
    };
  });
  
  // 检查是否所有题目都已作答
  if (answers.some(a => a.value === -1)) {
    alert('请完成所有题目后再提交');
    return;
  }
  
  // 准备提交数据
  const submitData = {
    answers: answers.map(a => a.value)
  };
  
  // 显示加载状态
  const submitBtn = document.getElementById('submit-btn');
  submitBtn.disabled = true;
  submitBtn.textContent = '提交中...';
  
  // 提交到后端
  fetch('/whitelist/submit', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify(submitData)
  })
  .then(response => {
    submitBtn.disabled = false;
    submitBtn.textContent = '提交答案';
    
    if (!response.ok) {
      throw new Error(`服务器错误: ${response.status}`);
    }
    return response.json();
  })
  .then(data => {
    const resultDiv = document.getElementById('result');
    resultDiv.style.display = 'block';
    resultDiv.innerHTML = '';
    
    if (data.success) {
      // 全部正确的处理
      resultDiv.innerHTML = `
        <div class="quiz-success">
          <h3>${data.message}</h3>
          <p>你的GameID已添加到服务器白名单</p>
          <p>现在你可以进入游戏了，祝你游玩愉快！</p>
        </div>
      `;
    } else if (data.error) {
      // 错误情况
      resultDiv.innerHTML = `<p class="error">${data.error}</p>`;
    } else {
      // 部分错误情况
      let html = `
        <div class="quiz-result">
          <p>得分：${data.score}/${data.total}</p>
          <p>${data.score < 18 ? '很遗憾未能通过，请认真阅读服务器规则后重新答题' : '接近成功了，只差一点点！请修正错题后重试'}</p>
          <div class="wrong-section">
            <h4>错题回顾：</h4>
      `;
      
      data.wrong_answers.forEach(w => {
        html += `
          <div class="wrong-item">
            <p><strong>问题 ${w.index}:</strong> ${w.question}</p>
            <p class="wrong"><span>✖</span> 你的答案: ${w.selected}</p>
            <p class="correct"><span>✓</span> 正确答案: ${w.correct}</p>
          </div>
        `;
      });
      
      html += `
          </div>
          <a href="/whitelist" class="start-button">重新答题</a>
        </div>
      `;
      
      resultDiv.innerHTML = html;
    }
    
    // 滚动到结果区域
    resultDiv.scrollIntoView({behavior: 'smooth'});
  })
  .catch(error => {
    document.getElementById('result').innerHTML = `
      <p class="error">请求失败: ${error.message}</p>
      <p>请检查网络连接后重试</p>
    `;
    document.getElementById('result').style.display = 'block';
  });
});

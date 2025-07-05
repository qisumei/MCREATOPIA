// 全局变量
let currentLogPage = 1;
let totalLogPages = 1;
let autoScrollEnabled = true;
let serverStatus = "unknown";
let lastRefreshTime = new Date();

// DOM元素
const serverStatusElement = document.getElementById('server-status');
const serverTimeElement = document.getElementById('server-time');
const serverTimeFooterElement = document.getElementById('server-time-footer');
const logViewerElement = document.getElementById('log-viewer');
const currentPageElement = document.getElementById('current-page');
const totalPagesElement = document.getElementById('total-pages');
const errorLogContainer = document.getElementById('error-log-container');
const aiAnalysisContainer = document.getElementById('ai-analysis-container');
const autoScrollCheckbox = document.getElementById('auto-scroll');

// 初始化事件监听器
function initEventListeners() {
    // 服务器控制按钮
    document.getElementById('start-btn').addEventListener('click', startServer);
    document.getElementById('restart-btn').addEventListener('click', restartServer);
    document.getElementById('stop-btn').addEventListener('click', stopServer);
    
    // 日志分页按钮
    document.getElementById('prev-log').addEventListener('click', () => {
        if (currentLogPage > 1) {
            currentLogPage--;
            fetchLogs(currentLogPage);
        }
    });
    
    document.getElementById('next-log').addEventListener('click', () => {
        if (currentLogPage < totalLogPages) {
            currentLogPage++;
            fetchLogs(currentLogPage);
        }
    });
    
    // 发送命令
    document.getElementById('send-command-btn').addEventListener('click', sendCommand);
    document.getElementById('command-input').addEventListener('keyup', (e) => {
        if (e.key === 'Enter') {
            sendCommand();
        }
    });
    
    // 错误处理按钮
    document.getElementById('refresh-errors-btn').addEventListener('click', fetchErrorLogs);
    document.getElementById('analyze-btn').addEventListener('click', analyzeErrors);
    
    // 自动滚动
    autoScrollCheckbox.addEventListener('change', () => {
        autoScrollEnabled = autoScrollCheckbox.checked;
    });
}

// 更新服务器状态
function updateServerStatus() {
    fetch('/health')
        .then(response => response.json())
        .then(data => {
            const statusBadge = document.getElementById('server-status');
            
            if (data.status === 'running') {
                serverStatus = 'running';
                statusBadge.className = 'server-status-badge server-running';
                statusBadge.textContent = '状态: 运行中';
                document.getElementById('start-btn').disabled = true;
                document.getElementById('restart-btn').disabled = false;
                document.getElementById('stop-btn').disabled = false;
            } else {
                serverStatus = 'down';
                statusBadge.className = 'server-status-badge server-stopped';
                statusBadge.textContent = '状态: 已停止';
                document.getElementById('start-btn').disabled = false;
                document.getElementById('restart-btn').disabled = true;
                document.getElementById('stop-btn').disabled = true;
            }
            
            // 更新服务器PID显示
            if (data.server_pid) {
                document.getElementById('server-pid').textContent = data.server_pid;
            }
            
            // 更新最后刷新时间
            lastRefreshTime = new Date();
            const timeString = lastRefreshTime.toLocaleTimeString();
            serverTimeElement.textContent = `最后刷新时间: ${timeString}`;
            serverTimeFooterElement.textContent = `最后刷新时间: ${timeString}`;
        })
        .catch(error => {
            console.error('获取服务器状态失败:', error);
            serverStatusElement.textContent = '状态: 连接失败';
            serverStatusElement.className = 'server-status-badge server-stopped blinking';
        });
}

// 获取服务器日志
function fetchLogs(page = 1) {
    fetch(`/get_log?page=${page}`)
        .then(response => response.json())
        .then(data => {
            logViewerElement.innerHTML = '';
            
            data.log.forEach(log => {
                const logLine = document.createElement('div');
                logLine.className = 'log-line';
                logLine.textContent = log;
                
                // 根据日志级别添加样式
                if (log.includes('[ERROR]') || log.includes('Exception') || log.includes('java.') || log.includes('Crash')) {
                    logLine.classList.add('log-line-error');
                } else if (log.includes('[WARN]')) {
                    logLine.classList.add('log-line-warn');
                } else if (log.includes('[INFO]')) {
                    logLine.classList.add('log-line-info');
                }
                
                logViewerElement.appendChild(logLine);
            });
            
            currentPageElement.textContent = page;
            totalPagesElement.textContent = data.total_pages;
            totalLogPages = data.total_pages;
            currentLogPage = page;
            
            // 滚动到底部
            if (autoScrollEnabled) {
                logViewerElement.scrollTop = logViewerElement.scrollHeight;
            }
        })
        .catch(error => {
            console.error('获取日志失败:', error);
            logViewerElement.innerHTML = '<div class="log-line log-line-error">无法加载日志</div>';
        });
}

// 获取错误日志
function fetchErrorLogs() {
    fetch('/get_errors')
        .then(response => response.json())
        .then(data => {
            errorLogContainer.innerHTML = '';
            
            if (data.errors && data.errors.length > 0) {
                data.errors.forEach(error => {
                    const errorLine = document.createElement('div');
                    errorLine.className = 'log-line log-line-error';
                    errorLine.textContent = error;
                    errorLogContainer.appendChild(errorLine);
                });
            } else {
                errorLogContainer.innerHTML = '<p class="text-success"><i class="bi bi-check-circle me-2"></i>没有检测到错误日志</p>';
            }
        })
        .catch(error => {
            console.error('获取错误日志失败:', error);
            errorLogContainer.innerHTML = '<div class="log-line log-line-error">无法加载错误日志</div>';
        });
}

// AI错误分析
function analyzeErrors() {
    aiAnalysisContainer.innerHTML = '<p class="text-info"><i class="bi bi-hourglass-split me-2"></i>正在通过AI分析错误，请稍候...</p>';
    
    fetch('/analyze_errors')
        .then(response => response.json())
        .then(data => {
            if (data.task_id) {
                // 在实际应用中，这里会处理异步任务
                // 简化处理：模拟从API获取数据
                setTimeout(() => {
                    fetchAnalysisResult();
                }, 1500);
            } else {
                aiAnalysisContainer.innerHTML = '<p class="text-danger">分析请求失败，请重试</p>';
            }
        })
        .catch(error => {
            console.error('分析错误失败:', error);
            aiAnalysisContainer.innerHTML = '<p class="text-danger">分析请求失败</p>';
        });
}

// 模拟获取分析结果
function fetchAnalysisResult() {
    fetch('/get_errors')
        .then(response => response.json())
        .then(data => {
            if (data.errors && data.errors.length > 0) {
                const errors = data.errors.join('\n');
                aiAnalysisContainer.innerHTML = `
                    <div>
                        <h5><i class="bi bi-exclamation-triangle-fill text-warning me-2"></i>检测到Forge Mod加载错误</h5>
                        <hr class="border-secondary">
                        <p class="fw-bold">问题分析：</p>
                        <ul>
                            <li>Mod冲突：<span class="text-danger">universalbonemeal-mod</span> 与 <span class="text-danger">neoforge-core</span> 存在API兼容性问题</li>
                            <li>版本不匹配：建议升级 UniversalBonemeal 至 v4.2.1+</li>
                            <li>配置文件错误：发现损坏的服务器配置文件</li>
                        </ul>
                        
                        <p class="fw-bold mt-3">解决方案：</p>
                        <ol>
                            <li>删除 <span class="text-warning">universalbonemeal-server.toml</span> 配置文件（位于 <code>/config</code> 目录）</li>
                            <li>从 <a href="#" class="text-info">官方来源</a> 下载 UniversalBonemeal v4.2.1 版本</li>
                            <li>重启服务器应用配置更改</li>
                            <li>如果问题持续，尝试禁用可疑Mod以排查问题</li>
                        </ol>
                        
                        <div class="mt-3 p-2 bg-dark text-white">
                            <small>DeepSeek AI分析 - ${new Date().toLocaleString()}</small>
                        </div>
                    </div>
                `;
            } else {
                aiAnalysisContainer.innerHTML = '<p class="text-success"><i class="bi bi-check-circle me-2"></i>没有检测到错误日志</p>';
            }
        })
        .catch(error => {
            console.error('获取错误日志失败:', error);
            aiAnalysisContainer.innerHTML = '<p class="text-danger">无法获取错误日志</p>';
        });
}

// 启动服务器
function startServer() {
    fetch('/start-server', { method: 'POST' })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                showToast('服务器启动成功', 'success');
                setTimeout(() => {
                    updateServerStatus();
                    fetchLogs(1);
                }, 2000);
            } else {
                showToast('服务器启动失败', 'danger');
            }
        })
        .catch(error => {
            console.error('启动服务器失败:', error);
            showToast('启动服务器失败', 'danger');
        });
}

// 停止服务器
function stopServer() {
    fetch('/stop-server', { method: 'POST' })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                showToast('服务器停止命令已发送', 'success');
                setTimeout(() => {
                    updateServerStatus();
                }, 2000);
            } else {
                showToast('停止服务器失败', 'danger');
            }
        })
        .catch(error => {
            console.error('停止服务器失败:', error);
            showToast('停止服务器失败', 'danger');
        });
}

// 重启服务器
function restartServer() {
    fetch('/restart-server', { method: 'POST' })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                showToast('服务器重启命令已发送', 'success');
                setTimeout(() => {
                    updateServerStatus();
                    fetchLogs(1);
                }, 2000);
            } else {
                showToast('重启服务器失败', 'danger');
            }
        })
        .catch(error => {
            console.error('重启服务器失败:', error);
            showToast('重启服务器失败', 'danger');
        });
}

// 发送命令
function sendCommand() {
    const commandInput = document.getElementById('command-input');
    const command = commandInput.value.trim();
    
    if (!command) {
        showToast('请输入命令', 'warning');
        return;
    }
    
    fetch('/send-command', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ command: command })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showToast(`命令已发送: ${command}`, 'success');
            commandInput.value = '';
            
            // 刷新日志显示最新结果
            setTimeout(() => {
                fetchLogs(currentLogPage);
            }, 1000);
        } else {
            showToast(`发送命令失败: ${command}`, 'danger');
        }
    })
    .catch(error => {
        console.error('发送命令失败:', error);
        showToast('发送命令失败', 'danger');
    });
}

// 显示Toast通知
function showToast(message, type = 'info') {
    // 移除现有的Toast
    const existingToast = document.querySelector('.toast');
    if (existingToast) existingToast.remove();
    
    // 创建Toast元素
    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    toast.innerHTML = `
        <div class="toast-content">
            <span>${message}</span>
        </div>
    `;
    
    // 添加到DOM
    document.body.appendChild(toast);
    
    // 显示Toast
    setTimeout(() => {
        toast.classList.add('show');
    }, 10);
    
    // 自动隐藏
    setTimeout(() => {
        toast.classList.remove('show');
        setTimeout(() => {
            toast.remove();
        }, 300);
    }, 3000);
}

// 模拟服务器指标数据
function updateServerMetrics() {
    // 在线玩家数
    const onlinePlayers = Math.floor(Math.random() * 5);
    document.getElementById('online-players').textContent = onlinePlayers;
    document.getElementById('player-bar').style.width = `${(onlinePlayers / 20) * 100}%`;
    
    // TPS
    const tps = (18 + Math.random() * 2).toFixed(1);
    document.getElementById('tps').textContent = tps;
    document.getElementById('tps-bar').style.width = `${(tps / 20) * 100}%`;
    
    // 内存使用
    const usedMem = Math.floor(1000 + Math.random() * 2000);
    const maxMem = 4096;
    document.getElementById('memory-usage').textContent = `${usedMem}MB/${maxMem}MB`;
    document.getElementById('memory-bar').style.width = `${(usedMem / maxMem) * 100}%`;
    
    // 根据内存使用情况设置颜色
    const memoryBar = document.getElementById('memory-bar');
    const usagePercent = (usedMem / maxMem) * 100;
    
    if (usagePercent > 90) {
        memoryBar.className = 'progress-bar bg-danger';
    } else if (usagePercent > 70) {
        memoryBar.className = 'progress-bar bg-warning';
    } else {
        memoryBar.className = 'progress-bar bg-success';
    }
}

// 页面加载完成后执行初始化
document.addEventListener('DOMContentLoaded', () => {
    // 初始获取日志和状态
    fetchLogs(1);
    fetchErrorLogs();
    updateServerStatus();
    
    // 设置定时更新
    setInterval(updateServerStatus, 5000); // 每5秒更新一次状态
    setInterval(updateServerMetrics, 10000); // 每10秒更新一次指标
    
    // 初始化事件监听器
    initEventListeners();
    
    // 模拟一些服务器指标数据
    updateServerMetrics();
});
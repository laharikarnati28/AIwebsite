// Graph coordinates and edges
const nodes = {
    'A': { x: 300, y: 50 },
    'B': { x: 200, y: 140 },
    'C': { x: 400, y: 140 },
    'D': { x: 130, y: 250 },
    'E': { x: 300, y: 260 },
    'F': { x: 300, y: 360 }
};

const edges = [
    ['A','B'], ['A','C'],
    ['B','E'], ['B','D'], ['B','C'],
    ['C','E'],
    ['D','E'],
    ['E','F']
];

const costLabels = {
    'A-B': '2', 'A-C': '4', 'B-E': '1', 'B-D': '5', 'B-C': '3',
    'C-E': '6', 'D-E': '2', 'E-F': '3'
};

function drawGraph(path = []) {
    const canvas = document.getElementById('graphCanvas');
    const ctx = canvas.getContext('2d');
    canvas.width = 600;
    canvas.height = 400;
    ctx.clearRect(0, 0, 600, 400);

    // Draw edges
    ctx.beginPath();
    ctx.strokeStyle = '#94a3b8';
    ctx.lineWidth = 2;
    for (let [u, v] of edges) {
        ctx.beginPath();
        ctx.moveTo(nodes[u].x, nodes[u].y);
        ctx.lineTo(nodes[v].x, nodes[v].y);
        ctx.stroke();
    }

    // Draw edge costs
    ctx.font = '12px "Segoe UI", monospace';
    ctx.fillStyle = '#2c3e66';
    for (let [edge, cost] of Object.entries(costLabels)) {
        let [u, v] = edge.split('-');
        let mx = (nodes[u].x + nodes[v].x) / 2;
        let my = (nodes[u].y + nodes[v].y) / 2;
        ctx.fillText(cost, mx - 6, my - 4);
    }

    // Draw nodes
    for (let [id, pos] of Object.entries(nodes)) {
        let color = '#3b82f6'; // normal
        if (id === 'A') color = '#10b981';
        else if (id === 'F') color = '#ef4444';
        else if (id === 'C') color = '#f59e0b';
        if (path.includes(id) && id !== 'A' && id !== 'F' && id !== 'C') color = '#22c55e';

        ctx.beginPath();
        ctx.fillStyle = color;
        ctx.arc(pos.x, pos.y, 22, 0, 2 * Math.PI);
        ctx.fill();
        ctx.fillStyle = '#ffffff';
        ctx.font = 'bold 16px "Inter"';
        ctx.textAlign = 'center';
        ctx.textBaseline = 'middle';
        ctx.fillText(id, pos.x, pos.y);
        if (id === 'C') {
            ctx.fillStyle = '#1e293b';
            ctx.font = '14px monospace';
            ctx.fillText('🚫', pos.x + 16, pos.y - 16);
        }
    }
}

// Run algorithm via Flask API
async function runAlgorithm(algo) {
    const logDiv = document.getElementById('logContainer');
    const pathSpan = document.getElementById('finalPathDisplay');
    logDiv.innerHTML = '<div class="log-line">⏳ AI reasoning in progress...</div>';
    pathSpan.innerText = '—';

    try {
        const response = await fetch(`/api/run/${algo}`);
        const data = await response.json();
        if (data.error) {
            logDiv.innerHTML = `<div class="log-line">❌ ${data.error}</div>`;
            return;
        }
        logDiv.innerHTML = '';
        data.logs.forEach(line => {
            const div = document.createElement('div');
            div.className = 'log-line';
            div.textContent = line;
            logDiv.appendChild(div);
        });
        if (data.path && data.path.length) {
            pathSpan.innerText = data.path.join(' → ');
            drawGraph(data.path);
        } else {
            pathSpan.innerText = '❌ No valid path found';
            drawGraph([]);
        }
        logDiv.scrollTop = logDiv.scrollHeight;
    } catch (err) {
        logDiv.innerHTML = `<div class="log-line">🔥 Error: ${err.message}</div>`;
    }
}

// Tab switching
document.querySelectorAll('.tab-btn').forEach(btn => {
    btn.addEventListener('click', () => {
        document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
        btn.classList.add('active');
        const algo = btn.getAttribute('data-algo');
        runAlgorithm(algo);
    });
});

// Clear logs
document.getElementById('clearLogsBtn').addEventListener('click', () => {
    document.getElementById('logContainer').innerHTML = '<div class="log-line">🧹 Logs cleared. Select an algorithm to run again.</div>';
    document.getElementById('finalPathDisplay').innerText = '—';
    drawGraph([]);
});

// Initial graph and default algorithm (DFS)
drawGraph([]);
runAlgorithm('dfs');
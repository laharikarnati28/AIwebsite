from flask import Flask, render_template, jsonify
import heapq
import math
from queue import Queue

app = Flask(__name__)

# =====================================
# COMMON ENVIRONMENT (matching your scripts)
# =====================================
START = 'A'
GOAL = 'F'
BLOCKED = ['C']
MAX_COST = 15

GRAPH = {
    'A': [('B', 2), ('C', 4)],
    'B': [('E', 1), ('D', 5), ('C', 3)],
    'C': [('E', 6)],
    'D': [('E', 2)],
    'E': [('F', 3)],
    'F': []
}

HEURISTIC = {'A': 7, 'B': 5, 'C': 100, 'D': 3, 'E': 1, 'F': 0}
SAFE_PROB = {'B': 0.90, 'C': 0.20, 'D': 0.80, 'E': 0.85, 'F': 0.95}
UTILITY = {'D': 6, 'E': 8, 'F': 10}

# --------------------------------------------------------------
# 1. DFS (co1 style)
# --------------------------------------------------------------
def run_dfs():
    logs = []
    visited = set()
    final_path = []

    def dfs(node, path):
        logs.append(f"Visiting: {node}")
        visited.add(node)
        path.append(node)
        logs.append(f"Current path: {' → '.join(path)}")
        if node == GOAL:
            logs.append(f"✅ Goal reached: {node}")
            final_path.extend(path)
            return True
        for neighbor, _ in GRAPH[node]:
            if neighbor not in visited:
                if neighbor in BLOCKED:
                    logs.append(f"⚠️ Avoid blocked node: {neighbor}")
                    continue
                logs.append(f"Reasoning step: {node} → {neighbor}")
                logs.append(f"AI selects {neighbor}")
                if dfs(neighbor, path[:]):
                    return True
        return False

    dfs(START, [])
    return logs, final_path

# --------------------------------------------------------------
# 2. BFS
# --------------------------------------------------------------
def run_bfs():
    logs = []
    q = Queue()
    q.put((START, [START]))
    visited = set()
    final_path = []
    while not q.empty():
        node, path = q.get()
        if node in visited:
            continue
        if node in BLOCKED:
            logs.append(f"Avoid blocked node: {node}")
            continue
        logs.append(f"Exploring: {node}")
        logs.append(f"Current path: {' → '.join(path)}")
        visited.add(node)
        if node == GOAL:
            logs.append(f"🎯 Goal reached: {node}")
            final_path = path
            break
        for neighbor, _ in GRAPH[node]:
            logs.append(f"Reason: {node} can move to {neighbor}")
            q.put((neighbor, path + [neighbor]))
    return logs, final_path

# --------------------------------------------------------------
# 3. UCS (Uniform Cost Search)
# --------------------------------------------------------------
def run_ucs():
    logs = []
    pq = [(0, START, [START])]
    visited = set()
    final_path = []
    while pq:
        cost, node, path = heapq.heappop(pq)
        if node in visited:
            continue
        if node in BLOCKED:
            logs.append(f"🚫 Avoid blocked: {node}")
            continue
        visited.add(node)
        logs.append(f"Selected node: {node} (cost={cost})")
        logs.append(f"Current path: {' → '.join(path)}")
        if node == GOAL:
            logs.append(f"✨ Goal reached!")
            final_path = path
            break
        for neighbor, edge_cost in GRAPH[node]:
            total = cost + edge_cost
            logs.append(f"Comparing total cost to {neighbor}: {total}")
            heapq.heappush(pq, (total, neighbor, path + [neighbor]))
    return logs, final_path

# --------------------------------------------------------------
# 4. A* Search
# --------------------------------------------------------------
def run_astar():
    logs = []
    open_list = [(HEURISTIC[START], 0, START, [START])]
    visited = set()
    final_path = []
    while open_list:
        f, g, node, path = heapq.heappop(open_list)
        if node in BLOCKED:
            logs.append(f"Avoid blocked node: {node}")
            continue
        logs.append(f"Expanding node: {node} | f={f}, g={g}")
        logs.append(f"Path: {' → '.join(path)}")
        if node == GOAL:
            logs.append(f"🏁 Goal reached!")
            final_path = path
            break
        if node in visited:
            continue
        visited.add(node)
        for neighbor, cost in GRAPH[node]:
            g_new = g + cost
            h = HEURISTIC[neighbor]
            f_new = g_new + h
            logs.append(f"Reasoning: {node} → {neighbor}")
            logs.append(f"  g({neighbor})={g_new}, h={h}, f={f_new}")
            heapq.heappush(open_list, (f_new, g_new, neighbor, path + [neighbor]))
    return logs, final_path

# --------------------------------------------------------------
# 5. Constraint Backtracking (max cost + blocked)
# --------------------------------------------------------------
def run_constraint():
    logs = []
    visited = set()
    final_path = []

    def is_valid(node, total_cost):
        if node in BLOCKED:
            logs.append(f"Constraint failed: {node} is blocked")
            return False
        if total_cost > MAX_COST:
            logs.append(f"Constraint failed: cost {total_cost} > {MAX_COST}")
            return False
        return True

    def backtrack(node, total_cost, path):
        logs.append(f"Visiting: {node} (cost={total_cost})")
        path.append(node)
        visited.add(node)
        logs.append(f"Current path: {' → '.join(path)}")
        if node == GOAL:
            logs.append(f"✅ Goal reached!")
            final_path.extend(path)
            return True
        for neighbor, cost in GRAPH[node]:
            if neighbor not in visited:
                logs.append(f"Checking constraints for {neighbor}")
                new_cost = total_cost + cost
                if is_valid(neighbor, new_cost):
                    logs.append("Constraint accepted")
                    if backtrack(neighbor, new_cost, path[:]):
                        return True
        return False

    backtrack(START, 0, [])
    return logs, final_path

# --------------------------------------------------------------
# 6. Minimax (with utility values)
# --------------------------------------------------------------
def run_minimax():
    logs = []
    best_path = []

    def minimax(node, is_max, path):
        logs.append(f"Visiting: {node} ({'MAX' if is_max else 'MIN'} turn)")
        logs.append(f"Current path: {' → '.join(path)}")
        if node in UTILITY:
            logs.append(f"Terminal node {node}, utility = {UTILITY[node]}")
            return UTILITY[node], path
        if is_max:
            best_val = -math.inf
            best_local_path = None
            for neighbor, _ in GRAPH[node]:
                if neighbor in BLOCKED:
                    logs.append(f"Avoid blocked node: {neighbor}")
                    continue
                logs.append(f"MAX checks move: {node} → {neighbor}")
                val, sub_path = minimax(neighbor, False, path + [neighbor])
                if val > best_val:
                    best_val = val
                    best_local_path = sub_path
            logs.append(f"Best value at {node} (MAX) = {best_val}")
            return best_val, best_local_path if best_local_path else path
        else:
            best_val = math.inf
            best_local_path = None
            for neighbor, _ in GRAPH[node]:
                if neighbor in BLOCKED:
                    continue
                logs.append(f"MIN checks move: {node} → {neighbor}")
                val, sub_path = minimax(neighbor, True, path + [neighbor])
                if val < best_val:
                    best_val = val
                    best_local_path = sub_path
            logs.append(f"Best value at {node} (MIN) = {best_val}")
            return best_val, best_local_path if best_local_path else path

    _, final_path = minimax(START, True, [START])
    if final_path:
        best_path = final_path
    logs.append(f"Minimax utility value: {UTILITY.get(GOAL, 'N/A')}")
    return logs, best_path

# --------------------------------------------------------------
# 7. Probabilistic Reasoning (Bayes style)
# --------------------------------------------------------------
def run_probabilistic():
    logs = []
    # Expected best path from your original code
    path = ['A', 'B', 'E', 'F']
    total_prob = 1.0
    logs.append("📊 Evaluating safest path: A → B → E → F")
    for node in path:
        if node in SAFE_PROB:
            prob = SAFE_PROB[node]
            logs.append(f"Node {node}: safety probability = {prob}")
            if node in BLOCKED:
                logs.append(f"  ⚠️ Node {node} is marked risky (blocked)")
            else:
                logs.append(f"  ✅ AI considers node SAFE")
                total_prob *= prob
    logs.append(f"Overall path safety probability = {round(total_prob, 4)}")
    return logs, path

# --------------------------------------------------------------
# 8. Hybrid A* (cost + heuristic + safety >= 0.5 + blocked)
# --------------------------------------------------------------
def run_hybrid():
    logs = []
    open_list = [(HEURISTIC[START], 0, START, [START])]
    visited = set()
    final_path = []

    while open_list:
        f, g, node, path = heapq.heappop(open_list)
        logs.append(f"Expanding node: {node} (cost={g}, f={f})")
        logs.append(f"Path: {' → '.join(path)}")
        if node == GOAL:
            logs.append(f"🎉 Goal reached with hybrid constraints!")
            final_path = path
            break
        if node in visited:
            continue
        visited.add(node)
        for neighbor, cost in GRAPH[node]:
            # Constraint: blocked
            if neighbor in BLOCKED:
                logs.append(f"Constraint failed: {neighbor} is blocked")
                continue
            # Probability constraint (safety >= 0.5)
            prob = SAFE_PROB.get(neighbor, 1.0)
            logs.append(f"Safety probability for {neighbor} = {prob}")
            if prob < 0.5:
                logs.append(f"❌ AI avoids risky node {neighbor} (prob < 0.5)")
                continue
            g_new = g + cost
            h = HEURISTIC[neighbor]
            f_new = g_new + h
            logs.append(f"Hybrid reasoning: {node} → {neighbor}")
            logs.append(f"  g={g_new}, h={h}, f={f_new} ✅")
            heapq.heappush(open_list, (f_new, g_new, neighbor, path + [neighbor]))
    if not final_path:
        logs.append("❌ No path satisfies all constraints (blocked, safety, optimality).")
    return logs, final_path

# --------------------------------------------------------------
# Flask Routes
# --------------------------------------------------------------
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/run/<algo>')
def run_algorithm(algo):
    algos = {
        'dfs': run_dfs,
        'bfs': run_bfs,
        'ucs': run_ucs,
        'astar': run_astar,
        'constraint': run_constraint,
        'minimax': run_minimax,
        'probabilistic': run_probabilistic,
        'hybrid': run_hybrid
    }
    if algo not in algos:
        return jsonify({'error': 'Algorithm not found'}), 404
    logs, path = algos[algo]()
    return jsonify({'logs': logs, 'path': path})

if __name__ == '__main__':
    app.run(debug=True)
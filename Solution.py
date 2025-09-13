import json
from collections import defaultdict
from datetime import datetime

# --- Step 1: Load dataset ---
with open("dataset.json") as f:
    data = json.load(f)

agents = data["agents"]
tickets = data["tickets"]

# Track agent workloads
agent_workload = defaultdict(int)

# --- Step 2: Helper scoring functions ---
def skill_match(agent, ticket):
    agent_skills = set(agent.get("skills", []))
    ticket_tags = set(ticket.get("tags", []))
    return len(agent_skills & ticket_tags) / max(1, len(ticket_tags))

def priority_score(ticket):
    base = {"low": 1, "medium": 2, "high": 3, "urgent": 5}
    score = base.get(ticket.get("priority", "low"), 1)
    # Add waiting time boost
    created = datetime.fromisoformat(ticket["created_at"])
    age_days = (datetime.now() - created).days
    return score + 0.1 * age_days

def agent_score(agent, ticket):
    # Factors: skill match, experience, workload
    s_match = skill_match(agent, ticket)
    exp = agent.get("experience", 1)
    load_penalty = 1 / (1 + agent_workload[agent["id"]])
    return s_match * 0.6 + (exp / 10) * 0.3 + load_penalty * 0.1

# --- Step 3: Assign tickets ---
assignments = []

# Sort tickets by priority
tickets_sorted = sorted(tickets, key=priority_score, reverse=True)

for ticket in tickets_sorted:
    best_agent = None
    best_score = -1
    for agent in agents:
        if not agent.get("available", True):
            continue
        score = agent_score(agent, ticket)
        if score > best_score:
            best_score = score
            best_agent = agent
    if best_agent:
        assignments.append({
            "ticket_id": ticket["id"],
            "assigned_agent": best_agent["id"]
        })
        agent_workload[best_agent["id"]] += 1

# --- Step 4: Save results ---
with open("output.json", "w") as f:
    json.dump(assignments, f, indent=2)

print("✅ Assignment complete! Saved to output.json")

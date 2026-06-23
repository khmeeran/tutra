import datetime

class MemoryNode:
    def __init__(self, name, type, confidence, created_at, last_referenced_at=None, concept_id=None):
        self.name = name
        self.type = type
        self.confidence_score = confidence
        self.created_at = created_at
        self.last_referenced_at = last_referenced_at
        self.concept_id = concept_id

def score_memory(memory, current_concept_id, now):
    score = memory.confidence_score * 10
    
    if memory.type == 'Relationship':
        if memory.concept_id == current_concept_id:
            score += 50.0 
    
    days_old = (now - memory.created_at).days
    score -= (days_old * 0.05)
    
    if memory.last_referenced_at:
        hours_since_used = (now - memory.last_referenced_at).total_seconds() / 3600
        if hours_since_used < 72:
            score -= 100.0  # Fatigue Penalty
        else:
            score += min(hours_since_used * 0.01, 10.0) 
            
    return score

def run_retrieval_test():
    print("--- STARTING RETRIEVAL ENGINE TESTS ---")
    now = datetime.datetime.now()
    
    current_concept_id = "concept_gravity"
    
    memories = [
        MemoryNode("Cricket", "Interest", 1.0, now - datetime.timedelta(days=100), now - datetime.timedelta(hours=24)),
        MemoryNode("Space", "Interest", 0.8, now - datetime.timedelta(days=10), now - datetime.timedelta(days=10)),
        MemoryNode("Dhoni Sixer for Projectile", "Relationship", 1.0, now - datetime.timedelta(days=30), now - datetime.timedelta(days=15), "concept_gravity"),
        MemoryNode("Generic Math Joke", "Relationship", 1.0, now - datetime.timedelta(days=20), None, "concept_algebra")
    ]
    
    print(f"\nTarget Concept: {current_concept_id}")
    print(f"Total Candidates: {len(memories)}")
    
    scored_candidates = []
    for mem in memories:
        s = score_memory(mem, current_concept_id, now)
        scored_candidates.append({"memory": mem, "score": s})
        print(f"Scored {mem.name} ({mem.type}) -> Score: {s}")
        
    scored_candidates.sort(key=lambda x: x["score"], reverse=True)
    
    print("\n--- Applying Truncation Rules ---")
    final_context = {"Interest": None, "Relationship": None}
    
    for item in scored_candidates:
        mem = item["memory"]
        if final_context.get(mem.type) is None:
            final_context[mem.type] = mem
            print(f"✅ Selected top {mem.type}: {mem.name} (Score: {item['score']})")
        else:
            print(f"❌ Truncated (Bloat Prevention): {mem.name} (Score: {item['score']})")
            
    print("\n[TEST RESULTS]")
    assert final_context["Interest"].name == "Space", "Fatigue penalty failed, Cricket was chosen!"
    print("✅ Fatigue Penalty Test Passed: 'Cricket' was rejected due to recent usage, falling back to 'Space'.")
    assert final_context["Relationship"].name == "Dhoni Sixer for Projectile", "Relevance boost failed!"
    print("✅ Concept Relevance Test Passed: 'Dhoni Sixer' got +50 boost for matching target concept.")
    print("✅ Prompt Truncation Test Passed: Only 1 Interest and 1 Relationship returned.")
    print("\n--- ALL RETRIEVAL TESTS PASSED ---")

if __name__ == "__main__":
    run_retrieval_test()

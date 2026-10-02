#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MEC-2.3 | Chunked quota watcher + auto-resume — FULL CHAIN edition.
Foreground execution in repeated tool calls (no background processes — MEC-2.1 lesson).
Each invocation = one chunk (default 540s):

  stage=search_b2  -> batch2_search.py (15 deferred queries; script IS the probe:
                       aborts cleanly in ~40s if quota still blocked)
  ledger 130/130 OK -> stage=compile_b2: batch2_compile + batch2_intelligence
  -> stage=search_b3: batch3_search.py (143 queries, MAX_SECONDS budget per chunk)
  ledger b3 143/143 OK -> stage=compile_b3: batch3_compile + batch3_intelligence
  -> stage=awaiting_curation: no-op (manual curation + merge by the agent)

State: research/quota_watcher_state.json | Log: research/quota_watcher.log
"""
import json, os, subprocess, time

BASE = "/home/z/my-project"
LOG = os.path.join(BASE, "research", "quota_watcher.log")
STATE = os.path.join(BASE, "research", "quota_watcher_state.json")
CHUNK_S = int(os.environ.get("CHUNK_S", "540"))
SEARCH_BUDGET_S = int(os.environ.get("SEARCH_BUDGET_S", "440"))

def log(msg):
    line = time.strftime("[%Y-%m-%d %H:%M:%S] ") + msg
    print(line, flush=True)
    with open(LOG, "a", encoding="utf-8") as f:
        f.write(line + "\n")

def load_state():
    if os.path.exists(STATE):
        try:
            s = json.load(open(STATE, encoding="utf-8"))
            # migrate MEC-2.2 stage names
            if s.get("stage") == "search":
                s["stage"] = "search_b2"
            elif s.get("stage") == "compile":
                s["stage"] = "compile_b2"
            return s
        except Exception:
            pass
    return {"stage": "search_b2", "chunks": 0, "blocked_streak": 0}

def save_state(s):
    json.dump(s, open(STATE, "w", encoding="utf-8"), ensure_ascii=False, indent=1)

def ledger_ok_count(batch):
    try:
        led = json.load(open(os.path.join(BASE, "research", "action_ledger.json"), encoding="utf-8"))
        return len([l for l in led if l.get("batch") == batch and l.get("retrieval_status") == "OK"])
    except Exception:
        return -1

def run_step(script, timeout_s, env_extra=None):
    log(f"RUN {script} (budget {timeout_s}s)")
    env = dict(os.environ)
    if env_extra:
        env.update(env_extra)
    try:
        r = subprocess.run(["python3", os.path.join(BASE, "scripts", script)],
                           capture_output=True, text=True, timeout=timeout_s + 90, cwd=BASE, env=env)
        tail = (r.stdout or "").strip().split("\n")
        log(f"{script} exit={r.returncode}")
        for line in tail[-4:]:
            log("  | " + line[:150])
        if r.returncode != 0:
            log(f"{script} STDERR: {(r.stderr or '')[:300]}")
        return r.returncode == 0
    except subprocess.TimeoutExpired:
        log(f"{script} TIMEOUT after {timeout_s + 90}s (state preserved — resumable)")
        return False
    except Exception as e:
        log(f"{script} ERROR {e}")
        return False

def main():
    s = load_state()
    t0 = time.time()
    s["chunks"] += 1
    save_state(s)
    b2ok, b3ok = ledger_ok_count(2), ledger_ok_count(3)
    log(f"=== chunk #{s['chunks']} start | stage={s['stage']} | b2={b2ok}/130 b3={b3ok}/143 ===")

    if s["stage"] == "awaiting_curation":
        log("stage=awaiting_curation — nothing to do (manual curation + merge pending)")
        return 0

    if s["stage"] == "search_b2":
        before = b2ok
        run_step("batch2_search.py", SEARCH_BUDGET_S, {"MAX_SECONDS": str(SEARCH_BUDGET_S)})
        after = ledger_ok_count(2)
        log(f"b2 search chunk: ok actions {before} -> {after}")
        if after >= 130:
            s["stage"] = "compile_b2"
        else:
            s["blocked_streak"] = s.get("blocked_streak", 0) + 1 if after == before else 0
            save_state(s)
            log(f"chunk ended: b2 {after}/130, blocked_streak={s['blocked_streak']}")
            return 0
        save_state(s)

    if s["stage"] == "compile_b2":
        if run_step("batch2_compile.py", 200) and run_step("batch2_intelligence.py", 200):
            s["stage"] = "search_b3"
            save_state(s)
            log("B2 PIPELINE COMPLETE (search+compile+intelligence) — moving to batch-3 search")
        else:
            save_state(s)
            log("b2 compile/intelligence failed — retry next chunk")
            return 1

    if s["stage"] == "search_b3":
        before = ledger_ok_count(3)
        run_step("batch3_search.py", SEARCH_BUDGET_S, {"MAX_SECONDS": str(SEARCH_BUDGET_S)})
        after = ledger_ok_count(3)
        log(f"b3 search chunk: ok actions {before} -> {after}")
        if after >= 143:
            s["stage"] = "compile_b3"
            save_state(s)
        else:
            s["blocked_streak"] = s.get("blocked_streak", 0) + 1 if after == before else 0
            save_state(s)
            log(f"chunk ended: b3 {after}/143, blocked_streak={s['blocked_streak']}")
            return 0

    if s["stage"] == "compile_b3":
        if run_step("batch3_compile.py", 200) and run_step("batch3_intelligence.py", 200):
            s["stage"] = "awaiting_curation"
            save_state(s)
            log("FULL PIPELINE READY: b2(15 deferred)+b3(143) searched+compiled — awaiting manual curation + merge")
            return 0
        else:
            log("b3 compile/intelligence failed — retry next chunk")
            return 1

    log(f"=== chunk end at {time.strftime('%H:%M:%S')} (elapsed {int(time.time()-t0)}s) ===")
    return 0

if __name__ == "__main__":
    exit(main())

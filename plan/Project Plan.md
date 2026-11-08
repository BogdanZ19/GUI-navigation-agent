# Undergraduate Thesis Project Plan

**Working title:** Local Windows GUI Agent with Calibrated Autonomy — Selective Clarification and Confirmation Based on Uncertainty and Risk

**Target:** licență defence, June–July 2027 · **Plan date:** 8 November 2026

---

## 1. Idea in one paragraph

An agent receives a text command (voice optional) and carries it out in Windows applications through the GUI: it observes the screen and the accessibility tree, plans steps, proposes mouse/keyboard actions, and verifies each result. The contribution is **calibrated autonomy**: before each action the agent estimates *how sure it is* (uncertainty) and *how bad a mistake would be* (risk), and chooses to **execute**, **ask for clarification**, **ask for confirmation**, or **replan**. The goal is to stop wrong actions while interrupting the user as little as possible.

Example questions the agent should produce:

- "Open **Final report.pdf** (modified today) or **Old final report.pdf** (modified in March)?"
- "I'm about to **send** this message to **prof. Popescu**. Send it?"
- "This will **permanently delete** 3 files from *Documents\Thesis*. It cannot be undone. Continue?"

## 2. Research question and hypotheses

**RQ.** Can a GUI agent that asks selectively — based on uncertainty and risk — reach task success close to an agent that always asks, while interrupting far less, and prevent most of the errors an agent that never asks would make?

| # | Hypothesis | Tested by |
|---|---|---|
| H1 | Selective asking prevents most incorrect actions of the never-ask agent. | Prevented Error Rate, incorrect-action count (§10) |
| H2 | Selective asking reaches task success close to always-ask with far fewer questions. | Success-vs-interruptions curve (§9.4) |
| H3 | The uncertainty score is informative: higher score → higher chance the proposed action is wrong. | Reliability diagram, ECE, AUROC (§10) |
| H4 | Each signal source (multiple matches, conflicts between sources, sampling disagreement, risk rules) contributes. | Ablations (§9.5) |

## 3. Contributions

1. A **decision policy** (execute / clarify / confirm / replan) driven by an explicit uncertainty score and a context-aware risk level.
2. A set of **uncertainty indicators** for GUI agents, including disagreement between the screenshot and the accessibility tree.
3. **Contextual, structured questions** (multiple-choice with a natural-language rendering) and resuming the task from the answer.
4. A **small interactive Windows benchmark** with labelled ambiguity points and risk levels, plus a **simulated user** so runs can be repeated exactly.
5. An **evaluation of the trade-off** between success and interruptions, including calibration of the uncertainty score.

Not claimed as novel: combining screenshots with the accessibility tree; the planner/executor/critic split.

## 4. Scope

**In scope (core):**
- Windows-native, Python, no WSL; local open-weight models only.
- Two applications: **Notepad** (MVP) and **File Explorer** (main ambiguity and risk source).
- Text commands.
- Rule-based uncertainty and risk; thresholds tuned on a dev split.

**Stretch (pick at most one, only after core experiments are done):**
- Browser tasks (accessibility tree first; DOM/CDP only if needed).
- Voice commands with a local speech-to-text model (adds ASR ambiguity as an uncertainty source).
- Conformal prediction for the clarification decision (§6.3).
- Results on a subset of a public benchmark (ScreenSpot for grounding; WindowsAgentArena for interactive tasks).

**Out of scope:** Linux/Fedora, UAC / secure desktop, real payments, destructive operations on real data, fine-tuning (unless everything else is done).

## 5. Architecture

```
            user (or simulated user)
                 ▲        │ command / answers
       question  │        ▼
┌──────────────────────────────────────────────┐
│ Orchestrator: task state, step, history,     │
│ pause/resume, trajectory logging             │
└───┬───────────────┬───────────────┬──────────┘
    ▼               ▼               ▼
 Planner         Executor         Critic
 goal → steps    step + obs →     pre:  uncertainty + risk → decision
 replans         candidate        post: before/after diff → ok / retry / replan
                 actions
    └───────────────┴───────┬───────┘
                            ▼
        Windows environment (observe / act / emergency stop)
        screenshot · UI Automation tree · window info · input
```

Roles can share one model with different prompts and output schemas. The critic's pre-action decision is mostly **rule-based** on top of signals produced by the model and the environment, so it can be inspected and ablated.

### 5.1 Loop per step

1. **Observe:** active window, screenshot, simplified UIA tree → `Observation`.
2. **Propose:** the executor returns the **top-k candidate actions** with scores, not a single one. This is needed for the uncertainty signals.
3. **Assess (critic, pre):** compute uncertainty `u ∈ [0,1]`, risk level `r`, conflict flags → decision.
4. **Act or ask:** execute, or emit a structured `Question` and pause.
5. **Verify (critic, post):** compare before/after against the step's `expected_effect` → success / retry / replan.
6. **Log** everything (§11).

### 5.2 Core schemas (JSON / dataclasses)

- `Observation`: window info, screenshot path, UIA elements (id, name, control type, state, bbox, supported patterns), timestamp.
- `Plan`: goal, ordered steps, each with `description` and `expected_effect`.
- `Action`: type (`click`, `double_click`, `type`, `hotkey`, `scroll`), target element id and/or coordinates, parameters, rationale.
- `Candidate`: action + score + source (UIA / visual / both).
- `Assessment`: `u`, the uncertainty indicators that fired, risk level and the rule that set it, decision.
- `Question`: kind (`clarify` / `confirm`), text, options (each mapped to a candidate or to yes/no), consequence text.
- `StepResult`: before/after observation ids, verified effect, outcome.

## 6. Uncertainty estimation

### 6.1 Indicators (version 1, rule-based)

| Indicator | Signal |
|---|---|
| Multiple matches | > 1 element matches the target description |
| Small score margin | top-1 vs top-2 candidate score gap below δ |
| Sampling disagreement | n samples (e.g. 3–5, temperature > 0) choose different targets |
| Planner–executor mismatch | executor's target doesn't match the planner's step |
| Source conflict | screenshot/OCR and UIA disagree (missing element, different text, off-screen bbox) |
| Ambiguous reference | command uses "it", "that file", "the report", or a partial name |
| Unverifiable effect | the step's expected effect cannot be checked from the observation |
| (stretch) ASR ambiguity | low-confidence or multiple speech-to-text hypotheses |

Combine them as a weighted sum clipped to [0,1] (weights set by hand, then tuned on dev). Every fired indicator is kept as a **reason**, used both in questions and in logs.

### 6.2 Cost control

Sampling disagreement is the most expensive signal with a local model. Run it only when the cheap indicators are inconclusive, or when risk ≥ medium.

### 6.3 Stretch: conformal clarification

Following Ren et al. (2023, *Robots That Ask For Help*): on a calibration set, choose a threshold so the **prediction set** of candidate actions contains the correct one with probability ≥ 1−α. If the set has one element → act; if more than one → ask, offering the set as the options. This gives "calibrated" a formal meaning and is a clean extension to compare with the rule-based score.

## 7. Risk assessment

Risk applies to an **action in context**, not to an action type. Rules look at the target element's name and control type, the application, the window/dialog title and the planned step.

| Level | Examples | Default |
|---|---|---|
| Low | scroll, switch tab, open menu, select item | execute if `u` is low |
| Medium | edit text, rename, move a file, save over a file | execute if `u` is very low, otherwise clarify |
| High | send message, publish, delete to Recycle Bin, close without saving | confirm |
| Critical | permanent delete (Shift+Del, "Delete permanently"), payments, security settings | confirm with explicit consequence; blocked in evaluation |

Reversibility is a rule input: an action with an obvious undo is one level lower.

## 8. Decision policy

Evaluated in order, first match wins:

1. Source conflict on the target → **stop and ask**.
2. `u ≥ τ_clarify` → **clarify** (options = top candidates).
3. Risk ≥ high → **confirm** (state action, target and consequence).
4. Risk = medium and `u ≥ τ_medium` → **clarify**.
5. Otherwise → **execute**.

After execution: effect matches → next step; effect missing → retry once; still missing or unexpected state → **replan**; if the step was high-risk and can't be verified → stop and report.

Question rules: always name the action, the target and the consequence; offer concrete options; never ask a bare "Are you sure?".

`τ_clarify` and `τ_medium` are tuned on the **dev split only**, then frozen.

## 9. Evaluation design

### 9.1 Task suite

About **80 tasks** on Notepad + File Explorer, each a declarative spec:

```yaml
id: fe-ambig-07
app: explorer
setup: fixtures/report_pair      # files created before the run
command: "Open the final report"
category: ambiguous              # clear | ambiguous | similar-names | risky | unexpected | conflict
intended:
  target: "Final report.pdf"
ambiguity_points:
  - step: 1
    candidates: ["Final report.pdf", "Old final report.pdf"]
    oracle_answer: "Final report.pdf"
risk_points:
  - step: 1
    level: low
success_check: window_title_contains("Final report.pdf")
```

Suggested mix: 25 clear, 20 ambiguous / similar names, 20 risky, 15 unexpected result or source conflict. Split **30 dev / 50 test** before tuning anything. Labels (ambiguity points, risk levels) are written **before** running the critic, ideally checked by a second person.

### 9.2 Simulated user

A scripted oracle answers questions using the task spec:

- clarification → returns `oracle_answer` (matched against the question's options);
- confirmation → approves if the action is part of the intended goal, refuses otherwise;
- unexpected question (not at a labelled point) → answers from the intended goal and is counted as **unnecessary**.

This makes runs repeatable and ablations cheap. A small **human pilot** (5–10 tasks, 2–3 people) checks whether the questions are understandable.

### 9.3 Configurations (all required)

| Config | Behaviour |
|---|---|
| **Never-ask** | executes every proposed action (base agent) |
| **Always-confirm-risky** | asks on every action with risk ≥ medium, no uncertainty |
| **Always-ask** | asks before every action (upper bound on success, lower bound on autonomy) |
| **Selective (ours)** | full policy (§8) |

Each task runs **3 times** per config (model sampling is non-deterministic); report mean ± std.

### 9.4 Trade-off curve

Sweep `τ_clarify` and plot **task success vs. questions per task**. Never-ask and always-ask are the two ends; the selective agent should sit above the line joining them. This is the main figure of the thesis.

### 9.5 Ablations

Remove one at a time: risk evaluator · post-action verification · UIA tree (screenshot only) · screenshot (UIA only) · sampling disagreement · source-conflict indicator · clarification (confirmations only) · same model vs. different model for executor and critic.

### 9.6 External comparison (optional)

- **ScreenSpot** (or ScreenSpot-v2): grounding accuracy of the vision model alone, to place it among published results.
- **WindowsAgentArena**: a small subset with the base agent, if hardware allows.

Comparisons with published numbers are only valid with the same data, split and protocol. Report them as context, not as the main result.

## 10. Metrics

**Primary:**
- **Task Success Rate**
- **Questions per task** (interruptions)
- **Incorrect actions per task** (actions not part of the intended trajectory; high-risk ones counted separately)

**Clarification quality** (ground truth = labelled ambiguity/risk points):
- Clarification precision / recall / F1
- Unnecessary Clarification Rate (questions in clear situations)
- Prevented Error Rate (asks where never-ask made a wrong action at the same step)

**Calibration of `u`:**
- Reliability diagram and **ECE** (is the action wrong as often as `u` says?)
- **AUROC** of `u` for predicting a wrong action
- Risk–coverage curve

**Standard GUI-agent metrics:** Step Success Rate, Grounding Accuracy, Action Type Accuracy, Situation Assessment F1 (critic post-check: ok / retry / replan), Total Step Count.

**Secondary:** latency per step and total time, on stated hardware.

## 11. Trajectory logging

One JSONL file per run plus a screenshots folder. Per step: observation id, plan version, candidates with scores, uncertainty indicators and `u`, risk level and rule, decision, question and answer, executed action, before/after ids, verification outcome. Per task: config, model, seed, thresholds, final outcome, metrics. Logs feed both the metrics scripts and the thesis figures, and can later be used as fine-tuning data.

## 12. Code structure

```
src/gui_agent/
├── schemas/           # dataclasses + JSON (de)serialisation
├── platform/windows/  # window_manager, screenshot, accessibility, input_control, observer, kill_switch
├── models/            # language_model, vision_language_model, (speech_to_text)
├── agent/
│   ├── planner.py
│   ├── executor.py
│   └── critic/        # uncertainty.py, risk.py, policy.py, questions.py, verify.py
├── orchestration/     # loop, task state, pause/resume
├── trajectories/      # logging (avoid naming a package "logging")
├── evaluation/        # task runner, simulated_user.py, metrics.py, plots.py
└── cli.py
tasks/                 # YAML task specs + fixtures
tests/
```

## 13. Model selection

- In November, write down the hardware (GPU, VRAM, RAM) and run a short test of 1–2 candidate vision-language models of a size that fits (e.g. Qwen-VL-family or UI-TARS-family) plus one text-only model.
- Pick based on: does it run natively on Windows, latency per step, JSON-output reliability, grounding on 20 hand-made screenshots.
- Many Notepad/Explorer steps can be solved from the UIA tree with a text model. Use the vision model where UIA is missing or conflicting. This also reduces latency.

## 14. Safety during development

- Run the agent in a **VM or a separate Windows user** with a throwaway working folder; fixtures are recreated before each task.
- **Global kill switch** hotkey (and a mouse-to-corner fail-safe).
- Allow-list of applications; refuse to act on windows outside it.
- Critical actions are blocked in evaluation; their correct handling is measured as "asked / refused".

## 15. Timeline (Nov 2026 – Jul 2027)

| Period | Work | Milestone |
|---|---|---|
| **Nov** | Hardware notes, model test, VM setup; schemas; task-spec format; simulated-user design; first 10 Notepad tasks | M0: specs and schemas frozen |
| **Dec** | Windows environment: observe (screenshot + UIA), actions, kill switch, before/after state, fixture setup | M1: scripted (no-model) run of a Notepad task, fully logged |
| **Jan** | Planner, executor (top-k candidates), orchestrator, post-action verification; File Explorer support | M2: base agent runs end-to-end on both apps |
| *Jan–Feb* | *Exam session: lighter workload, buffer* | |
| **Feb** | Critic: uncertainty indicators, risk rules, policy, structured questions, pause/resume | M3: selective agent works with the simulated user |
| **Mar** | Build the full 80-task suite, label it, split dev/test; tune thresholds on dev; never-ask baseline numbers | M4: frozen test set and thresholds |
| **Apr** | All configs × 3 runs, threshold sweep, ablations, calibration analysis; human pilot | M5: all core results and figures |
| **May** | One stretch item (browser, voice, conformal or external benchmark); start writing | M6: thesis draft |
| **Jun** | Writing, final runs if needed, slides, demo video | M7: submission |
| **Jul** | Buffer / defence | |

If behind schedule at M3: drop stretch items, reduce the suite to ~50 tasks, keep the four configs and the trade-off curve. Those are the minimum for the thesis claim.

## 16. Risks and mitigations

| Risk | Mitigation |
|---|---|
| Local model too weak or slow at grounding | Rely on UIA + text model; use the vision model only as fallback; keep tasks small |
| UIA tree incomplete for some controls | OCR fallback; this gap is itself a source-conflict signal |
| Results look trivial (never-ask fails ambiguous tasks by design) | Main claim is the trade-off curve vs. always-ask, plus calibration, not raw success |
| Overfitting rules to own tasks | Labels written before tuning; frozen dev/test split; second annotator |
| Non-deterministic runs | 3 runs per task, fixed seeds where possible, mean ± std |
| Scope creep | Stretch items only after M5 |

## 17. Thesis outline (draft)

1. Introduction — motivation, RQ, contributions
2. Related work — GUI agents; grounding; human-agent collaboration; uncertainty and asking for help
3. System design — environment, roles, schemas
4. Calibrated autonomy — uncertainty, risk, policy, questions
5. Benchmark and simulated user
6. Experiments — setup, configurations, results, trade-off curve, calibration, ablations
7. Discussion and limitations
8. Conclusion and future work (Linux adapter, voice, fine-tuning on trajectories, learned risk model)

## 18. Reading list

**Already selected:**
1. Zhang et al. — *Large Language Model-Brained GUI Agents: A Survey* — arXiv:2411.18279
2. Niu et al. — *ScreenAgent* — arXiv:2402.07945
3. *WebNav: An Intelligent Agent for Voice-Controlled Web Navigation* — arXiv:2503.13843
4. *CowPilot: A Framework for Autonomous and Human-Agent Collaborative Web Navigation* — arXiv:2501.16609
5. *UITron-Speech: Towards Automated GUI Agents Based on Speech Instructions* — arXiv:2506.11127
6. *SGGNet²: Speech-Scene Graph Grounding Network for Speech-guided Navigation* — arXiv:2307.07468

**To add:**
- Ren et al., 2023 — *Robots That Ask For Help: Uncertainty Alignment for LLM Planners* (conformal clarification)
- Angelopoulos & Bates — *A Gentle Introduction to Conformal Prediction*
- Guo et al., 2017 — *On Calibration of Modern Neural Networks* (ECE, reliability diagrams)
- Cheng et al., 2024 — *SeeClick* (introduces ScreenSpot)
- Bonatti et al., 2024 — *Windows Agent Arena*
- Zhang et al., 2024 — *UFO: A UI-Focused Agent for Windows OS Interaction* (closest Windows-native system)
- Xie et al., 2024 — *OSWorld* (interactive desktop benchmark design)

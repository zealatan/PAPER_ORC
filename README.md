# Multi-Agent Paper Importance Evaluation System

## 1. Overview

This document proposes a **Multi-Agent Paper Importance Evaluation System** designed to help researchers identify which papers are truly important for their own research projects.

Unlike ordinary paper summarization tools, this system does not simply answer:

> "What is this paper about?"

Instead, it answers a more practical research question:

> "How important is this paper for my current research direction, paper writing, experiment design, citation strategy, portfolio building, or patent exploration?"

The system is intended to function as a **research triage agent**. Given a paper, or a collection of candidate papers, it evaluates each paper using multiple specialized agents and generates a structured importance report.

The main goal is to reduce time spent reading low-value papers and increase the speed of building strong related work, baselines, experiments, and research positioning.

---

## 2. Motivation

Researchers are often overwhelmed by a large number of papers. Existing tools can help with paper discovery, citation search, or summarization, but they usually do not answer the most important practical question:

> "Should I actually spend time reading this paper?"

For example, a paper may be highly cited but not directly relevant to a specific project. Another paper may be weak academically but still useful as a baseline, experiment template, or motivation source.

Therefore, a paper evaluation system should consider not only generic paper quality, but also **project-specific importance**.

This system evaluates a paper based on the following dimensions:

- Topic relevance
- Novelty
- Technical depth
- Experimental value
- Citation value
- Strategic value
- Weakness and risk

The final output is not only a score, but also a concrete decision:

- Must Read
- High Priority
- Read Selectively
- Skim Only
- Citation Only
- Ignore

---

## 3. Key Idea

The key idea is to separate paper evaluation into multiple specialized agents.

Instead of asking one LLM to judge everything at once, each evaluation category is handled by an independent agent. Each agent produces evidence, reasoning, and a score. A final judge agent then combines the reports into a final importance decision.

```text
Paper PDF / arXiv Link / Metadata
        |
        v
Paper Parser Agent
        |
        v
Specialist Evaluation Agents
        |
        +--> Topic Relevance Agent
        +--> Novelty Agent
        +--> Technical Depth Agent
        +--> Experiment Value Agent
        +--> Citation Value Agent
        +--> Strategic Value Agent
        +--> Weakness / Risk Agent
        |
        v
Final Importance Judge Agent
        |
        v
Markdown Report + Ranking Table
```

This multi-agent structure makes the evaluation more transparent, reproducible, and useful than a single-pass summary.

---

## 4. Difference from Ordinary Paper Summarizers

Most paper summarizers focus on content extraction.

They answer:

```text
What problem does the paper solve?
What method does it propose?
What are the main results?
```

This system focuses on research decision-making.

It answers:

```text
Is this paper important for my current project?
Should I read it deeply or only skim it?
Can I cite it?
Can I use it as a baseline?
Can I reuse its metrics or experiment structure?
Does it reveal a research gap I can exploit?
Should I ignore it?
```

This distinction is critical. The goal is not simply to understand papers, but to **prioritize research effort**.

---

## 5. Relationship to Connected Papers

Connected Papers is a useful visual literature mapping tool. Given a seed paper, it generates a graph of related papers and helps researchers explore nearby works.

A simplified view of Connected Papers is:

```text
Seed Paper
   |
   v
Related Paper Graph
   |
   v
Prior Work / Similar Work / Derivative Work
```

Connected Papers is strong at **paper discovery**.

However, it does not fully answer:

```text
Which of these papers actually matter for my project?
Which ones should become baselines?
Which ones are citation-only?
Which ones can be ignored?
Which ones expose a gap for my own paper?
```

Therefore, this proposed system can be positioned as the next step after literature discovery.

```text
Connected Papers
= Finds related papers

Paper Importance Agent
= Decides which papers actually matter
```

A concise positioning statement is:

> Connected Papers finds related papers.  
> This system decides which papers are important for a specific research project.

The two systems are complementary:

```text
Seed Paper
   |
   v
Connected Papers / Semantic Scholar / Google Scholar
   |
   v
Candidate Paper List
   |
   v
Multi-Agent Paper Importance Evaluation System
   |
   v
Reading Priority + Citation Strategy + Experiment Ideas
```

---

## 6. Target Use Case

The system is especially useful for researchers who need to quickly build:

- Related work sections
- Baseline comparisons
- Experiment designs
- Research gap analysis
- Paper writing strategy
- Literature review reports
- Portfolio or patent-oriented technical positioning

An example target research direction is:

```text
LLM-orchestrated RTL/FPGA verification
AI-assisted hardware design
Simulation-to-synthesis-to-board feedback loop
Automated RTL debugging
FPGA board-level validation
Vivado/xsim/AXI/UART/register-log-based debugging
```

However, the framework is general. The project context can be replaced with any other research direction.

---

## 7. Agent Architecture

### 7.1 Paper Parser Agent

The Paper Parser Agent extracts and structures the content of a paper.

It does not evaluate the paper. Its role is only to organize the input.

#### Input

- PDF text
- arXiv metadata
- title and abstract
- optional citation information

#### Output

```markdown
# Parsed Paper Structure

## Title
...

## Authors
...

## Abstract
...

## Introduction
...

## Related Work
...

## Method
...

## Experiments
...

## Results
...

## Conclusion
...

## References
...
```

---

### 7.2 Topic Relevance Agent

The Topic Relevance Agent evaluates how closely the paper matches the user's current research direction.

#### Evaluation Questions

- Is the paper related to the user's target field?
- Does it address a similar problem?
- Does it share similar assumptions, methods, tools, or evaluation goals?
- Is the relevance direct or only superficial?

#### Example Relevance Keywords

```text
LLM-assisted verification
RTL generation
testbench generation
EDA automation
FPGA validation
board-level debugging
simulation-to-hardware mismatch
AXI / DMA / SoC debugging
research automation agent
```

#### Output

```markdown
# Topic Relevance Report

## Topic Relevance Score
- Score: 8 / 10
- Confidence: High

## Relevant Parts
- ...

## Irrelevant Parts
- ...

## Evidence
- ...

## Final Verdict
Directly Relevant / Partially Relevant / Weakly Relevant / Not Relevant
```

---

### 7.3 Novelty Agent

The Novelty Agent evaluates whether the paper contributes something genuinely new.

#### Evaluation Questions

- Does the paper introduce a new method?
- Does it introduce a new workflow, metric, benchmark, or system?
- Is the novelty technical or mostly packaging?
- Is the contribution incremental or fundamental?
- Does the paper overclaim its novelty?

#### Output

```markdown
# Novelty Report

## Novelty Score
- Score: 7 / 10
- Confidence: Medium

## Claimed Contributions
- ...

## Actual Contributions
- ...

## Incremental vs. Fundamental
- ...

## Potential Prior Work Overlap
- ...

## Final Verdict
Strong Novelty / Moderate Novelty / Incremental Novelty / Weak Novelty / No Clear Novelty
```

---

### 7.4 Technical Depth Agent

The Technical Depth Agent evaluates how technically substantial the paper is.

#### Evaluation Questions

- Are algorithms described clearly?
- Is there a system architecture?
- Are implementation details provided?
- Are mathematical formulations or pseudo-code included?
- Is the experimental setup reproducible?
- Is the paper more than a high-level concept?

#### Output

```markdown
# Technical Depth Report

## Technical Depth Score
- Score: 6.5 / 10
- Confidence: Medium

## Main Technical Components
- ...

## Implementation Details
- ...

## Missing Technical Details
- ...

## Reproducibility
- ...

## Final Verdict
Deep Technical Paper / Moderately Technical / High-level but Useful / Shallow
```

---

### 7.5 Experiment Value Agent

The Experiment Value Agent evaluates whether the paper's experiments are useful for the user's own research.

This is one of the most important agents because many papers are useful not because their method is strong, but because their experimental structure can be reused.

#### Evaluation Questions

- Are the experiments well designed?
- Are the baselines useful?
- Are the metrics reusable?
- Can the experiments be reproduced?
- Can the experiments be extended?
- Are there useful failure cases?
- Are the figures and tables useful as templates?

#### Output

```markdown
# Experiment Value Report

## Experiment Value Score
- Score: 8.5 / 10
- Confidence: High

## Useful Experimental Elements
- ...

## Reusable Metrics
- ...

## Reproducibility
- ...

## Extension Ideas
- ...

## Final Verdict
Very Useful Experiment Template / Useful Reference / Limited Experiment Value / Not Useful
```

---

### 7.6 Citation Value Agent

The Citation Value Agent evaluates how the paper can be used in the user's own paper.

#### Citation Categories

- Core Related Work
- Baseline
- Competitor
- Supporting Evidence
- Motivation Source
- Metric Source
- Benchmark Source
- Weak Citation
- Ignore

#### Output

```markdown
# Citation Value Report

## Citation Value Score
- Score: 7 / 10
- Confidence: High

## Citation Category
- Core Related Work
- Baseline Candidate

## Where to Use This Paper
- Introduction
- Related Work
- Experiment

## Possible Citation Sentence
Recent works have explored LLM-based RTL generation and verification, but most remain limited to simulation-only workflows.

## Citation Risk
- ...

## Final Verdict
Must Cite / Useful Citation / Optional Citation / Do Not Cite
```

---

### 7.7 Strategic Value Agent

The Strategic Value Agent evaluates whether the paper is useful for research positioning, portfolio building, patent thinking, or long-term technical strategy.

This is a project-specific agent. It is not a generic paper quality evaluator.

#### Evaluation Questions

- Does the paper help frame the user's own paper?
- Does it reveal a gap the user can exploit?
- Does it support the user's positioning?
- Does it suggest patentable or productizable ideas?
- Does it help build a strong portfolio narrative?
- Does it validate that the field is important?

#### Output

```markdown
# Strategic Value Report

## Strategic Value Score
- Score: 9 / 10
- Confidence: High

## Strategic Use
- ...

## Gap Opportunity
- ...

## Positioning Sentence
The user's work can be positioned as a board-feedback-aware extension beyond simulation-only LLM verification workflows.

## Portfolio / Patent Value
- ...

## Final Verdict
Strategically Critical / Strategically Useful / Somewhat Useful / Not Strategic
```

---

### 7.8 Weakness and Risk Agent

The Weakness and Risk Agent critically evaluates limitations of the paper.

This agent should be skeptical. Its job is not to praise the paper, but to identify missing evidence and overclaims.

#### Evaluation Questions

- Are the experiments weak?
- Is the benchmark too small?
- Are baselines missing?
- Are prompts or methods unclear?
- Is the work reproducible?
- Is hardware validation missing?
- Are claims exaggerated?
- Is the work limited to toy examples?

#### Output

```markdown
# Weakness and Risk Report

## Weakness Severity Score
- Score: 5 / 10
- Confidence: Medium

## Main Weaknesses
- ...

## Missing Evidence
- ...

## Overclaim Risk
Low / Medium / High

## Reproducibility Risk
Low / Medium / High

## How the User Can Improve Beyond This Paper
- ...

## Final Verdict
Reliable / Useful but Limited / Weak Evidence / High Risk
```

---

## 8. Final Importance Judge Agent

The Final Importance Judge Agent synthesizes the reports from all specialist agents.

It computes a final score and produces the final research decision.

### 8.1 Scoring Formula

```text
Final Score =
0.20 × Topic Relevance
0.15 × Novelty
0.15 × Technical Depth
0.15 × Experiment Value
0.15 × Citation Value
0.15 × Strategic Value
- 0.10 × Weakness Severity
```

The weakness score is used as a penalty.

### 8.2 Decision Rule

```text
8.5 - 10.0 : Must Read
7.0 - 8.4  : High Priority
5.5 - 6.9  : Read Selectively
4.0 - 5.4  : Skim Only
2.0 - 3.9  : Citation Only or Archive
0.0 - 1.9  : Ignore
```

### 8.3 Output

```markdown
# Final Paper Importance Report

## 1. Final Verdict
High Priority

## 2. Final Importance Score
- Final Score: 8.2 / 10
- Priority: High
- Confidence: High

## 3. Score Summary

| Category | Score | Weight | Contribution |
|---|---:|---:|---:|
| Topic Relevance | 9.0 | 0.20 | 1.80 |
| Novelty | 7.0 | 0.15 | 1.05 |
| Technical Depth | 6.5 | 0.15 | 0.98 |
| Experiment Value | 8.0 | 0.15 | 1.20 |
| Citation Value | 8.0 | 0.15 | 1.20 |
| Strategic Value | 9.0 | 0.15 | 1.35 |
| Weakness Severity | 5.0 | -0.10 | -0.50 |

## 4. Main Reason for Score
...

## 5. How This Paper Should Be Used
- Core Related Work
- Baseline
- Experiment Template
- Metric Source

## 6. Reading Plan
- Read Introduction deeply
- Read Method selectively
- Read Experiments deeply
- Skim Appendix

## 7. Action Items
1. Extract reusable metrics.
2. Compare against board-feedback-aware workflow.
3. Add to related work section.

## 8. One-line Strategic Summary
This paper is important because it validates the relevance of LLM-assisted verification, but leaves open the stronger board-feedback-aware research direction.
```

---

## 9. Recommended Repository Structure

A clean repository structure could look like this:

```text
paper_importance_agent/
├── README.md
├── papers/
│   ├── paper_001.pdf
│   └── paper_002.pdf
├── context/
│   └── project_context.md
├── prompts/
│   ├── parser_agent.md
│   ├── topic_relevance_agent.md
│   ├── novelty_agent.md
│   ├── technical_depth_agent.md
│   ├── experiment_value_agent.md
│   ├── citation_value_agent.md
│   ├── strategic_value_agent.md
│   ├── weakness_risk_agent.md
│   └── final_judge_agent.md
├── reports/
│   ├── paper_001/
│   │   ├── parsed_structure.md
│   │   ├── topic_relevance.md
│   │   ├── novelty.md
│   │   ├── technical_depth.md
│   │   ├── experiment_value.md
│   │   ├── citation_value.md
│   │   ├── strategic_value.md
│   │   ├── weakness_risk.md
│   │   └── final_report.md
│   └── ranking_table.csv
├── src/
│   ├── pdf_parser.py
│   ├── agent_runner.py
│   ├── scoring.py
│   ├── report_writer.py
│   └── main.py
└── examples/
    └── sample_report.md
```

---

## 10. Minimum Viable Product

The first version should be simple.

### MVP v0.1

#### Input

```text
papers/ folder containing PDF files
context/project_context.md
```

#### Processing

```text
1. Extract text from each PDF.
2. Extract title, abstract, introduction, method, experiment, conclusion.
3. Run each specialist agent.
4. Run final judge.
5. Generate Markdown reports.
6. Generate CSV ranking table.
```

#### Output

```text
reports/
├── paper_001/final_report.md
├── paper_002/final_report.md
└── ranking_table.csv
```

Example ranking table:

| Paper | Final Score | Priority | Use Type | Read Depth | Main Reason |
|---|---:|---|---|---|---|
| paper_001.pdf | 8.7 | Must Read | Baseline | Deep | Strong experiment template |
| paper_002.pdf | 6.1 | Read Selectively | Related Work | Skim | Useful citation, limited implementation |
| paper_003.pdf | 3.2 | Citation Only | Weak Citation | Abstract only | Low project relevance |

---

## 11. Example CLI Interface

A future command-line interface could look like this:

```bash
python -m paper_importance_agent scan ./papers \
  --context ./context/project_context.md \
  --output ./reports
```

Or:

```bash
paper-agent scan ./papers \
  --project-context ./context/project_context.md \
  --output ./reports
```

Expected output:

```text
[INFO] Found 12 PDF files.
[INFO] Parsing papers...
[INFO] Running specialist agents...
[INFO] Generating final reports...
[INFO] Writing ranking_table.csv...
[DONE] Reports saved to ./reports
```

---

## 12. Project Context File

The system should always use a project context file.

Example:

```markdown
# Project Context

## Current Research Direction

The current research direction is LLM-orchestrated RTL/FPGA verification.

The main idea is to treat the LLM not as a one-shot RTL generator, but as a verification orchestrator that coordinates:

- specification analysis
- RTL generation
- testbench generation
- simulation
- failure detection
- debugging
- patch generation
- synthesis check
- FPGA board execution
- board-level log feedback

## Important Keywords

- LLM-assisted RTL verification
- testbench generation
- FPGA validation
- AXI-Lite / AXI-Stream debugging
- Vivado xsim
- synthesis / implementation
- UART logs
- board-level status counters
- simulation-to-board mismatch

## Current Paper Goal

The current paper aims to compare:

1. Direct LLM-based RTL/testbench generation
2. Structured simulation-only LLM verification
3. Board-feedback-aware LLM verification

## Desired Evidence

- simulation pass/fail statistics
- debug iteration count
- failure localization accuracy
- synthesis warnings
- board-level execution logs
- AXI register dumps
- UART output
- status counter traces
```

---

## 13. Core Prompt Templates

### 13.1 Topic Relevance Agent Prompt

```markdown
# Role

You are a Topic Relevance Agent.

Your task is to judge how relevant the given paper is to the user's current research direction.

The user's research direction is:

- LLM-orchestrated RTL/FPGA verification
- AI-assisted hardware design
- simulation → synthesis → FPGA board feedback
- automated RTL debugging
- testbench generation
- Vivado/xsim/AXI/FPGA board-level validation
- evidence-driven debugging using logs, register dumps, UART outputs, and hardware counters

# Task

Analyze the paper and assign a Topic Relevance score from 0 to 10.

# Output Format

## Topic Relevance Score
- Score:
- Confidence:

## Relevant Parts
List the parts of the paper that are relevant to the user's work.

## Irrelevant Parts
List parts that are not relevant.

## Evidence
Quote or paraphrase specific evidence from the paper.

## Final Verdict
Choose one:
- Directly Relevant
- Partially Relevant
- Weakly Relevant
- Not Relevant
```

---

### 13.2 Novelty Agent Prompt

```markdown
# Role

You are a Novelty Evaluation Agent.

Your task is to determine whether the paper contains a genuinely novel idea, method, workflow, benchmark, metric, or system.

# Evaluation Criteria

Score from 0 to 10 based on:

1. Is the core idea new?
2. Is the method clearly different from prior work?
3. Does the paper introduce a new system architecture, benchmark, or evaluation protocol?
4. Is the novelty technical or just packaging?
5. Does the paper overclaim its novelty?

# Output Format

## Novelty Score
- Score:
- Confidence:

## Claimed Contributions
List the contributions claimed by the authors.

## Actual Contributions
Judge what is actually new.

## Incremental vs. Fundamental
Explain whether the novelty is incremental or fundamental.

## Potential Prior Work Overlap
Mention which types of prior work may overlap.

## Final Verdict
Choose one:
- Strong Novelty
- Moderate Novelty
- Incremental Novelty
- Weak Novelty
- No Clear Novelty
```

---

### 13.3 Final Judge Agent Prompt

```markdown
# Role

You are the Final Paper Importance Judge.

You will receive reports from multiple specialist agents:

1. Topic Relevance Agent
2. Novelty Agent
3. Technical Depth Agent
4. Experiment Value Agent
5. Citation Value Agent
6. Strategic Value Agent
7. Weakness/Risk Agent

Your task is to synthesize their findings and produce a final importance decision for the user.

# Scoring Formula

Use the following weighted formula:

Final Score =
0.20 × Topic Relevance
0.15 × Novelty
0.15 × Technical Depth
0.15 × Experiment Value
0.15 × Citation Value
0.15 × Strategic Value
- 0.10 × Weakness Severity

Normalize the final score to 0-10.

# Decision Rule

- 8.5 - 10.0: Must Read
- 7.0 - 8.4: High Priority
- 5.5 - 6.9: Read Selectively
- 4.0 - 5.4: Skim Only
- 2.0 - 3.9: Citation Only or Archive
- 0.0 - 1.9: Ignore

# Output Format

## 1. Final Verdict

Choose one:
- Must Read
- High Priority
- Read Selectively
- Skim Only
- Citation Only
- Ignore

## 2. Final Importance Score

- Final Score:
- Priority:
- Confidence:

## 3. Score Summary

| Category | Score | Weight | Contribution |
|---|---:|---:|---:|

## 4. Main Reason for Score

Explain the main reason behind the final score.

## 5. How This Paper Should Be Used

Choose all that apply:
- Core Related Work
- Baseline
- Competitor
- Experiment Template
- Metric Source
- Motivation Source
- Citation Only
- Ignore

## 6. Reading Plan

Tell the user which sections to read:
- Abstract
- Introduction
- Related Work
- Method
- Experiments
- Discussion
- Appendix

## 7. Action Items

Give concrete next actions:
1. ...
2. ...
3. ...

## 8. One-line Strategic Summary

Write one strong sentence explaining why this paper matters or does not matter for the user's work.
```

---

## 14. Future Extensions

After the MVP, the system can be extended in several directions.

### 14.1 Multi-Paper Ranking

Evaluate a folder of papers and rank them automatically.

```text
Must Read
High Priority
Read Selectively
Citation Only
Ignore
```

### 14.2 Related Work Builder

Automatically group papers into related work categories:

```text
LLM for RTL generation
LLM for testbench generation
EDA automation
Simulation-only verification
Hardware-in-the-loop validation
Automated debugging
```

### 14.3 Baseline Finder

Identify which papers can be used as baselines.

```text
Baseline Candidate
Competitor
Metric Source
Benchmark Source
```

### 14.4 Experiment Template Extractor

Extract reusable experiment designs:

```text
baseline comparison
ablation study
benchmark split
pass/fail metric
debug iteration count
failure localization accuracy
```

### 14.5 Research Gap Detector

Identify what existing papers do not address.

Example:

```text
Most existing LLM-for-HDL workflows focus on simulation-level correctness.
Few works incorporate synthesis feedback, implementation constraints, or board-level execution logs.
This creates an opportunity for board-feedback-aware LLM verification.
```

### 14.6 Citation Sentence Generator

Generate possible citation sentences for the user's paper.

Example:

```text
Recent works have explored LLM-assisted RTL generation and verification, but most remain limited to simulation-level evaluation and do not close the loop with FPGA board execution feedback.
```

---

## 15. Research and Product Positioning

This project can be positioned in two ways.

### 15.1 As a Research Tool

The system helps researchers decide which papers to read, cite, reproduce, or ignore.

Possible title:

```text
A Multi-Agent Research Triage System for Project-Specific Paper Importance Evaluation
```

### 15.2 As a Research Automation Component

The system can become one component of a larger research automation pipeline:

```text
Paper discovery
   |
   v
Importance evaluation
   |
   v
Related work generation
   |
   v
Experiment planning
   |
   v
Paper writing support
```

In this broader view, the system is not just a literature review assistant. It is part of an AI research orchestrator.

---

## 16. Conclusion

The proposed system is a **Multi-Agent Paper Importance Evaluation System**.

Its main purpose is to help researchers decide which papers matter for their specific research goals.

The core insight is:

> Paper discovery is not enough.  
> Researchers need project-specific importance judgment.

Connected Papers and similar tools help researchers discover related papers. This system takes the next step by deciding how each paper should be used:

- read deeply
- skim
- cite
- use as baseline
- reuse as experiment template
- exploit as research gap
- ignore

The final goal is to transform literature review from passive reading into an active, evidence-driven research decision process.

---

## 17. One-Line Summary

> This project builds a multi-agent research triage system that evaluates papers by project-specific importance, not just by generic relevance or citation count.

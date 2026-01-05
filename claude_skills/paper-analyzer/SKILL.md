---
name: paper-analyzer
description: Analyze academic papers for methodology, contributions, strengths, and weaknesses. Use when the user wants to understand a paper's approach, evaluate its quality, or identify limitations.
---

# Analyzing Academic Papers

This skill guides you through a comprehensive analysis of academic papers.

## When to Use

- User asks "What are the strengths/weaknesses of this paper?"
- User asks "Analyze this paper's methodology"
- User asks "What are the contributions of this paper?"
- User wants a critical review or evaluation

## Analysis Framework

### 1. Paper Overview

First, identify:
- **Title and authors** (if available)
- **Research domain/field** (ML, NLP, CV, systems, etc.)
- **Problem statement** - What problem does this paper address?
- **Paper type** - Is it proposing a new method, benchmark, analysis, or survey?

### 2. Methodology Analysis

For each method/approach proposed:

- **Core idea** - What is the key insight or innovation?
- **Technical approach** - How does it work at a high level?
- **Key components** - What are the main building blocks?
- **Novelty** - What's new compared to prior work?
- **Assumptions** - What assumptions does the method make?

### 3. Key Contributions

List contributions as the authors claim them, then evaluate:
- Are the claimed contributions accurate?
- Are they significant to the field?
- Are they well-supported by evidence?

### 4. Strengths

Evaluate positives in these categories:

**Technical:**
- Sound methodology
- Rigorous theoretical analysis
- Novel approach or insight

**Experimental:**
- Comprehensive experiments
- Strong baselines
- Ablation studies
- Statistical significance

**Presentation:**
- Clear writing
- Good visualizations
- Reproducibility details

### 5. Weaknesses & Limitations

Identify issues in these categories:

**Technical concerns:**
- Flawed assumptions
- Missing theoretical justification
- Scalability issues
- Computational cost

**Experimental gaps:**
- Missing baselines
- Limited datasets
- No ablation studies
- Cherry-picked results
- Missing error bars/significance tests

**Clarity issues:**
- Unclear explanations
- Missing details for reproduction
- Overclaimed contributions

**Scope limitations:**
- Narrow applicability
- Strong assumptions that limit use
- Missing failure case analysis

### 6. Technical Details to Extract

- Important equations and their meaning
- Architecture/algorithm specifics
- Hyperparameters and training details
- Dataset descriptions
- Evaluation metrics used

## Output Format

Structure your analysis as:

```
## Paper Overview
[Title, field, problem]

## Methodology
[Core approach and how it works]

## Key Contributions
1. [Contribution 1]
2. [Contribution 2]
...

## Strengths
- [Strength 1]
- [Strength 2]
...

## Weaknesses
- [Weakness 1]
- [Weakness 2]
...

## Technical Details
[Key equations, architecture, hyperparameters]

## Overall Assessment
[Brief summary: is this paper good? Should it be read? Cited?]
```

## Tips for Good Analysis

1. **Be objective** - Separate facts from opinions
2. **Be specific** - Point to specific sections/claims when critiquing
3. **Be balanced** - Every paper has both strengths and weaknesses
4. **Consider context** - A workshop paper has different standards than a journal
5. **Check claims vs evidence** - Are conclusions supported by experiments?

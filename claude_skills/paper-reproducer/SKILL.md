---
name: paper-reproducer
description: Generate pseudo-code and implementation code to reproduce methods from academic papers. Use when the user wants to implement a paper, write code for a paper's method, or understand how to reproduce results.
---

# Reproducing Academic Papers

This skill guides you through generating code to reproduce methods from academic papers.

## When to Use

- User asks "How do I implement this paper?"
- User asks "Generate code for this method"
- User asks "Write pseudo-code for this algorithm"
- User wants to reproduce paper results

## Code Generation Levels

### 1. Outline
High-level structure showing classes, functions, and their relationships.
- Good for: Understanding architecture, planning implementation

### 2. Pseudo-code
Algorithm-level detail with clear logic flow.
- Good for: Understanding the method, language-agnostic implementation

### 3. Detailed Implementation
Working code with proper imports, types, and documentation.
- Good for: Actual reproduction, starting point for experiments

## Implementation Workflow

### Step 1: Identify Key Components

From the paper, extract:
1. **Data pipeline** - How is data loaded, preprocessed, augmented?
2. **Model architecture** - What are the layers, modules, connections?
3. **Loss functions** - What objectives are optimized?
4. **Training procedure** - Optimizer, schedule, batch size, epochs?
5. **Evaluation** - What metrics? What test procedure?

### Step 2: Map to Code Structure

```
project/
├── data/
│   ├── dataset.py      # Data loading and preprocessing
│   └── transforms.py   # Data augmentation
├── models/
│   ├── model.py        # Main model architecture
│   └── layers.py       # Custom layers/modules
├── training/
│   ├── trainer.py      # Training loop
│   ├── losses.py       # Loss functions
│   └── optimizer.py    # Optimizer configuration
├── evaluation/
│   └── metrics.py      # Evaluation metrics
├── train.py            # Entry point for training
└── config.py           # Hyperparameters
```

### Step 3: Generate Code for Each Component

For each component, follow this pattern:

```python
"""
[Component Name]

From Section X.X of the paper:
"[Relevant quote from paper]"

Implements: [Equation number or algorithm name]
"""

# Code implementation here
```

## Code Templates by Domain

### Deep Learning (PyTorch)

```python
import torch
import torch.nn as nn

class PaperModel(nn.Module):
    """
    Implementation of [Paper Title]

    Paper: [URL or citation]

    Architecture:
        [Describe the architecture]
    """

    def __init__(self, config):
        super().__init__()
        # Initialize layers based on paper

    def forward(self, x):
        # Forward pass following paper's method
        return output
```

### Training Loop

```python
def train(model, dataloader, optimizer, criterion, device):
    """
    Training procedure from Section X.X

    Key details from paper:
    - Optimizer: [Adam/SGD/etc] with lr=[value]
    - Batch size: [value]
    - Training epochs: [value]
    """
    model.train()
    for batch in dataloader:
        optimizer.zero_grad()
        # Forward pass
        loss = criterion(output, target)
        loss.backward()
        optimizer.step()
```

### Loss Function

```python
class PaperLoss(nn.Module):
    """
    Loss function from Equation (X):

    L = [LaTeX or description of loss]

    Where:
    - term1: [explanation]
    - term2: [explanation]
    """

    def forward(self, pred, target):
        # Implement the loss
        return loss
```

## Handling Ambiguity

Papers often omit details. When this happens:

1. **State the assumption clearly**
   ```python
   # NOTE: Paper doesn't specify activation. Using ReLU (common default)
   ```

2. **Provide alternatives**
   ```python
   # Paper unclear. Options:
   # Option A: [implementation]
   # Option B: [implementation]
   # Using Option A based on [reasoning]
   ```

3. **Reference related work**
   ```python
   # Following [Other Paper] which uses similar approach
   ```

## Hyperparameter Extraction

Create a config section with all paper hyperparameters:

```python
# Hyperparameters from paper (Table X / Section X.X)
config = {
    # Model
    "hidden_dim": 512,        # Section 3.2
    "num_layers": 6,          # Section 3.2
    "num_heads": 8,           # Section 3.2

    # Training
    "learning_rate": 1e-4,    # Section 4.1
    "batch_size": 32,         # Section 4.1
    "epochs": 100,            # Section 4.1

    # Regularization
    "dropout": 0.1,           # Section 3.3
    "weight_decay": 1e-5,     # Section 4.1
}
```

## Output Format

Structure reproduction code as:

```
## Overview
[What this code implements]

## Dependencies
[Required packages with versions if known]

## Code

### 1. Configuration
[Hyperparameters]

### 2. Model
[Architecture implementation]

### 3. Training
[Training loop]

### 4. Evaluation
[Evaluation code]

## Usage Example
[How to run the code]

## Notes
- [Implementation detail 1]
- [Difference from paper, if any]
- [Potential issues]
```

## Tips

1. **Start with the algorithm box** - Many papers have algorithm pseudocode
2. **Check the appendix** - Implementation details often hidden there
3. **Look for official code** - Reference if available, note differences
4. **Test incrementally** - Verify each component before combining
5. **Match paper's framework** - If paper uses TensorFlow, consider matching

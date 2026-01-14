# Linux Command TUI Helper 🐧

An interactive terminal tool for learning Linux commands powered by Ollama LLM.

## Features

- **Tutorial Mode** - Get comprehensive tutorials for any Linux command
- **Step-by-Step Mode** - Receive actionable instructions for complex tasks
- **Follow-up Questions** - Ask clarifying questions and get context-aware answers
- **Beautiful TUI** - Clean interface powered by Rich library

## Installation

### Prerequisites

- Python 3.12+
- [Ollama](https://ollama.com/) installed and running

### Setup with uv (Recommended)

```bash
# Install uv if not already installed
curl -LsSf https://astral.sh/uv/install.sh | sh

# Clone and setup the project
cd tui-help

# Install dependencies
uv sync
```

### Setup with pip

```bash
# Install dependencies directly
pip install -r requirements.txt

# Or from pyproject.toml
pip install -e .
```

## Usage

### Start the application

```bash
uv run python main.py
```

### Commands

| Command | Description |
|---------|-------------|
| `tutorial <command>` | Get a tutorial for a specific command |
| `steps <task>` | Get step-by-step instructions for a task |
| `help` | Show help message |
| `quit` / `exit` | Exit the program |

### Examples

```bash
# Get a tutorial for grep
tutorial grep

# Get step-by-step instructions
steps configure ssh server

# Ask follow-up questions (after a tutorial)
what does -i option do?
how about -v flag?
```

## Configuration

### Changing the Ollama Model

Edit `main.py` and modify the `MODEL` variable:

```python
MODEL = "gemma3:12b"  # Change to your preferred model
```

### Ollama Setup

Make sure Ollama is running:

```bash
ollama serve
```

## Project Structure

```
tui-help/
├── main.py           # Main application
├── pyproject.toml    # Project configuration
├── README.md         # This file
└── .python-version  # Python version specification
```

## Dependencies

- `rich` - Terminal UI framework
- `requests` - HTTP client for Ollama API

Install with: `uv add rich requests`

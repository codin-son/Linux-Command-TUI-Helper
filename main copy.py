#!/usr/bin/env python3
"""
Linux Command TUI Helper - Interactive terminal tool for learning Linux commands
Requires: pip install rich requests
"""

import requests
import json
import sys
from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown
from rich.prompt import Prompt
from rich.live import Live
from rich.spinner import Spinner
from rich.text import Text

console = Console()

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL = "gemma3:12b"  # Change this to your preferred model

def check_ollama():
    """Check if Ollama is running"""
    try:
        response = requests.get("http://localhost:11434/api/tags", timeout=2)
        return response.status_code == 200
    except requests.exceptions.RequestException:
        return False

def ask_ollama(prompt, stream=True):
    """Send prompt to Ollama and get response"""
    payload = {
        "model": MODEL,
        "prompt": prompt,
        "stream": stream
    }
    
    try:
        response = requests.post(OLLAMA_URL, json=payload, stream=stream)
        if stream:
            full_response = ""
            for line in response.iter_lines():
                if line:
                    data = json.loads(line)
                    if "response" in data:
                        chunk = data["response"]
                        full_response += chunk
                        yield chunk
            return full_response
        else:
            return response.json().get("response", "")
    except Exception as e:
        console.print(f"[red]Error connecting to Ollama: {e}[/red]")
        return None

def format_tutorial_prompt(command):
    """Format the prompt for getting a tutorial"""
    return f"""Provide a concise, practical tutorial for the Linux command: {command}

Include:
1. Brief description (1-2 sentences)
2. Basic syntax
3. 3-5 most useful examples with explanations
4. Common options/flags
5. One tip or warning

Keep it practical and beginner-friendly. Use markdown formatting."""

def format_stepbystep_prompt(task):
    """Format the prompt for step-by-step instructions"""
    return f"""Provide clear step-by-step instructions for: {task}

Format as:
1. Step 1: [command] - explanation
2. Step 2: [command] - explanation
...

Include actual commands to run. Keep it concise and actionable. Use markdown formatting."""

def show_welcome():
    """Display welcome screen"""
    welcome = """
# Linux Command Helper 🐧

**Interactive TUI for learning Linux commands**

Available modes:
- `tutorial <command>` - Get a tutorial for a specific command
- `steps <task>` - Get step-by-step instructions for a task
- `help` - Show this help
- `quit` or `exit` - Exit the program

Examples:
- `tutorial grep`
- `steps configure ssh server`
"""
    console.print(Panel(Markdown(welcome), border_style="cyan"))

def main():
    """Main program loop"""
    console.clear()
    
    # Check Ollama connection
    if not check_ollama():
        console.print("[red]Error: Cannot connect to Ollama at http://localhost:11434[/red]")
        console.print("Make sure Ollama is running: [cyan]ollama serve[/cyan]")
        sys.exit(1)
    
    show_welcome()
    
    while True:
        try:
            # Get user input
            user_input = Prompt.ask("\n[bold cyan]λ[/bold cyan]").strip()
            
            if not user_input:
                continue
            
            if user_input.lower() in ["quit", "exit", "q"]:
                console.print("[yellow]Goodbye! 👋[/yellow]")
                break
            
            if user_input.lower() == "help":
                show_welcome()
                continue
            
            # Parse command
            parts = user_input.split(maxsplit=1)
            if len(parts) < 2:
                console.print("[yellow]Please specify a command or task. Try 'help' for examples.[/yellow]")
                continue
            
            mode, query = parts[0].lower(), parts[1]
            
            # Generate appropriate prompt
            if mode == "tutorial":
                prompt = format_tutorial_prompt(query)
                title = f"Tutorial: {query}"
            elif mode in ["steps", "step"]:
                prompt = format_stepbystep_prompt(query)
                title = f"Steps: {query}"
            else:
                console.print(f"[yellow]Unknown mode '{mode}'. Use 'tutorial' or 'steps'.[/yellow]")
                continue
            
            # Show loading indicator and get response
            console.print()
            full_response = ""
            
            with Live(Spinner("dots", text="Thinking..."), console=console, refresh_per_second=10):
                for chunk in ask_ollama(prompt):
                    full_response += chunk
            
            # Display response
            if full_response:
                console.print(Panel(Markdown(full_response), title=title, border_style="green"))
            else:
                console.print("[red]No response received from Ollama[/red]")
                
        except KeyboardInterrupt:
            console.print("\n[yellow]Use 'quit' or 'exit' to leave[/yellow]")
        except Exception as e:
            console.print(f"[red]Error: {e}[/red]")

if __name__ == "__main__":
    main()
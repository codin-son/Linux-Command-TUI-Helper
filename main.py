#!/usr/bin/env python3
"""
Linux Command TUI Helper - Interactive terminal tool for learning Linux commands
Requires: pip install rich requests
"""

import requests
import json
import sys
from datetime import datetime
from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown
from rich.prompt import Prompt
from rich.live import Live
from rich.spinner import Spinner
from rich.text import Text
from rich.table import Table
from rich.layout import Layout
from rich.align import Align
from rich import box

console = Console()

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL = "gemma3:12b"

# Color scheme
COLORS = {
    "primary": "cyan",
    "secondary": "blue",
    "success": "green",
    "warning": "yellow",
    "error": "red",
    "muted": "dim white",
    "highlight": "bright_cyan"
}

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
        console.print(f"[{COLORS['error']}]✗ Error connecting to Ollama: {e}[/{COLORS['error']}]")
        return None

def format_tutorial_prompt(command, conversation_history=""):
    """Format the prompt for getting a tutorial"""
    base_prompt = f"""Provide a concise, practical tutorial for the Linux command: {command}

Include:
1. Brief description (1-2 sentences)
2. Basic syntax
3. 3-5 most useful examples with explanations
4. Common options/flags
5. One tip or warning

Keep it practical and beginner-friendly. Use markdown formatting."""
    
    if conversation_history:
        base_prompt += f"\n\nPrevious conversation:\n{conversation_history}\n\nPlease answer the follow-up question above, maintaining context from the previous discussion."
    
    return base_prompt

def format_stepbystep_prompt(task, conversation_history=""):
    """Format the prompt for step-by-step instructions"""
    base_prompt = f"""Provide clear step-by-step instructions for: {task}

Format as:
1. Step 1: [command] - explanation
2. Step 2: [command] - explanation
...

Include actual commands to run. Keep it concise and actionable. Use markdown formatting."""
    
    if conversation_history:
        base_prompt += f"\n\nPrevious conversation:\n{conversation_history}\n\nPlease answer the follow-up question above, maintaining context from the previous discussion."
    
    return base_prompt

def format_followup_prompt(conversation_history, followup_question):
    """Format the prompt for follow-up questions"""
    return f"""You are helping a user learn Linux commands. Maintain context from the previous conversation and answer the follow-up question.

Previous conversation:
{conversation_history}

Follow-up question: {followup_question}

Provide a helpful, concise answer that builds on the previous context. Use markdown formatting where appropriate."""

def create_header():
    """Create an attractive header"""
    header_text = Text()
    header_text.append("╔═══════════════════════════════════════════════════════════╗\n", style="cyan")
    header_text.append("║  ", style="cyan")
    header_text.append("🐧 Linux Command Helper", style="bold bright_cyan")
    header_text.append("  ", style="cyan")
    header_text.append("─", style="dim cyan")
    header_text.append("  Learn. Explore. Master.  ", style="italic cyan")
    header_text.append(" ║\n", style="cyan")
    header_text.append("╚═══════════════════════════════════════════════════════════╝", style="cyan")
    return header_text

def create_command_table():
    """Create a table of available commands"""
    table = Table(
        show_header=True,
        header_style=f"bold {COLORS['primary']}",
        border_style=COLORS['primary'],
        box=box.ROUNDED,
        padding=(0, 1)
    )
    
    table.add_column("Command", style=COLORS['highlight'], width=20)
    table.add_column("Description", style="white")
    table.add_column("Example", style=COLORS['muted'])
    
    table.add_row(
        "tutorial <cmd>",
        "Learn about a command",
        "tutorial grep"
    )
    table.add_row(
        "steps <task>",
        "Get step-by-step guide",
        "steps setup nginx"
    )
    table.add_row(
        "<question>",
        "Ask follow-up questions",
        "what about permissions?"
    )
    table.add_row(
        "clear",
        "Clear the screen",
        "clear"
    )
    table.add_row(
        "help",
        "Show this help",
        "help"
    )
    table.add_row(
        "quit / exit",
        "Exit the program",
        "quit"
    )
    
    return table

def show_welcome():
    """Display enhanced welcome screen"""
    console.print("\n")
    console.print(create_header())
    console.print()
    
    # Quick tips
    tips_panel = Panel(
        "[dim]💡 Tip: Start with 'tutorial <command>' or 'steps <task>', then ask follow-ups![/dim]",
        border_style=COLORS['secondary'],
        box=box.ROUNDED
    )
    console.print(tips_panel)
    console.print()
    
    # Commands table
    console.print(create_command_table())
    console.print()

def show_context_bar(context):
    """Show current conversation context"""
    if context["mode"] and context["topic"]:
        context_text = Text()
        context_text.append("┃ ", style=COLORS['primary'])
        context_text.append("Context: ", style="dim")
        context_text.append(f"{context['mode'].title()}", style=f"bold {COLORS['highlight']}")
        context_text.append(" → ", style="dim")
        context_text.append(f"{context['topic']}", style=COLORS['success'])
        context_text.append(" ┃", style=COLORS['primary'])
        return Panel(
            context_text,
            border_style=COLORS['primary'],
            box=box.ROUNDED,
            padding=(0, 1)
        )
    return None

def show_thinking_animation(text="Processing your request"):
    """Create an enhanced loading animation"""
    spinners = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]
    return Spinner("dots", text=f"[{COLORS['primary']}]{text}...[/{COLORS['primary']}]", style=COLORS['primary'])

def format_response_panel(content, title, mode):
    """Format response with appropriate styling"""
    # Choose icon based on mode
    icons = {
        "tutorial": "📚",
        "steps": "📋",
        "followup": "💬"
    }
    icon = icons.get(mode, "💡")
    
    # Create title with icon
    panel_title = f"{icon} {title}"
    
    return Panel(
        Markdown(content),
        title=panel_title,
        title_align="left",
        border_style=COLORS['success'],
        box=box.ROUNDED,
        padding=(1, 2)
    )

def show_error(message):
    """Display error message"""
    error_text = Text()
    error_text.append("✗ ", style=f"bold {COLORS['error']}")
    error_text.append(message, style=COLORS['error'])
    
    console.print(Panel(
        error_text,
        border_style=COLORS['error'],
        box=box.ROUNDED
    ))

def show_info(message):
    """Display info message"""
    info_text = Text()
    info_text.append("ℹ ", style=f"bold {COLORS['primary']}")
    info_text.append(message, style=COLORS['primary'])
    
    console.print(Panel(
        info_text,
        border_style=COLORS['primary'],
        box=box.ROUNDED
    ))

def show_success(message):
    """Display success message"""
    success_text = Text()
    success_text.append("✓ ", style=f"bold {COLORS['success']}")
    success_text.append(message, style=COLORS['success'])
    
    console.print(Panel(
        success_text,
        border_style=COLORS['success'],
        box=box.ROUNDED
    ))

def main():
    """Main program loop"""
    console.clear()
    
    # Check Ollama connection with styled message
    console.print(f"\n[{COLORS['primary']}]⟳ Connecting to Ollama...[/{COLORS['primary']}]", end="")
    if not check_ollama():
        console.print(f" [{COLORS['error']}]✗[/{COLORS['error']}]")
        show_error("Cannot connect to Ollama at http://localhost:11434\nMake sure Ollama is running: ollama serve")
        sys.exit(1)
    console.print(f" [{COLORS['success']}]✓[/{COLORS['success']}]")
    
    show_welcome()
    
    # Conversation context tracking
    current_context = {"mode": None, "topic": "", "history": ""}
    
    while True:
        try:
            # Show context if available
            context_panel = show_context_bar(current_context)
            if context_panel:
                console.print(context_panel)
            
            # Enhanced prompt with color
            prompt_text = Text()
            prompt_text.append("┌─[", style=COLORS['primary'])
            prompt_text.append("λ", style=f"bold {COLORS['highlight']}")
            prompt_text.append("]", style=COLORS['primary'])
            console.print(prompt_text)
            
            user_input = Prompt.ask(
                f"[{COLORS['primary']}]└─▶[/{COLORS['primary']}]",
                default=""
            ).strip()
            
            if not user_input:
                continue
            
            if user_input.lower() in ["quit", "exit", "q"]:
                console.print(f"\n[{COLORS['warning']}]👋 Thanks for using Linux Command Helper! Happy learning![/{COLORS['warning']}]\n")
                break
            
            if user_input.lower() == "clear":
                console.clear()
                show_welcome()
                continue
            
            if user_input.lower() == "help":
                console.clear()
                show_welcome()
                continue
            
            # Check if it's a follow-up question
            is_followup = False
            
            # Parse command
            parts = user_input.split(maxsplit=1)
            if len(parts) < 2:
                if current_context["mode"] and current_context["topic"]:
                    is_followup = True
                    query = user_input
                else:
                    show_info("Please specify a command or task. Try 'help' for examples.")
                    continue
            else:
                mode, query = parts[0].lower(), parts[1]
                
                if mode not in ["tutorial", "steps", "step"]:
                    if current_context["mode"] and current_context["topic"]:
                        is_followup = True
                        query = user_input
                    else:
                        show_error(f"Unknown mode '{mode}'. Use 'tutorial', 'steps', or ask a follow-up question.")
                        continue
            
            # Generate appropriate prompt
            if is_followup:
                prompt = format_followup_prompt(current_context["history"], query)
                title = query[:50] + "..." if len(query) > 50 else query
                response_mode = "followup"
            elif mode == "tutorial":
                prompt = format_tutorial_prompt(query)
                title = f"Tutorial: {query}"
                response_mode = "tutorial"
                current_context = {"mode": "tutorial", "topic": query, "history": ""}
            elif mode in ["steps", "step"]:
                prompt = format_stepbystep_prompt(query)
                title = f"Steps: {query}"
                response_mode = "steps"
                current_context = {"mode": "steps", "topic": query, "history": ""}
            
            # Show loading indicator and get response
            console.print()
            full_response = ""
            
            with Live(show_thinking_animation(), console=console, refresh_per_second=10):
                for chunk in ask_ollama(prompt):
                    full_response += chunk
            
            # Display response
            if full_response:
                console.print(format_response_panel(full_response, title, response_mode))
                
                # Update conversation history
                if current_context["history"]:
                    current_context["history"] += f"\nUser: {query}\nAssistant: {full_response}\n"
                else:
                    current_context["history"] = f"Topic: {current_context['topic']}\nUser: {query}\nAssistant: {full_response}\n"
                
                console.print()
            else:
                show_error("No response received from Ollama. Please try again.")
                
        except KeyboardInterrupt:
            console.print(f"\n[{COLORS['warning']}]⚠ Interrupted. Use 'quit' or 'exit' to leave[/{COLORS['warning']}]")
        except Exception as e:
            show_error(f"Unexpected error: {e}")

if __name__ == "__main__":
    main()
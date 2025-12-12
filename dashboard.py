#!/usr/bin/env python3
"""CBORG Terminal Dashboard - Monitor your CBORG usage and models."""

import os
import sys
from datetime import datetime
from typing import Optional

from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.layout import Layout
from rich.text import Text
from rich import box
from dateutil import parser as date_parser

from cborg_api import CBORGClient
from storage import CBORGStorage


class CBORGDashboard:
    """Terminal dashboard for CBORG service."""

    def __init__(self, api_key: str):
        """Initialize dashboard."""
        self.console = Console()
        self.api_key = api_key
        self.client = CBORGClient(api_key)
        self.storage = CBORGStorage()

    def run(self):
        """Run the dashboard."""
        self.console.clear()

        # Show header
        self._show_header()

        # Test connection
        if not self._test_connection():
            return

        # Fetch and display data
        self._fetch_and_display_models()
        self._show_spend_info()
        self._show_footer()

    def _show_header(self):
        """Display dashboard header."""
        title = Text("CBORG Dashboard", style="bold cyan", justify="center")
        subtitle = Text(f"API Key: {self.api_key[:8]}...{self.api_key[-4:]}",
                       style="dim", justify="center")

        header = Panel(
            Text.assemble(title, "\n", subtitle),
            box=box.DOUBLE,
            border_style="cyan"
        )
        self.console.print(header)
        self.console.print()

    def _test_connection(self) -> bool:
        """Test API connection."""
        with self.console.status("[bold cyan]Connecting to CBORG API...", spinner="dots"):
            if not self.client.test_connection():
                self.console.print("[red]✗ Failed to connect to CBORG API[/red]")
                self.console.print("[yellow]Check your API key and internet connection[/yellow]")
                return False

        self.console.print("[green]✓ Connected to CBORG API[/green]")
        self.console.print()
        return True

    def _fetch_and_display_models(self):
        """Fetch models and display with new model highlighting."""
        with self.console.status("[bold cyan]Fetching models...", spinner="dots"):
            try:
                current_models = self.client.get_models()
                result = self.storage.update_models(self.api_key, current_models)
            except Exception as e:
                self.console.print(f"[red]Error fetching models: {e}[/red]")
                return

        # Show summary
        last_check = self.storage.get_last_check(self.api_key)
        if last_check:
            last_check_dt = date_parser.isoparse(last_check)
            last_check_str = self._format_relative_time(last_check_dt)
        else:
            last_check_str = "First check"

        summary = Table.grid(padding=(0, 2))
        summary.add_column(style="cyan", justify="right")
        summary.add_column(style="white")

        summary.add_row("Total Models:", str(result['total_count']))
        summary.add_row("New Models:", str(len(result['new_models'])))
        summary.add_row("Last Check:", last_check_str)

        self.console.print(Panel(summary, title="[bold]Model Summary[/bold]",
                                border_style="green", box=box.ROUNDED))
        self.console.print()

        # Show new models if any
        if result['new_models']:
            self._show_new_models(result['new_models'])
        else:
            self.console.print("[dim]No new models since last check[/dim]")
            self.console.print()

        # Show all models
        self._show_all_models(result['all_models'])

    def _show_new_models(self, new_models: list):
        """Display new models in a highlighted table."""
        table = Table(title="[bold yellow]🆕 New Models[/bold yellow]",
                     box=box.ROUNDED, border_style="yellow")
        table.add_column("#", style="dim", width=4)
        table.add_column("Model ID", style="yellow bold")

        for i, model in enumerate(new_models, 1):
            table.add_row(str(i), model)

        self.console.print(table)
        self.console.print()

    def _show_all_models(self, models: list):
        """Display all available models in a table."""
        table = Table(title="[bold]All Available Models[/bold]",
                     box=box.SIMPLE, border_style="blue",
                     show_lines=False)
        table.add_column("#", style="dim", width=4, justify="right")
        table.add_column("Model ID", style="cyan")

        # Group models by prefix for better organization
        for i, model in enumerate(models, 1):
            style = "cyan" if not model.startswith("lbl/") else "green"
            table.add_row(str(i), f"[{style}]{model}[/{style}]")

        self.console.print(table)
        self.console.print()

    def _show_spend_info(self):
        """Display spending information."""
        spend_info = self.client.get_spend_info()

        if spend_info and spend_info.get('current_spend') is not None:
            # Display actual spend data
            grid = Table.grid(padding=(0, 2))
            grid.add_column(style="cyan", justify="right")
            grid.add_column(style="white")

            current = spend_info.get('current_spend', 0)
            budget = spend_info.get('budget_limit')
            remaining = spend_info.get('remaining')

            grid.add_row("Current Spend:", f"${current:.2f}")

            if budget:
                grid.add_row("Budget Limit:", f"${budget:.2f}")
                grid.add_row("Remaining:", f"${remaining:.2f}")

                # Calculate and display usage percentage
                usage_pct = (current / budget * 100) if budget > 0 else 0

                # Color code based on usage
                if usage_pct >= 90:
                    usage_style = "red bold"
                elif usage_pct >= 75:
                    usage_style = "yellow bold"
                else:
                    usage_style = "green"

                grid.add_row("Usage:", f"[{usage_style}]{usage_pct:.1f}%[/{usage_style}]")

            if spend_info.get('key_alias'):
                grid.add_row("Key Alias:", spend_info['key_alias'])

            if spend_info.get('reset_date'):
                grid.add_row("Reset Date:", spend_info['reset_date'])

            self.console.print(Panel(grid, title="[bold]Spending Information[/bold]",
                                   border_style="magenta", box=box.ROUNDED))
        else:
            # Spend data not available
            info = Text.assemble(
                ("Unable to retrieve spending information\n", "yellow"),
                ("This may indicate an API issue or permissions problem.", "dim"),
            )
            self.console.print(Panel(info, title="[bold]Spending Information[/bold]",
                                   border_style="yellow", box=box.ROUNDED))

        self.console.print()

    def _show_footer(self):
        """Display footer with helpful information."""
        footer = Text.assemble(
            ("💡 Tip: ", "yellow bold"),
            ("Run this dashboard regularly to track new models and usage", "white"),
        )
        self.console.print(Panel(footer, border_style="dim", box=box.ROUNDED))

    def _format_relative_time(self, dt: datetime) -> str:
        """Format datetime as relative time string."""
        now = datetime.now(dt.tzinfo) if dt.tzinfo else datetime.now()
        diff = now - dt

        if diff.days > 0:
            return f"{diff.days} day{'s' if diff.days > 1 else ''} ago"
        elif diff.seconds >= 3600:
            hours = diff.seconds // 3600
            return f"{hours} hour{'s' if hours > 1 else ''} ago"
        elif diff.seconds >= 60:
            minutes = diff.seconds // 60
            return f"{minutes} minute{'s' if minutes > 1 else ''} ago"
        else:
            return "just now"


def main():
    """Main entry point."""
    api_key = os.environ.get('CBORG_API_KEY')

    if not api_key:
        console = Console()
        console.print("[red]Error: CBORG_API_KEY environment variable not set[/red]")
        console.print()
        console.print("Set your API key with:")
        console.print("  [cyan]export CBORG_API_KEY=your-key-here[/cyan]")
        sys.exit(1)

    dashboard = CBORGDashboard(api_key)
    dashboard.run()


if __name__ == "__main__":
    main()

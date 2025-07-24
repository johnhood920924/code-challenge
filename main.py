import click
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.panel import Panel

from ingestion import ingest_file
from parsing import parse_sections
from summarization import summarize_sections, format_summary, process_for_presentation
from ppt_generator import generate_ppt

console = Console()

@click.command()
@click.option('--input', prompt='📄 Path to CIM file (PDF or TXT)', help='Input CIM file path')
@click.option('--summary', prompt='📝 Output path for executive summary (e.g., summary.md)', help='Output summary file path')
@click.option('--ppt', prompt='📊 Output path for PowerPoint deck (e.g., deck.pptx)', help='Output PowerPoint file path')
def main(input, summary, ppt):
    console.print(Panel.fit("[bold cyan]CIM Summarizer & Mini Deck Generator[/bold cyan]\n[green]by Hopkins Coding Challenge[/green]", border_style="cyan"))

    with Progress(
        SpinnerColumn(style="magenta"),
        TextColumn("[progress.description]{task.description}"),
        transient=True,
        console=console
    ) as progress:
        task = progress.add_task("[yellow]Ingesting file...", start=False)
        progress.start_task(task)
        pdf_data = ingest_file(input)
        progress.update(task, description="[green]File ingested successfully!")
        progress.stop_task(task)

        task = progress.add_task("[yellow]Parsing sections...", start=False)
        progress.start_task(task)
        parsed_data = parse_sections(pdf_data)
        progress.update(task, description="[green]Sections parsed!")
        progress.stop_task(task)

        task = progress.add_task("[yellow]Summarizing sections...", start=False)
        progress.start_task(task)
        summary_dict = summarize_sections(parsed_data)
        progress.update(task, description="[green]Sections summarized!")
        progress.stop_task(task)

        task = progress.add_task("[yellow]Writing executive summary...", start=False)
        progress.start_task(task)
        formatted_summary = format_summary(summary_dict, parsed_data)
        with open(summary, 'w', encoding='utf-8') as f:
            f.write(formatted_summary)
        progress.update(task, description=f"[green]Executive summary saved to [bold]{summary}[/bold]")
        progress.stop_task(task)

        task = progress.add_task("[yellow]Generating PowerPoint deck...", start=False)
        progress.start_task(task)
        presentation_data = process_for_presentation(parsed_data)
        import json
        with open('pptx_data.json', 'w', encoding='utf-8') as f:
            json.dump(presentation_data, f, indent=2)
        generate_ppt(presentation_data, ppt)
        progress.update(task, description=f"[green]PowerPoint deck saved to [bold]{ppt}[/bold]")
        progress.stop_task(task)

    console.print(Panel.fit("[bold green]:sparkles: All done! :sparkles:[/bold green]\n\n[cyan]Thank you for using the CIM Summarizer.[/cyan]", border_style="green"))

if __name__ == '__main__':
    main()
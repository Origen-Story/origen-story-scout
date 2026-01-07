import click
import json
from datetime import datetime
from pathlib import Path
from rich.console import Console
from rich.table import Table
from .sources.rss import RSSSource
from .sources.base import ContentItem
from .processing.provenance import ProvenanceVerifier
from .processing.scorer import Scorer
from .processing.summarizer import Summarizer
from .output.report import ReportGenerator
from .storage.archive import Archive
from .config import settings

console = Console()


def safe_title(title: str, max_len: int = 60) -> str:
    """Sanitize title for Windows console output (remove problematic Unicode)."""
    # Encode to ascii, replacing problematic chars, then decode back
    safe = title[:max_len].encode('ascii', 'replace').decode('ascii')
    return safe


def fetch_gmail_newsletters() -> list:
    """Fetch newsletters from Gmail if configured."""
    if not settings.sources.gmail.enabled:
        return []

    try:
        from .sources.gmail import GmailSource, GMAIL_AVAILABLE
        if not GMAIL_AVAILABLE:
            console.print("[yellow]Gmail dependencies not installed. Skipping newsletters.[/yellow]")
            return []

        gmail = GmailSource(
            label_name=settings.sources.gmail.label_name,
            credentials_path=settings.sources.gmail.credentials_path
        )
        return gmail.fetch()
    except ImportError as e:
        console.print(f"[yellow]Gmail module not available: {e}[/yellow]")
        return []
    except Exception as e:
        console.print(f"[red]Error fetching Gmail newsletters: {e}[/red]")
        return []

def load_mock_data() -> list:
    """Load mock data for development mode"""
    mock_path = Path("data/mock_data.json")
    if not mock_path.exists():
        console.print("[red]Mock data file not found at data/mock_data.json[/red]")
        return []

    with open(mock_path, 'r') as f:
        data = json.load(f)

    items = []
    for story in data.get('stories', []):
        item = ContentItem(
            id=story['id'],
            title=story['title'],
            content=story['content'],
            url=story['url'],
            source_name=story['source_name'],
            source_category=story['source_category'],
            published_date=datetime.fromisoformat(story['published_date']),
            author=story.get('author'),
            metadata={'media_link': story.get('media_link')}
        )
        item.provenance_rating = story.get('provenance_rating', 'Unknown')
        items.append(item)

    return items

@click.group()
def cli():
    """AI Content Curator Agent CLI"""
    pass

@cli.command()
@click.option('--limit', default=10, help='Limit the number of items to display')
@click.option('--summarize', is_flag=True, help='Generate AI summaries')
@click.option('--force', is_flag=True, help='Re-process already archived items')
@click.option('--dev', is_flag=True, help='Use mock data instead of fetching RSS feeds')
def run(limit, summarize, force, dev):
    """Run the full curation pipeline"""
    console.print("[bold blue]Starting Origen Story Scout...[/bold blue]")

    # 1. Ingestion
    if dev:
        console.print("[yellow]Phase 1: Loading Mock Data (dev mode)...[/yellow]")
        all_items = load_mock_data()
        console.print(f"[green]Loaded {len(all_items)} mock items.[/green]")
    else:
        all_items = []

        # 1a. RSS Feeds
        console.print("[yellow]Phase 1a: Ingesting RSS Feeds...[/yellow]")
        rss = RSSSource()
        rss_items = rss.fetch()
        all_items.extend(rss_items)
        console.print(f"[green]Fetched {len(rss_items)} items from RSS feeds.[/green]")

        # 1b. Gmail Newsletters
        if settings.sources.gmail.enabled:
            console.print("[yellow]Phase 1b: Fetching Gmail Newsletters...[/yellow]")
            newsletter_items = fetch_gmail_newsletters()
            all_items.extend(newsletter_items)
            console.print(f"[green]Fetched {len(newsletter_items)} newsletters from Gmail.[/green]")

    # Check archive
    archive = Archive()

    # Prune old items from archive (older than 10 days)
    archive.prune_old_items(days=10)

    if not force:
        items = archive.filter_new(all_items)
        console.print(f"[green]Found {len(items)} new items out of {len(all_items)} total.[/green]")
    else:
        items = all_items
        console.print(f"[yellow]Forcing re-process of {len(items)} items.[/yellow]")

    if not items:
        console.print("[bold green]Everything is up to date! No new stories to scout.[/bold green]")
        return

    # 2. Fast Keyword Scoring (Filter)
    console.print("[yellow]Phase 2: Fast Filtering...[/yellow]")
    scorer = Scorer()
    
    potential_items = []
    for item in items:
        if scorer.is_potentially_relevant(item):
            potential_items.append(item)
    
    console.print(f"[green]Found {len(potential_items)} potentially relevant items.[/green]")

    if not potential_items:
        console.print("[yellow]No new items matched your interest topics.[/yellow]")
        # Still mark as processed so we don't look at them again
        for item in items:
            archive.mark_processed(item)
        return

    # 3. Provenance Verification (only for potential items)
    console.print("[yellow]Phase 3: Verifying Provenance (C2PA)...[/yellow]")
    pv = ProvenanceVerifier()
    pv.process_batch(potential_items)
    
    # 4. Detailed Scoring & Ranking
    console.print("[yellow]Phase 4: Detailed Scoring & Ranking (may take a few minutes)...[/yellow]")

    # Fast sorting by keyword baseline score first
    potential_items.sort(key=lambda x: scorer._get_keyword_baseline(x), reverse=True)
    top_candidates = potential_items[:30]

    for i, item in enumerate(top_candidates):
        console.print(f"  [{i+1}/{len(top_candidates)}] Scoring: {safe_title(item.title)}...")
        item.relevance_score = scorer.score_item(item)

    ranked_items = sorted(top_candidates, key=lambda x: x.relevance_score, reverse=True)
    
    # 5. Summarization (Optional)
    # We summarize the top 9 for the main grid
    num_to_summarize = 9
    top_items = [i for i in ranked_items if i.relevance_score >= settings.interests.preferences.min_relevance_score][:num_to_summarize]
    
    if summarize and top_items:
        console.print(f"[yellow]Phase 5: Generating Summaries for top {len(top_items)} items...[/yellow]")
        summ = Summarizer()
        for i, item in enumerate(top_items):
            console.print(f"  [{i+1}/{len(top_items)}] Summarizing: {safe_title(item.title)}...")
            summ.process_batch([item])
    
    # After processing, mark everything in this batch as processed
    for item in items:
        archive.mark_processed(item)

    # 6. Save Report for UI (Top 30 for Grid + List)
    rg = ReportGenerator()
    report_path = rg.generate_json_report(ranked_items[:30])
    console.print(f"\n[bold green]Report saved to {report_path}[/bold green]")

if __name__ == '__main__':
    cli()

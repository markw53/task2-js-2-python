"""Transform package — TOC generation, HTML conversion, statistics."""

from mdforge.transform.toc import generate_toc
from mdforge.transform.html import to_html
from mdforge.transform.stats import compute_stats, aggregate_stats

__all__ = ["generate_toc", "to_html", "compute_stats", "aggregate_stats"]
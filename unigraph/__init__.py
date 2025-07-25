"""
DeepWiki Parser: A tool for extracting structured information from codebases.

This package provides functionality to parse repositories and extract nodes and edges
representing code structure, dependencies, and relationships.
"""

__version__ = "0.1.0"
__author__ = "Anh Nguyen Hoang"
__email__ = "anh.nh204511@gmail.com"

from .parsing.repository import RepositoryParser, parse_repository_incrementally
from .core.models import Node, Edge

__all__ = [
    "RepositoryParser",
    "parse_repository_incrementally", 
    "Node",
    "Edge"
] 
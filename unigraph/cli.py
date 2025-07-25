"""
Command-line interface for UniGraph.

This module provides the main CLI entry point for parsing repositories.
"""

import argparse
import asyncio
import sys
from pathlib import Path
import traceback
import logging

from .parsing.repository import parse_repository_incrementally
from .utils.logger import logger, set_log_level
from .analyzing import FileSummaryAnalyzer, DefinitionAnalyzer


def validate_repo_path(repo_path: str) -> Path:
    """Validate that the repository path exists and is a directory."""
    path = Path(repo_path).resolve()
    if not path.exists():
        logger.debug(f"Repository path does not exist: {path}")
        sys.exit(1)
    
    if not path.is_dir():
        logger.debug(f"Repository path is not a directory: {path}")
        sys.exit(1)
    
    return path


def create_parser() -> argparse.ArgumentParser:
    """Create and configure the argument parser."""
    parser = argparse.ArgumentParser(
        description="Parse repositories to extract code structure and relationships",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    # Create subparsers for different commands
    subparsers = parser.add_subparsers(dest='command', help='Available commands')

    # Full parse subcommand
    parse_parser = subparsers.add_parser(
        'parse', 
        help='Parse entire repository from scratch',
        description='Parse the entire repository, processing all supported files'
    )
    
    # Required arguments
    parse_parser.add_argument(
        "--repo-path", 
        required=True, 
        type=str,
        help="The absolute directory to the repository to parse"
    )

    parse_parser.add_argument(
        "--output-dir", 
        type=str, 
        required=True,
        help="The absolute path to the output directory"
    )

    parse_parser.add_argument(
        "--file-paths",
        type=str,
        required=False,
        default=[],
        help="The absolute paths to the files to parse. If not provided, all files in the repository will be parsed."
    )
    
    parse_parser.add_argument(
        "--max-concurrent", 
        type=int, 
        default=5,
        help="Maximum number of files to process concurrently (default: 5)"
    )

    parse_parser.add_argument(
        "--log-level",
        type=str,
        default="INFO",
        help="The log level to use. Can be DEBUG, INFO, WARNING, ERROR, CRITICAL"
    )
    
    
    # File summary subcommand
    file_summary_parser = subparsers.add_parser(
        'file-summary',
        help='Generate file summary with elide messages',
        description='Generate a summary of a file showing only first lines of nodes with elide messages'
    )
    file_summary_parser.add_argument(
        "--repo-path",
        required=True,
        type=str,
        help="The absolute directory to the repository to parse"
    )
    file_summary_parser.add_argument(
        "--output-dir",
        type=str, 
        required=True,
        help="The absolute path to the output directory"
    )
    file_summary_parser.add_argument(
        "--file-path",
        required=True,
        type=str,
        help="Path to the file to summarize (relative to repo or absolute)"
    )
    
    # Get definition subcommand
    get_definition_parser = subparsers.add_parser(
        'get-definition',
        help='Get detailed definition analysis for a specific node',
        description='Analyze a specific node by file path and name, showing code snippet, dependencies, and dependents'
    )
    get_definition_parser.add_argument(
        "--repo-path",
        required=True,
        type=str,
        help="The absolute directory to the repository to parse"
    )
    get_definition_parser.add_argument(
        "--output-dir",
        type=str, 
        required=True,
        help="The absolute path to the output directory"
    )
    get_definition_parser.add_argument(
        "--file-path",
        required=True,
        type=str,
        help="Absolute path to the file containing the node"
    )
    get_definition_parser.add_argument(
        "--node-name",
        required=True,
        type=str,
        help="Name of the node (e.g., 'SearchProvider', 'ClassName.method_name')"
    )
    
    # Legacy support: if no subcommand is provided, default to parse
    parser.set_defaults(command='parse')
    
    return parser


async def run_file_summary(args: argparse.Namespace) -> None:
    """Run file summary analysis."""
    try:
        args.file_paths = [args.file_path]
        args.max_concurrent = 1
        aggregated_results_path = await run_parser(args)

        # Create analyzer
        analyzer = FileSummaryAnalyzer.from_aggregated_results(aggregated_results_path)
        
        # Run analysis
        summary = analyzer.analyze_file_summary(file_path=args.file_path)
        
        # Format result
        print(analyzer.format_file_summary(summary))
        
    except KeyboardInterrupt:
        logger.debug("🛑 Analysis interrupted by user")
        sys.exit(130)
    except Exception as e:
        logger.debug(f"❌ File summary failed with error: {e}")
        logger.error(traceback.format_exc())
        sys.exit(1)


async def run_get_definition(args: argparse.Namespace) -> None:
    """Run definition analysis."""
    try:
        args.file_paths = [args.file_path]
        args.max_concurrent = 1
        aggregated_results_path = await run_parser(args)
        
        # Create analyzer
        analyzer = DefinitionAnalyzer.from_aggregated_results(str(aggregated_results_path), on_demand=True)
        
        # Run analysis
        analysis = analyzer.get_definition_analysis(
            absolute_file_path=args.file_path,
            node_name=args.node_name
        )
        
        # Format and print result
        print(analyzer.format_definition_analysis(analysis))
        
        logger.debug(f"✅ Definition analysis completed successfully!")
        
    except KeyboardInterrupt:
        logger.debug("🛑 Analysis interrupted by user")
        sys.exit(130)
    except Exception as e:
        logger.debug(f"❌ Definition analysis failed with error: {e}")
        logger.error(traceback.format_exc())
        sys.exit(1)


async def run_parser(args: argparse.Namespace) -> None:
    """Run the repository parser with the given arguments."""
    try:
        # Run incremental update
        output_file = await parse_repository_incrementally(
            repo_path=str(args.repo_path),
            output_dir=args.output_dir,
            file_paths=args.file_paths,
            max_concurrent=args.max_concurrent
        )
        
        if output_file:
            logger.debug(f"✅ Incremental repository update completed successfully!")
            logger.debug(f"📁 Results saved to: {output_file}")
        else:
            logger.warning("⚠️  Incremental update completed but no output file was generated")
        
        return output_file

    except KeyboardInterrupt:
        logger.debug("🛑 Parser interrupted by user")
        sys.exit(130)
    except Exception as e:
        logger.debug(f"❌ Parser failed with error: {e}")
        logger.error(traceback.format_exc())
        sys.exit(1)


def main() -> None:
    """Main entry point for the CLI."""
    parser = create_parser()
    
    # Handle legacy usage (no subcommand) by checking if first arg looks like --repo-path
    if len(sys.argv) > 1 and not sys.argv[1] in ['parse', 'file-summary', 'get-definition', '-h', '--help']:
        # Legacy usage - insert 'parse' as the default command
        sys.argv.insert(1, 'parse')
    
    args = parser.parse_args()

    # set_log_level(logging.DEBUG)

    if args.command == 'file-summary':
        try:
            asyncio.run(run_file_summary(args))
        except Exception as e:
            logger.debug(f"❌ Fatal error: {e}")
            sys.exit(1)
    elif args.command == 'get-definition':
        try:
            asyncio.run(run_get_definition(args))
        except Exception as e:
            logger.debug(f"❌ Fatal error: {e}")
            sys.exit(1)
    else:
        # Parse and update commands need repo validation and API key
        args.repo_path = validate_repo_path(args.repo_path)
        
        # Print startup info
        logger.debug(f"🚀 Starting Universal Parser")
        logger.debug(f"📂 Repository: {args.repo_path}")
        logger.debug(f"🏷️  Output Directory: {args.output_dir}")
        logger.debug(f"⚡ Concurrency: {args.max_concurrent}")
        
        # Run the parser
        try:
            set_log_level(logging.getLevelName(args.log_level.upper()))
            asyncio.run(run_parser(args))
        except Exception as e:
            logger.debug(f"❌ Fatal error: {e}")
            sys.exit(1)


if __name__ == "__main__":
    main() 
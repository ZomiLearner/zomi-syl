#!/usr/bin/env python3
"""
Zomi Syllabifier CLI

This CLI provides:
    • syllabification
    • analysis
    • batch processing
    • benchmarking
    • model management
    • profile management
    • dataset management
    • config management
    • cache management
    • validation
    • downloads

All heavy lifting is delegated to internal modules:
    zomi_syl.core.pipeline
    zomi_syl.core.engine
    zomi_syl.batch.processor
    zomi_syl.evaluation.benchmark
    zomi_syl.registry.models
    zomi_syl.registry.profiles
    zomi_syl.datasets.manager
    zomi_syl.config.manager
    zomi_syl.models.downloader
"""

import argparse
import sys
import json


from zomi_syl.core.pipeline import run_pipeline
from zomi_syl.registry.models import (
    list_models,
    get_model_info,
)
from zomi_syl.registry.profiles import (
    list_profiles,
    load_profile,
)
from zomi_syl.models.downloader import download_model
from zomi_syl.models.cache import (
    clear_cache,
    remove_model,
    get_cache_dir,
)
from zomi_syl.config.manager import (
    load_config,
    save_config,
    get_config_path,
)
from zomi_syl.batch.processor import run_batch
from zomi_syl.evaluation.benchmark import run_benchmark
# from zomi_syl.logging_config import get_logger

# logger = get_logger(__name__)
import logging
logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Command registration
# ---------------------------------------------------------------------------


def register_commands(parser: argparse.ArgumentParser):
    sub = parser.add_subparsers(dest="command")

    # syllabify
    p = sub.add_parser("syllabify", help="Syllabify a single word")
    p.add_argument("word")
    p.add_argument("--backend", default="auto")
    p.add_argument("--profile", default="auto")
    p.add_argument("--json", action="store_true")
    p.add_argument("--compact", action="store_true")

    # analyze
    p = sub.add_parser("analyze", help="Detailed analysis")
    p.add_argument("word")
    p.add_argument("--backend", default="auto")
    p.add_argument("--profile", default="auto")

    # batch
    p = sub.add_parser("batch", help="Batch syllabification")
    p.add_argument("file")
    p.add_argument("--output")
    p.add_argument("--format", choices=["text", "jsonl", "csv"], default="text")
    p.add_argument("--workers", type=int, default=1)
    p.add_argument("--progress", action="store_true")

    # benchmark
    p = sub.add_parser("benchmark", help="Run evaluation benchmark")
    p.add_argument("--backend", default="auto")
    p.add_argument("--dataset", default="auto")
    p.add_argument("--report")

    # models
    p = sub.add_parser("models", help="Manage models")
    p.add_argument("action", choices=["list", "info", "download", "remove", "verify"])
    p.add_argument("name", nargs="?")

    # profiles
    p = sub.add_parser("profiles", help="Manage profiles")
    p.add_argument("action", choices=["list", "info", "validate"])
    p.add_argument("name", nargs="?")

    # datasets
    p = sub.add_parser("datasets", help="Manage datasets")
    p.add_argument("action", choices=["list", "download", "validate"])
    p.add_argument("name", nargs="?")

    # config
    p = sub.add_parser("config", help="View or modify config")
    p.add_argument("action", choices=["show", "path", "validate", "set"])
    p.add_argument("key", nargs="?")
    p.add_argument("value", nargs="?")

    # cache
    p = sub.add_parser("cache", help="Manage cache")
    p.add_argument("action", choices=["info", "clear", "remove"])
    p.add_argument("name", nargs="?")

    # validate
    p = sub.add_parser("validate", help="Validate resources")
    p.add_argument("target", nargs="?", default="all")

    # download
    p = sub.add_parser("download", help="Download a model")
    p.add_argument("name")

    # version
    sub.add_parser("version", help="Show version")


# ---------------------------------------------------------------------------
# Command handlers
# ---------------------------------------------------------------------------


def cmd_syllabify(args):
    result = run_pipeline(
        args.word,
        model=args.backend,
        dialect=args.profile,
        include_metadata=False,
    )

    # print(type(result), result.to_json(indent=2))

    # if args.json:
    #     print(result.to_json(indent=2))

    # elif args.compact:

    #     print(result.joined.replace("-", "."))
    # else:
    #     print(result.joined)
    # Use the backend syllables, not the fallback formatter
    # output = "-".join(result.syllables)
    output = result.syllables

    if args.json:
        print(result.to_json(indent=2))
    elif args.compact:
        print(output.replace("-", "."))
    else:
        print(output)


def cmd_analyze(args):
    result = run_pipeline(
        args.word,
        model=args.backend,
        dialect=args.profile,
        include_metadata=True,
    )
    # print(result.to_json(indent=2))
    if args.json:
        print(result.to_json(indent=2))
    elif args.compact:
        print(result.joined.replace("-", "."))
    else:
        print(result.joined)


def cmd_batch(args):
    run_batch(
        file_path=args.file,
        output=args.output,
        fmt=args.format,
        workers=args.workers,
        show_progress=args.progress,
    )


def cmd_benchmark(args):
    report = run_benchmark(
        backend=args.backend,
        dataset=args.dataset,
        report_path=args.report,
    )
    print(report)


def cmd_models(args):
    if args.action == "list":
        for m in list_models():
            print(m)

    elif args.action == "info":
        info = get_model_info(args.name)
        print(json.dumps(info, indent=2))

    elif args.action == "download":
        download_model(args.name)
        print(f"Downloaded model: {args.name}")

    elif args.action == "remove":
        remove_model(args.name)
        print(f"Removed model: {args.name}")

    elif args.action == "verify":
        print("Model verification not implemented yet")


def cmd_profiles(args):
    if args.action == "list":
        for p in list_profiles():
            print(p)

    elif args.action == "info":
        print(json.dumps(load_profile(args.name), indent=2))

    elif args.action == "validate":
        load_profile(args.name)
        print("Profile OK")


def cmd_datasets(args):
    print("Dataset management not implemented yet")


def cmd_config(args):
    cfg = load_config()

    if args.action == "show":
        print(json.dumps(cfg, indent=2))

    elif args.action == "path":
        print(get_config_path())

    elif args.action == "validate":
        print("Config OK")

    elif args.action == "set":
        cfg[args.key] = args.value
        save_config(cfg)
        print("Updated config")


def cmd_cache(args):
    if args.action == "info":
        print(f"Cache: {get_cache_dir()}")

    elif args.action == "clear":
        clear_cache()
        print("Cache cleared")

    elif args.action == "remove":
        remove_model(args.name)
        print(f"Removed cached model: {args.name}")


def cmd_validate(args):
    print("Validation not implemented yet")


def cmd_download(args):
    download_model(args.name)
    print(f"Downloaded model: {args.name}")


def cmd_version(args):
    from zomi_syl import __version__

    print(f"zomi-syl {__version__}")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main():
    parser = argparse.ArgumentParser(prog="zomi-syl", description="Zomi Syllabifier CLI")
    register_commands(parser)
    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    dispatch = {
        "syllabify": cmd_syllabify,
        "analyze": cmd_analyze,
        "batch": cmd_batch,
        "benchmark": cmd_benchmark,
        "models": cmd_models,
        "profiles": cmd_profiles,
        "datasets": cmd_datasets,
        "config": cmd_config,
        "cache": cmd_cache,
        "validate": cmd_validate,
        "download": cmd_download,
        "version": cmd_version,
    }

    try:
        dispatch[args.command](args)
    except Exception as e:
        print("\nERROR:")
        print(str(e))
        sys.exit(1)


if __name__ == "__main__":
    main()

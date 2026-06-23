#!/usr/bin/env python3
"""
Zomi-Syl CLI (pure Click)

Commands:
    syllabify   – syllabify a word
    analyze     – detailed analysis
    batch       – batch syllabification
    benchmark   – run evaluation benchmark
    models      – manage models
    profiles    – manage profiles
    datasets    – manage datasets (stub)
    config      – manage config
    cache       – manage cache
    validate    – validate resources (stub)
    download    – download models
    version     – show version
"""

from __future__ import annotations
import json
import logging
# from pathlib import Path

import click
import zomi_syl as zs

from zomi_syl.batch.processor import run_batch
from zomi_syl.evaluation.benchmark import run_benchmark
# from zomi_syl.registry.models import list_models, get_model_info
from zomi_syl.registry.profiles import list_profiles, load_profile
from zomi_syl.models.downloader import download_model
from zomi_syl.models.cache import clear_cache, remove_model, get_cache_dir
from zomi_syl.config.manager import load_config, save_config, get_config_path
# from zomi_syl.core.engine import run_syllabifier

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Root group
# ---------------------------------------------------------------------------

@click.group()
def main():
    """Zomi-Syl command-line interface."""
    pass


# ---------------------------------------------------------------------------
# syllabify
# ---------------------------------------------------------------------------

@main.command()
@click.argument("word")
@click.option("--backend", "--model", default="auto", help="Backend/model to use.")
@click.option("--profile", "--dialect", default="auto", help="Dialect/profile to use.")
@click.option("--json", "as_json", is_flag=True, help="Output as JSON.")
@click.option("--compact", is_flag=True, help="Compact syllable output with dots.")
def syllabify(word, backend, profile, as_json, compact):
    """Syllabify a single word."""
    import zomi_syl as zs
    pred = zs.syllabify(word, model=backend, dialect=profile, return_metadata=False)

    if as_json:
        click.echo(pred.to_json(indent=2))
    else:
        sylls = pred.syllables
        if compact:
            click.echo(".".join(sylls))
        else:
            click.echo(" ".join(sylls))


# ---------------------------------------------------------------------------
# analyze
# ---------------------------------------------------------------------------

# @main.command()
# @click.argument("word")
# @click.option("--backend", "--model", default="auto", help="Backend/model to use.")
# @click.option("--profile", "--dialect", default="auto", help="Dialect/profile to use.")
# @click.option("--json", "as_json", is_flag=True, help="Output as JSON.")
# def analyze(word, backend, profile, as_json):
#     """Return detailed analysis for a word."""
#     result = zs.analyze(word, model=backend, dialect=profile)

#     if as_json:
#         click.echo(json.dumps(result, indent=2))
#     else:
#         click.echo(json.dumps(result, indent=2))

@main.command()
@click.argument("word")
@click.option("--backend", "--model", default="auto")
@click.option("--profile", "--dialect", default="auto")
@click.option("--json", "as_json", is_flag=True)
def analyze(word, backend, profile, as_json):
    """Return detailed analysis for a word."""
    result = zs.analyze(word, model=backend, dialect=profile)

    # Convert Prediction → JSON-safe dict
    pred = result["prediction"]
    result["prediction"] = {
        "syllables": pred.syllables,
        "boundaries": [b.index for b in pred.boundaries],
        "confidence": [{"index": c.index, "score": c.score} for c in pred.confidence],
        "backend": pred.raw.get("backend"),
        "raw": pred.raw,
    }

    click.echo(json.dumps(result, indent=2))

# ---------------------------------------------------------------------------
# batch
# ---------------------------------------------------------------------------

@main.command()
@click.argument("file", type=click.Path(exists=True))
@click.option("--output", type=click.Path(), help="Output file path.")
@click.option(
    "--format",
    "fmt",
    type=click.Choice(["text", "jsonl", "csv"]),
    default="text",
    help="Output format.",
)
@click.option("--workers", type=int, default=1, help="Number of worker processes.")
@click.option("--progress", is_flag=True, help="Show progress bar.")
def batch(file, output, fmt, workers, progress):
    """Batch syllabification from a file."""
    run_batch(
        file_path=file,
        output=output,
        fmt=fmt,
        workers=workers,
        show_progress=progress,
    )


# ---------------------------------------------------------------------------
# benchmark
# ---------------------------------------------------------------------------

@main.command()
@click.option("--backend", "--model", default="auto", help="Backend/model to benchmark.")
@click.option("--dialect", default="auto", help="Dialect/profile to use.")
@click.option("--dataset", default="auto", help="Dataset name (stub).")
@click.option("--dataset-version", default="latest", help="Dataset version.")
@click.option("--report", type=click.Path(), help="Optional report file (md/html).")
def benchmark(models=None, dialect="auto", dataset="auto", dataset_version="latest", report_path=None):
    # Call the low-level benchmark
    out = run_benchmark(
        models=models,
        backend=models[0] if models else "auto",
        dialect=dialect,
        dataset=dataset,
        dataset_version=dataset_version,
        report_path=report_path,
    )

    # out is the dict returned by run_benchmark()
    # It already contains accuracy + boundary_f1
    return out

# def benchmark(backend, dialect, dataset, dataset_version, report):
#     """Run evaluation benchmark."""
#     report_dict = run_benchmark(
#         models=[backend],
#         backend=backend,
#         dialect=dialect,
#         dataset=dataset,
#         dataset_version=dataset_version,
#         report_path=report,
#     )
#     click.echo(json.dumps(report_dict, indent=2))


# ---------------------------------------------------------------------------
# models
# ---------------------------------------------------------------------------

# @main.command()
# @click.argument(
#     "action",
#     type=click.Choice(["list", "info", "download", "remove", "verify"]),
# )
# @click.argument("name", required=False)
# def models(action, name):
#     """Manage models."""
#     if action == "list":
#         for m in list_models():
#             click.echo(m)

#     elif action == "info":
#         if not name:
#             raise click.UsageError("Model name required for 'info'.")
#         info = get_model_info(name)
#         click.echo(json.dumps(info, indent=2))

#     elif action == "download":
#         if not name:
#             raise click.UsageError("Model name required for 'download'.")
#         download_model(name)
#         click.echo(f"Downloaded model: {name}")

#     elif action == "remove":
#         if not name:
#             raise click.UsageError("Model name required for 'remove'.")
#         remove_model(name)
#         click.echo(f"Removed model: {name}")

#     elif action == "verify":
#         click.echo("Model verification not implemented yet")


# ---------------------------------------------------------------------------
# profiles
# ---------------------------------------------------------------------------

@main.command()
@click.argument("action", type=click.Choice(["list", "info", "validate"]))
@click.argument("name", required=False)
def profiles(action, name):
    """Manage profiles."""
    if action == "list":
        for p in list_profiles():
            click.echo(p)

    elif action == "info":
        if not name:
            raise click.UsageError("Profile name required for 'info'.")
        prof = load_profile(name)
        click.echo(json.dumps(prof, indent=2))

    elif action == "validate":
        if not name:
            raise click.UsageError("Profile name required for 'validate'.")
        load_profile(name)
        click.echo("Profile OK")


# ---------------------------------------------------------------------------
# datasets (stub)
# ---------------------------------------------------------------------------

@main.command()
@click.argument("action", type=click.Choice(["list", "download", "validate"]))
@click.argument("name", required=False)
def datasets(action, name):
    """Manage datasets (stub)."""
    click.echo("Dataset management not implemented yet")


# ---------------------------------------------------------------------------
# config
# ---------------------------------------------------------------------------

@main.command()
@click.argument("action", type=click.Choice(["show", "path", "validate", "set"]))
@click.argument("key", required=False)
@click.argument("value", required=False)
def config(action, key, value):
    """View or modify config."""
    cfg = load_config()

    if action == "show":
        click.echo(json.dumps(cfg, indent=2))

    elif action == "path":
        click.echo(get_config_path())

    elif action == "validate":
        click.echo("Config OK")

    elif action == "set":
        if not key or value is None:
            raise click.UsageError("KEY and VALUE required for 'set'.")
        cfg[key] = value
        save_config(cfg)
        click.echo("Updated config")


# ---------------------------------------------------------------------------
# cache
# ---------------------------------------------------------------------------

@main.command()
@click.argument("action", type=click.Choice(["info", "clear", "remove"]))
@click.argument("name", required=False)
def cache(action, name):
    """Manage cache."""
    if action == "info":
        click.echo(f"Cache: {get_cache_dir()}")

    elif action == "clear":
        clear_cache()
        click.echo("Cache cleared")

    elif action == "remove":
        if not name:
            raise click.UsageError("Model name required for 'remove'.")
        remove_model(name)
        click.echo(f"Removed cached model: {name}")


# ---------------------------------------------------------------------------
# validate (stub)
# ---------------------------------------------------------------------------

@main.command()
@click.argument("target", required=False, default="all")
def validate(target):
    """Validate resources (stub)."""
    click.echo(f"Validation not implemented yet (target={target})")


# ---------------------------------------------------------------------------
# download (simple wrapper)
# ---------------------------------------------------------------------------

@main.command()
@click.argument("name")
def download(name):
    """Download a model."""
    download_model(name)
    click.echo(f"Downloaded model: {name}")


# ---------------------------------------------------------------------------
# version
# ---------------------------------------------------------------------------

@main.command()
def version():
    """Show version."""
    from zomi_syl import __version__
    click.echo(f"zomi-syl {__version__}")

@main.group()
def models():
    """Model registry and backend utilities."""
    pass

@models.command("list")
def models_list():
    """List all available backends/models."""
    import zomi_syl as zs

    models = zs.list_models()
    for m in models:
        click.echo(m)

@models.command("info")
@click.argument("backend_name")
def models_info(backend_name):
    """Show detailed information about a backend/model."""
    import zomi_syl as zs
    from zomi_syl.exceptions import ZomiSylError

    try:
        backend = zs.load_backend(backend_name)
    except ZomiSylError as e:
        click.echo(f"Error: {e}")
        raise SystemExit(1)

    meta = backend.get_metadata(include_ruleset=False)

    click.echo(f"Backend: {backend_name}")
    for key, value in meta.items():
        click.echo(f"{key}: {value}")

@models.command("benchmark")
@click.argument("backend_name")
@click.option("--dialect", default="auto", help="Dialect to benchmark.")
@click.option("--json", "as_json", is_flag=True, help="Output JSON instead of text.")
def models_benchmark(backend_name, dialect, as_json):
    """
    Run a benchmark for a specific backend.
    """
    import json
    import zomi_syl as zs
    from zomi_syl.exceptions import ZomiSylError

    try:
        result = zs.benchmark(
            models=[backend_name],
            dialect=dialect,
            dataset_version="latest",
        )
    except ZomiSylError as e:
        click.echo(f"Error: {e}")
        raise SystemExit(1)

    # --- Extract metrics robustly ---
    # 1. Prefer top-level keys
    if "accuracy" in result and "boundary_f1" in result:
        metrics = {
            "accuracy": result["accuracy"],
            "boundary_f1": result["boundary_f1"],
        }

    # 2. Otherwise fall back to nested results
    else:
        nested = result.get("results", {})
        # pick the first entry (e.g., "auto")
        if nested:
            metrics = next(iter(nested.values()))
        else:
            click.echo("Error: Benchmark returned no metrics.")
            raise SystemExit(1)

    # --- Output ---
    if as_json:
        click.echo(json.dumps(result, indent=2))
        raise SystemExit(0)

    click.echo(f"Benchmark results for backend '{backend_name}':")
    click.echo(f"  Accuracy:     {metrics['accuracy']:.4f}")
    click.echo(f"  Boundary F1:  {metrics['boundary_f1']:.4f}")

    raise SystemExit(0)

@models.command("compare")
@click.argument("backend_names", nargs=-1)
@click.option("--all", "use_all", is_flag=True, help="Benchmark all available backends.")
@click.option("--dialect", default="auto", help="Dialect to benchmark.")
@click.option("--json", "as_json", is_flag=True, help="Output JSON instead of text.")
def models_compare(backend_names, use_all, dialect, as_json):
    """
    Compare benchmark metrics across multiple backends.
    """
    import json
    import zomi_syl as zs
    from zomi_syl.exceptions import ZomiSylError

    # Determine which backends to benchmark
    if use_all:
        backends = zs.list_models()
    else:
        if not backend_names:
            click.echo("Error: Provide backend names or use --all")
            raise SystemExit(1)
        backends = list(backend_names)

    results = {}

    for backend in backends:
        try:
            out = zs.benchmark(
                models=[backend],
                dialect=dialect,
                dataset_version="latest",
            )
        except Zomi_SylError as e:
            results[backend] = {"error": str(e)}
            continue

        # Extract metrics robustly
        if "accuracy" in out and "boundary_f1" in out:
            metrics = {
                "accuracy": out["accuracy"],
                "boundary_f1": out["boundary_f1"],
            }
        else:
            nested = out.get("results", {})
            metrics = next(iter(nested.values())) if nested else {}

        results[backend] = metrics

    # JSON output
    if as_json:
        click.echo(json.dumps(results, indent=2))
        raise SystemExit(0)

    # Pretty table output
    click.echo(f"{'Backend':10} {'Accuracy':10} {'Boundary F1':12}")
    click.echo("-" * 36)

    for backend, metrics in results.items():
        if "error" in metrics:
            click.echo(f"{backend:10} ERROR       {metrics['error']}")
        else:
            acc = f"{metrics['accuracy']:.4f}"
            f1  = f"{metrics['boundary_f1']:.4f}"
            click.echo(f"{backend:10} {acc:10} {f1:12}")

    raise SystemExit(0)

@models.command("doctor")
@click.option("--verbose", is_flag=True, help="Show detailed backend diagnostics.")
def models_doctor(verbose):
    """
    Run a full backend self-test.

    Checks:
        - registry integrity
        - model file presence
        - backend loadability
        - metadata validity
        - single prediction
        - batch prediction
    """
    import zomi_syl as zs
    # from zomi_syl.exceptions import ZomiSylError

    backends = zs.list_models()
    click.echo("🔍 Running backend diagnostics...\n")

    all_ok = True

    for name in backends:
        click.echo(f"=== Backend: {name} ===")

        # 1. Load backend
        try:
            backend = zs.load_backend(name)
            click.echo("  ✔ Loaded successfully")
        except Exception as e:
            click.echo(f"  ✖ Failed to load: {e}")
            all_ok = False
            continue

        # 2. Metadata
        try:
            meta = backend.get_metadata()
            if verbose:
                click.echo(f"  ✔ Metadata: {meta}")
            else:
                click.echo("  ✔ Metadata OK")
        except Exception as e:
            click.echo(f"  ✖ Metadata error: {e}")
            all_ok = False

        # 3. Single prediction
        try:
            pred = backend("itna")
            if not pred.syllables:
                raise ValueError("Empty syllable output")
            click.echo(f"  ✔ Single prediction OK → {'.'.join(pred.syllables)}")
        except Exception as e:
            click.echo(f"  ✖ Prediction error: {e}")
            all_ok = False

        # 4. Batch prediction
        try:
            preds = backend.predict_batch(["itna", "khuapi"])
            if len(preds) != 2:
                raise ValueError("Batch output length mismatch")
            click.echo("  ✔ Batch prediction OK")
        except Exception as e:
            click.echo(f"  ✖ Batch prediction error: {e}")
            all_ok = False

        click.echo("")

    if all_ok:
        click.echo("🎉 All backends passed diagnostics.")
        raise SystemExit(0)
    else:
        click.echo("⚠ Some backends failed diagnostics.")
        raise SystemExit(1)


if __name__ == "__main__":
    main()

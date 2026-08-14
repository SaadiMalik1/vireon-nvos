"""VIREON CLI commands — human-first interface.

vireon validate <dataset> --pipeline <name> --mode <quick|standard|research>
vireon inspect <dataset>
vireon reproduce <paper>
"""
import sys
import os
import click


@click.group()
def cli():
    """VIREON — Scientific validation for neurotechnology."""
    pass


@cli.command()
@click.argument("dataset_name")
@click.option("--pipeline", default="logvar_lda", help="Pipeline name")
@click.option("--subject", type=int, default=None, help="Subject ID (None = all)")
@click.option("--mode", type=click.Choice(["quick", "standard", "research"]), default="standard")
@click.option("--output", default=None, help="Output directory for evidence bundle")
@click.option("--scorecard/--no-scorecard", default=False, help="Include scorecard")
def validate(dataset_name, pipeline, subject, mode, output, scorecard):
    """Validate a BCI pipeline on a MOABB dataset."""
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", ".."))
    from vireon_moabb.spec import quick_spec, standard_spec, research_spec
    from vireon_moabb import MoabbExecutor, ValidationLayer, EvidenceAssembler, Reporter

    click.echo(f"Validating {pipeline} on {dataset_name} (mode={mode})...")

    if mode == "quick":
        spec = quick_spec(dataset=dataset_name, subject=subject or 1, pipeline_name=pipeline)
    elif mode == "standard":
        spec = standard_spec(dataset=dataset_name, subject=subject, pipeline_name=pipeline)
    else:
        spec = research_spec(dataset=dataset_name, subject=subject, pipeline_name=pipeline)

    executor = MoabbExecutor(seed=42)
    trace = executor.run(spec)
    click.echo(f"  ✓ Executed {len(trace.fold_results)} folds, accuracy: {trace.mean_accuracy:.4f}")

    validator = ValidationLayer()
    validation = validator.validate(trace, spec)

    assembler = EvidenceAssembler()
    bundle = assembler.assemble(spec.model_dump(), trace, validation)
    click.echo(f"  ✓ Evidence hash: {bundle.evidence_hash[:32]}...")

    reporter = Reporter()
    if scorecard:
        report = reporter.generate_full_report(trace, validation, bundle)
    else:
        report = reporter.generate_raw_evidence_report(trace, validation, bundle)

    if output:
        os.makedirs(output, exist_ok=True)
        report_path = os.path.join(output, f"evidence_report_{bundle.bundle_id}.txt")
        bundle_path = os.path.join(output, f"evidence_bundle_{bundle.bundle_id}.json")
        with open(report_path, "w") as f:
            f.write(report)
        bundle.save(bundle_path)
        click.echo(f"\nReport: {report_path}")
        click.echo(f"Bundle: {bundle_path}")

    click.echo()
    click.echo(report)


@cli.command()
@click.argument("dataset_name")
@click.option("--subject", type=int, default=None)
def inspect(dataset_name, subject):
    """Inspect a MOABB dataset."""
    if dataset_name == "list":
        try:
            import moabb.datasets as mds
            click.echo("Available MOABB datasets:")
            for name in sorted(dir(mds)):
                obj = getattr(mds, name)
                if name[0].isupper() and hasattr(obj, 'subject_list'):
                    click.echo(f"  {name}")
        except ImportError:
            click.echo("MOABB not installed. Run: pip install moabb")
        return

    click.echo(f"\nInspecting: {dataset_name}")
    click.echo("─" * 50)
    try:
        import importlib
        mod = importlib.import_module("moabb.datasets")
        cls = getattr(mod, dataset_name)
        ds = cls()
        click.echo(f"Dataset:         {dataset_name}")
        click.echo(f"Subjects:        {ds.subject_list}")
        click.echo(f"N subjects:      {len(ds.subject_list)}")
    except Exception as e:
        click.echo(f"Error: {e}")
    click.echo()
    click.echo("Run:")
    click.echo(f"  vireon validate {dataset_name} --pipeline logvar_lda --mode standard")


@cli.command()
@click.argument("paper")
@click.option("--mode", type=click.Choice(["quick", "standard", "research"]), default="standard")
def reproduce(paper, mode):
    """Reproduce a literature result."""
    click.echo(f"Reproducing: {paper} (mode={mode})")
    click.echo("  (Literature reproduction via MOABB integration — coming soon)")


if __name__ == "__main__":
    cli()

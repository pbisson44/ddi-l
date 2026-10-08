# Fragment Reuse Lab

This lab expands on the fragment rebuild script in ``examples`` to teach how to
package reusable fragments, distribute them to other teams, and reuse them in
new DDI instances.

!!! note
    Install the project in editable mode (``pip install -e .``) so the
    examples can locate ``ddi_l`` modules.

!!! warning "Locate packaged examples"
    The fragment scripts load XML assets bundled in the wheel under
    ``ddi_l.examples`` instead of reading from a cloned repository. Resolve
    the packaged files with ``importlib.resources`` and pass the resolved path
    into your loaders (for example ``DDIDocument.from_xml``):

    ```python
    from importlib import resources
    from ddi_l import examples

    with resources.as_file(
        resources.files(examples) / "example_fragment.xml"
    ) as fragment_path:
        print(fragment_path)
    ```

## 1. Rebuild the example fragment bundle

1. Execute ``python -m ddi_l.examples.build_and_validate --refresh --refresh-fragment``
   to regenerate the sample bundle.  The script rewrites
   ``examples/example_instance.xml`` and the default fragment at
   ``examples/example_fragment.xml`` while printing confirmation that both
   payloads validate successfully.
2. Inspect the refreshed instance and fragment XML outputs to see how the
   maintainables are packaged and how the validation messages describe the
   rebuild.
3. Re-run the command with ``--fragment-output`` if you want the fragment to be
   written to another location (for example
   ``--fragment-output fragments/catalog/example_fragment.xml``) so teams know
   where to pick up the reusable artefact.

## 2. Publish fragments for team consumption

!!! caution "Compliance review before distribution"
    De-identify fragment payloads, strip production URNs, and align with your
    organisation's data-handling rules before sharing archives with other
    teams. Follow the [redaction guidance in the CLI automation
    playbook](automation-playbook.en.md#5-surface-findings-in-ci-dashboards) to
    keep tutorials consistent.

1. Copy the generated fragments into a shared location (for example
   ``fragments/catalog``).
2. Create a README that documents the fragment purpose, maintainable identifiers,
   and versioning scheme.
3. Optionally zip the fragments and validation report together so downstream
   consumers have a single artefact to download.

## 3. Consume fragments in a new project

1. Start a new Python script and load both the target document and fragment:

    ```python
    from ddi_l import MaintainableBase
    from ddi_l.document import DDIDocument, DDIFragment

    document = DDIDocument.from_xml("instances/source.ddi.xml")
    fragment = DDIFragment.from_xml("fragments/catalog/study-fragment.xml")
    ```

2. Iterate over :meth:`ddi_l.document.DDIFragment.iter_fragment_payloads` and
   attach each maintainable to the document explicitly:

    ```python
    for payload in fragment.iter_fragment_payloads():
        maintainable_cls = MaintainableBase.for_tag(payload.tag)
        if maintainable_cls is None:
            raise ValueError(f"Unsupported payload: {payload.tag}")
        document.add_maintainable(maintainable_cls.from_xml(payload))
    ```

3. Serialise the enriched instance and run ``ddi validate`` to confirm the
   fragments integrate cleanly.

## 4. Maintain fragment provenance

- Track fragment versions in your source control system and tag releases so
  consuming teams can pin to specific builds.
- Include a changelog with each fragment release that notes schema versions and
  lint expectations.
- Automate fragment rebuilds in CI to ensure new changes remain compatible with
  the canonical instance.

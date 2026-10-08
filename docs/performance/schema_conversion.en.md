# Schema conversion benchmark

This page outlines a baseline benchmark for converting schema definitions into ddi-l objects. Use it to validate performance changes and to keep regression testing repeatable.

## Benchmark objective

- Measure the time and memory required to parse, validate, and convert schema sources.
- Capture the impact of caching, streaming, and batching options.

## Dataset

- Include a representative DDI schema bundle and a large sample XML instance.
- Note the file sizes and any simplifications used for the benchmark run.

## Procedure

1. Warm up the environment by running a no-op command to load dependencies.
2. Execute the conversion command against the benchmark dataset.
3. Repeat runs at least three times and record the median.
4. Compare results when toggling key options (e.g., caching, parallelism, schema reuse).

## Metrics to collect

- Wall-clock duration for the full conversion pipeline.
- Peak memory usage and steady-state footprint.
- Number of warnings or validation errors encountered.

## Reporting template

Use the following skeleton to log results:

```markdown
### Environment
- Hardware:
- Python:
- Dependencies:

### Dataset
- Schema bundle:
- Instance file:

### Results
- Median runtime:
- Peak memory:
- Notes:
```

## Next steps

- Share findings in the performance playbook and update recommendations.
- Extend the benchmark to cover new schema features as they are added.

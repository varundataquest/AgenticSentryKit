# Examples

The `examples/` directory contains runnable walkthroughs for each adapter. All demos rely on HTML fixtures under `examples/common/sample_html`, which means you can test the guard engine without live network access or API keys.

Start with `make demo` to exercise the shared offline scenario. It generates a timestamped directory under `runs/` that stores the JSON verdict and HTML report so you can inspect the findings in a browser.

To explore a framework-specific integration, install the matching extra and run the associated script. Each demo loads the common goal definition, runs a guarded interaction, and prints the verdict before saving a report.

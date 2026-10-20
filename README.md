# 🛠️ Pipeline Development Tools (Dev_tools)

A collection of lightweight, standalone utility scripts designed to help develop, debug, and validate bioinformatic pipelines without running heavy executions.

> 💡 **Flexibility:** All tools use command-line arguments (`argparse`), allowing you to run them directly from this folder against any target project directory without moving files around.

---

## 📁 Available Tools

### 1. `snakemake_tree_inspector.py`
A dynamic visualization tool for Snakemake pipelines. It parses your configuration and helper functions to generate a clean, expected output directory tree.

* **Why use it?** 
  * Instantly preview your pipeline's final directory structure before running a dry-run or full execution.
  * Catch configuration errors, misplaced output paths, or unresolved wildcards in seconds.
  * 100% cross-platform (Windows / Linux / macOS) and fully dynamic (requires zero manual target maintenance when adding new helper functions).

* **How it works:**
  1. Loads your pipeline parameters from `config/config.yaml`.
  2. Reads and safely extracts pure Python helper code from `workflow/rules/common.smk` (automatically filtering out Snakemake-specific DSL blocks like `rule` or `checkpoint`).
  3. Automatically discovers and executes target-generating functions.
  4. Builds and prints a human-readable text tree of all expected final outputs.

* **Usage:**
  Default usage (run from the target project root):
  ```bash
  python Dev_tools/snakemake_tree_inspector.py
  ```
  Recommended usage:
  ```bash
  Dev_tools/snakemake_tree_inspector.py --config path/to/my_project/config.yaml --rules path/to/my_project/common.smk
  ```
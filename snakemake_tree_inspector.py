import argparse
import json
import os
import re
from os.path import join as pjoin
import yaml
from snakemake.io import expand


class MockWorkflow:

  def __init__(self):
    self.rules = []


def is_likely_filepath(path_str):
  """Universal check to determine if a string looks like a file path."""
  if not isinstance(path_str, str):
    return False
  # Must contain a path separator and at least a dot for an extension or deep structure
  has_separator = "/" in path_str or "\\" in path_str
  # Optional: check if it has a file extension or looks like a target path
  return has_separator


if __name__ == "__main__":

  # 0. Argument parsing
  parser = argparse.ArgumentParser(
      description="Inspect expected Snakemake output tree dynamically."
  )
  parser.add_argument(
      "--config",
      default="config/config.yaml",
      help="Path to the pipeline config file (default: config/config.yaml)",
  )
  parser.add_argument(
      "--rules",
      default="workflow/rules/common.smk",
      help="Path to the common.smk file (default: workflow/rules/common.smk)",
  )
  args = parser.parse_args()

  config_file = args.config
  common_smk_path = args.rules

  # 1. Load configuration
  if os.path.exists(config_file):
    print(f"Loading configuration from {config_file}...")
    with open(config_file, "r") as f:
      config = yaml.safe_load(f)
  else:
    print(f"Error: Config file not found at '{config_file}'.")
    exit(1)

  # 2. Fully dynamic namespace
  common_namespace = globals().copy()
  common_namespace.update({
      "config": config,
      "workflow": MockWorkflow(),
  })

  # 3. Read and execute common.smk (filtering out Snakemake DSL blocks)
  if os.path.exists(common_smk_path):
    print(f"Extracting and executing helpers from {common_smk_path}...\n")
    with open(common_smk_path, "r", encoding="utf-8") as f:
      lines = f.readlines()

    filtered_lines = []
    skip_block = False
    for line in lines:
      stripped = line.strip()
      if stripped.startswith("rule ") or stripped.startswith("checkpoint "):
        skip_block = True
        continue
      if skip_block:
        if line.startswith(" ") or line.startswith("\t") or stripped == "":
          continue
        else:
          skip_block = False
      if stripped.startswith("include:") or stripped.startswith("configfile:") or stripped.startswith("workdir:"):
        continue
      filtered_lines.append(line)

    exec("".join(filtered_lines), common_namespace)
  else:
    print(f"Error: common.smk not found at '{common_smk_path}'.")
    exit(1)

  # 4. Universal target discovery (No hardcoded lists or prefixes needed!)
  all_targets = []

  for name, obj in common_namespace.items():
    # Target only user-defined functions (ignoring built-ins and private variables)
    if callable(obj) and not name.startswith("_"):
      try:
        # Attempt to call the function without arguments
        res = obj()

        # Filter and accumulate results that look like file paths
        if isinstance(res, (list, set, tuple)):
          for item in res:
            if is_likely_filepath(item):
              all_targets.append(str(item))
        elif is_likely_filepath(res):
          all_targets.append(str(res))

      except TypeError:
        # Automatically skips functions requiring mandatory arguments (e.g. wildcards)
        pass
      except Exception:
        # Silently ignores any other execution errors in helper functions
        pass

  # Clean up and deduplicate target paths
  all_targets = sorted(list(set(all_targets)))


  # ==========================================
  # Tree Builder & Printer
  # ==========================================
  def build_tree(file_paths):
    """Convert a flat list of file paths into a nested tree dictionary."""
    tree = {}
    for path in file_paths:
        # Normalize path to match the current OS (converts / to \ on Windows)
        normalized_path = os.path.normpath(path)
        parts = normalized_path.split(os.sep)

        current = tree
        for part in parts:
            if part not in current:
                current[part] = {}
            current = current[part]
    return tree


  def print_tree(tree, prefix=""):
    """Recursively print the tree in a human-readable directory format."""
    pointers = ["├── ", "└── "]
    keys = list(tree.keys())
    for i, key in enumerate(keys):
      connector = pointers[1] if i == len(keys) - 1 else pointers[0]
      print(f"{prefix}{connector}{key}")
      if tree[key]:
        extension = "    " if i == len(keys) - 1 else "│   "
        print_tree(tree[key], prefix + extension)


  print(f"Resolved {len(all_targets)} expected output files.\n")
  print("📁 .")
  file_tree = build_tree(all_targets)
  print_tree(file_tree)
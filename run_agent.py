"""CLI runner for the form-filling agent MVP.

Usage examples:
  python run_agent.py --template templates/example_form.json --prompt "My name is Alice..."
  python run_agent.py --template templates/example_form.json --prompt-file examples/sample_prompt.txt --openai
"""
import argparse
import json
from pathlib import Path
from agent import fill_form


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--template", required=True, help="Path to template JSON")
    p.add_argument("--prompt", help="Prompt text")
    p.add_argument("--prompt-file",
                   help="Path to a file containing the prompt")
    p.add_argument("--openai", action="store_true",
                   help="Use OpenAI if available")
    p.add_argument(
        "--out", help="Output file for filled JSON (default: filled.json)", default="filled.json")
    args = p.parse_args()

    if not args.prompt and not args.prompt_file:
        raise SystemExit("Provide --prompt or --prompt-file")

    prompt_text = args.prompt
    if args.prompt_file:
        prompt_text = Path(args.prompt_file).read_text()

    tpl = json.loads(Path(args.template).read_text())

    filled = fill_form(tpl, prompt_text, use_openai=args.openai)

    out_path = Path(args.out)
    out_path.write_text(json.dumps(filled, indent=2))
    print(f"Wrote filled form to {out_path}")


if __name__ == "__main__":
    main()

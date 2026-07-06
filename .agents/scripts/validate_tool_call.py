import json
import re
import sys


def main():
    try:
        raw_input = sys.stdin.read()
        if not raw_input:
            sys.exit(0)

        command = ""
        # Try parsing stdin as JSON to extract the CommandLine argument
        try:
            data = json.loads(raw_input)
            if isinstance(data, dict):
                tool_input = data.get("tool_input", {})
                if isinstance(tool_input, dict):
                    # In ADK run_command, command line is typically passed as CommandLine
                    command = tool_input.get("CommandLine", "") or tool_input.get(
                        "command", ""
                    )
                elif isinstance(tool_input, str):
                    command = tool_input
            else:
                command = str(data)
        except json.JSONDecodeError:
            # Fallback to inspecting the raw input text if it's not JSON
            command = raw_input

        # Normalize spacing for robust regex matching
        normalized_command = " ".join(command.split()).lower()

        # Define patterns for blocking destructive system commands
        block_patterns = [
            r"\brm\s+-[a-z]*f[a-z]*r[a-z]*\b",  # rm -rf, rm -fr, rm -r -f
            r"\brm\s+-[a-z]*r[a-z]*f[a-z]*\b",
            r"\brm\s+-r\s+-f\b",
            r"\brm\s+-f\s+-r\b",
            r"\bmkfs\b",  # mkfs commands
            r"\bdd\s+if=",  # dd commands rewriting disks
        ]

        for pattern in block_patterns:
            if re.search(pattern, normalized_command):
                sys.stderr.write(
                    f"\n[SECURITY VIOLATION] Destructive command blocked: '{command}' matches pattern '{pattern}'\n"
                )
                sys.exit(2)  # Exit code 2 blocks tool execution

        # Allow execution
        sys.exit(0)

    except Exception as e:
        sys.stderr.write(f"Validation error: {e}\n")
        sys.exit(0)


if __name__ == "__main__":
    main()

# Connecting Claude Desktop to VIREON

## Step 1: Install VIREON

```bash
pip install vireon-mcp
```

## Step 2: Configure Claude Desktop

Add to `~/Library/Application Support/Claude/claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "vireon": {
      "command": "vireon-mcp",
      "args": []
    }
  }
}
```

## Step 3: Restart Claude Desktop

Quit Claude Desktop completely and restart. You should see "vireon" in the tools list.

## Step 4: Try it

Type in Claude:

> "I have an EEG file at /path/to/data.edf. Can you help me validate my classifier?"

Claude will:
1. Call `inspect_dataset` to examine the file
2. Call `plan_experiment` to propose a validation plan
3. Ask you to confirm
4. Call `validate_experiment` with `confirm: true`
5. Call `explain_result` to summarize the findings

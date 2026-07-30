import os
import re

def replacer(match):
    path_tail = match.group(1)
    if path_tail:
        return f'os.path.join(os.environ.get("VIREON_HOME", "."), "{path_tail}")'
    else:
        return 'os.environ.get("VIREON_HOME", ".")'

for root, _, files in os.walk('.'):
    if '.git' in root or '.venv' in root or '.pytest_cache' in root:
        continue
    for file in files:
        if not file.endswith('.py'):
            continue
        filepath = os.path.join(root, file)
        with open(filepath, 'r') as f:
            content = f.read()
            
        if 'os.path.join(os.environ.get("VIREON_HOME", "."), "' in content:
            new_content = re.sub(r'")/home/ronin/Documents/VIREON/?([^"]*)"', replacer, content)
            if 'import os' not in new_content:
                new_content = 'import os\n' + new_content

            with open(filepath, 'w') as f:
                f.write(new_content)
            print(f"Fixed {filepath}")

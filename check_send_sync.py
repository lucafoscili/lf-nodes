import os

count = 0
for root, dirs, files in os.walk('modules/nodes'):
    # Skip hidden directories and __pycache__
    dirs[:] = [d for d in dirs if not d.startswith('.') and d != '__pycache__']
    for file in files:
        if file.endswith('.py'):
            filepath = os.path.join(root, file)
            try:
                with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                    if 'PromptServer.instance.send_sync' in content:
                        print(f'Found in {filepath}')
                        count += 1
            except Exception as e:
                print(f'Error reading {filepath}: {e}')

print(f'Total files with send_sync: {count}')
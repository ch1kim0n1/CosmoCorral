import json

def analyze(x):
    try:
        with open('data.json', 'w', encoding='utf-8') as f:
            json.dump({'value': x}, f, ensure_ascii=False, indent=2)
        print("Saved to data.json:", x)
    except TypeError:
        with open('data.json', 'w', encoding='utf-8') as f:
            json.dump({'value': str(x)}, f, ensure_ascii=False, indent=2)
        print("Saved to data.json (as str):", x)
import json

with open(f'./results/poetry/tangshisanbaishou-word_poem_dict.json', 'r', encoding='utf-8') as f:
    data = json.load(f)
    results = []
    third = {
        'value': 0
    }
    next = {
        'value': 0
    }
    max = {
        'value': 0
    }
    for key, item in data.items():
        temp = {
            'type': key,
            'value': item['count']
        }
        results.append(temp)
        if(max['value'] < item['count']):
             third = next
             next = max
             max = temp
    with open(f'./results/poetry/temp.json', 'w', encoding='utf-8') as file:
            json.dump(results, file, ensure_ascii=False, indent=4)
    print(max, next, third)
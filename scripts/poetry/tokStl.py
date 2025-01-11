# 进行单任务的分词
import json
import uuid
import hanlp
import re

import hanlp.pretrained

hanlp.pretrained.tok.ALL
tok = hanlp.load(hanlp.pretrained.tok.COARSE_ELECTRA_SMALL_ZH)

# 存储分词词典
word_poem_dict = {}
word_translate_dict = {}
word_analysis_dict = {}

def remove_punctuation(words=[]):
    """
    去除标点
    """
    if(len(words) != 0):
        return [word for word in words if not re.match(r'[^\w]', word)]
    return words

def resolving_nagative_expectations_split(words=[]):
    """
    解决分词错误的把 不 单独分出来的问题
    """
    temp = ''
    result = []
    if(len(words) != 0):
        for word in words:
            if(word == '不'):
                temp = word
            else:
                result.append(temp + word)
                temp = ''
    return result

def update_dic(words=[], dic={}, poem_id=None):
    """
    更新词典
    """
    for word in words:
        try:
            word_store = dic[word]
            poem_ids = word_store["poem_ids"]
            if poem_id not in poem_ids:
                poem_ids.append(poem_id)
            word_store['count'] = word_store['count'] + 1
            word_store["poem_ids"] = poem_ids
            dic[word] = word_store
        except:
            word_store = {
                "count": 1,
                "poem_ids": [poem_id]
            }
            dic[word] = word_store

def main():
    poetry_type = 'tangshisanbaishou'
    with open('./data/poetry/tangshisanbaishou-data.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
        results = []
        count = 1
        for poem_item in data:
            poem = poem_item['poem']
            translate = poem_item['translate']
            analysis = poem_item['analysis']

            poem_id = uuid.uuid4().hex
            poem_tok = resolving_nagative_expectations_split(remove_punctuation(tok(poem)))
            translate_tok = resolving_nagative_expectations_split(remove_punctuation(tok(translate)))
            analysis_tok = resolving_nagative_expectations_split(remove_punctuation(tok(analysis)))

            poem_item['poem_id'] = poem_id
            poem_item['poem_tok'] = poem_tok
            poem_item['translate_tok'] = translate_tok
            poem_item['analysis_tok'] = analysis_tok

            results.append(poem_item)

            update_dic(poem_tok, word_poem_dict, poem_id)
            update_dic(translate_tok, word_translate_dict, poem_id)
            update_dic(analysis_tok, word_analysis_dict, poem_id)

            print(f"Finished {count} - {poem_item['title']}")
            count = count + 1
        
        with open(f'./results/poetry/{poetry_type}-data_dict.json', 'w', encoding='utf-8') as file:
            json.dump(results, file, ensure_ascii=False, indent=4)
        with open(f'./results/poetry/{poetry_type}-word_poem_dict.json', 'w', encoding='utf-8') as file:
            json.dump(word_poem_dict, file, ensure_ascii=False, indent=4)
        with open(f'./results/poetry/{poetry_type}-word_translate_dict.json', 'w', encoding='utf-8') as file:
            json.dump(word_translate_dict, file, ensure_ascii=False, indent=4)
        with open(f'./results/poetry/{poetry_type}-word_analysis_dict.json', 'w', encoding='utf-8') as file:
            json.dump(word_analysis_dict, file, ensure_ascii=False, indent=4)


if __name__ == '__main__':
    main()
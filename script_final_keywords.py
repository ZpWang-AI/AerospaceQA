from data_manager import DataManager


def main_final_keywords():
    save_file = './dataspace/final_keywords.txt'

    final_keywords = DataManager.keyword_final(return_set=False)
    
    with open(save_file, 'w', encoding='utf8')as f:
        for k in final_keywords:
            f.write(f'{k}\n')


if __name__ == '__main__':
    main_final_keywords()
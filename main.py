from baike_spider import main_baike
from zhidao_spider import main_zhidao

from keyword_extraction import (main_query_new_keywords, 
                                main_filter_new_keywords,
                                main_excel2txt_manual_todo,
                                )


if __name__ == '__main__':

    main_baike()
    main_zhidao()
    
    main_query_new_keywords()
    main_filter_new_keywords()

    main_excel2txt_manual_todo([2000]*3)
    
    pass

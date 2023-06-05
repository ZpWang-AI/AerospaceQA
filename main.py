from baike_spider import main_baike
from zhidao_spider import main_zhidao

from keyword_extraction import (main_query_new_keywords, 
                                main_filter_new_keywords,
                                KeywordManager,
                                )


if __name__ == '__main__':

    main_baike()
    main_zhidao()
    
    main_query_new_keywords()
    main_filter_new_keywords()

    KeywordManager.keyword_excel2txt()
    KeywordManager.get_new_filter_keywords()
    
    pass

USER_AGENTS = [
        "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/22.0.1207.1 Safari/537.1",
        "Mozilla/5.0 (X11; CrOS i686 2268.111.0) AppleWebKit/536.11 (KHTML, like Gecko) Chrome/20.0.1132.57 Safari/536.11",
        "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.6 (KHTML, like Gecko) Chrome/20.0.1092.0 Safari/536.6",
        "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.6 (KHTML, like Gecko) Chrome/20.0.1090.0 Safari/536.6",
        "Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/19.77.34.5 Safari/537.1",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/536.5 (KHTML, like Gecko) Chrome/19.0.1084.9 Safari/536.5",
        "Mozilla/5.0 (Windows NT 6.0) AppleWebKit/536.5 (KHTML, like Gecko) Chrome/19.0.1084.36 Safari/536.5",
        "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1063.0 Safari/536.3",
        "Mozilla/5.0 (Windows NT 5.1) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1063.0 Safari/536.3",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_8_0) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1063.0 Safari/536.3",
        "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1062.0 Safari/536.3",
        "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1062.0 Safari/536.3",
        "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1061.1 Safari/536.3",
        "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1061.1 Safari/536.3",
        "Mozilla/5.0 (Windows NT 6.1) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1061.1 Safari/536.3",
        "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1061.0 Safari/536.3",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/535.24 (KHTML, like Gecko) Chrome/19.0.1055.1 Safari/535.24",
        "Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/535.24 (KHTML, like Gecko) Chrome/19.0.1055.1 Safari/535.24",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.186 Safari/537.36",
        "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/49.0.2623.221 Safari/537.36 SE 2.X MetaSr 1.0",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36",
        ]
IQIYIUrls = [
    "https://pcw-api.iqiyi.com/search/recommend/list?channel_id=2&data_type=1&mode={mode}&page_id={lPage}&ret_num=48&session=ca05f72f509d4e276146faa28bf2d8d6&three_category_id={iarea}", ##电视剧
    "https://pcw-api.iqiyi.com/search/recommend/list?channel_id=1&data_type=1&mode={mode}&page_id={lPage}&ret_num=48&session=a105f758273445da58870f216c587d2d&three_category_id={iarea}" #电影
    "https://pcw-api.iqiyi.com/search/recommend/list?channel_id=6&data_type=1&mode={mode}&page_id={lPage}&ret_num=48&session=f925f77fd151b32777af7744a0c10446&three_category_id={iarea}" #综艺
    "https://pcw-api.iqiyi.com/search/recommend/list?channel_id=4&data_type=1&mode={mode}&page_id={lPage}&ret_num=48&session=f3d5f7c5ae71ce1ee3d998c698653137&three_category_id={iarea}" #动漫
    "https://pcw-api.iqiyi.com/search/recommend/list?channel_id=3&data_type=1&mode={mode}&page_id={lPage}&ret_num=48&session=1a15f7b5be34ce712fa319a7e1be29d9&three_category_id={iarea}" #纪录片
    ]
IQIYIModes = [
    # 综合排序，热播榜，好评榜，新上线
    "24","11","8","4"
]

TVAreas = [
    # 全部地区，内地，香港地区，韩国，美剧，日本，泰国，台湾地区，英国，其他
    "","15","16","17","18","309","1114","1117","28916","19"
]

MovieAreas = [
    # 全部地区，华语，香港地区，美国，欧洲，韩国，日本，泰国，印度，其他
    "","1","28997","2","3","4","308","1115","28999","5"
]
ShowAreas = [
    #全部地区，内地，港台，韩国，欧美，其它
    "","151","152","33306","154","1113"
]
AnimalAreas = [
    #全部地区，中国大陆，日本，韩国，欧美，其它
    "","37","38","1106","30218","40"
]
VlogAreas = [
    #全部出品方，BBC，美国历史频道，探索频道，央视记录，北京纪实频道，上海纪实频道，朗思文化
    "","28468","28470","28471","28472","28473","28474","28476"
]

TX_TVAreas = [
    ##全部，内地，美国，英国，韩国，泰国，日本，中国香港，中国台湾，其他
    "-1", "814", "815", "816", "818", "9", "10", "14", "817", "819"
    ]
TX_MovieAreas = [
    ##全部，内地，中国香港，美国，欧洲，中国台湾，日本，韩国，其他
    "-1", "100024", "100025", "100029", "100032", "100026", "100027", "100028", "100033"
    ]
TX_VarietyAreas = [
    ##全部 ， 国内， 海外
    "-1", "1", "2"
    ]
TX_CartoonAreas = [
    ##全部，内地，日本， 欧美，其他
    "-1", "1", "2", "3", "4"
    ]
TX_ChildAreas = [
    ##全部，欧美，日韩，国内
    "-1", "1","2","3"
]
## {ofset} 设置为 30 的倍数
TX_Urls = [
    "https://v.qq.com/x/bu/pagesheet/list?_all=1&append=1&channel=tv&iarea={iarea}&listpage=1&offset={ofset}&pagesize=30&sort=19",      ##剧集某地区最新
    "https://v.qq.com/x/bu/pagesheet/list?_all=1&append=1&channel=tv&iarea={iarea}&listpage=1&offset={ofset}&pagesize=30&sort=18",      ##剧集某地区最热
    "https://v.qq.com/x/bu/pagesheet/list?_all=1&append=1&channel=tv&iarea={iarea}&listpage=1&offset={ofset}&pagesize=30&sort=16",      ##剧集某地区好评
    "https://v.qq.com/x/bu/pagesheet/list?_all=1&append=1&channel=tv&iarea={iarea}&listpage=1&offset={ofset}&pagesize=30&sort=21",      ##剧集某地区口碑好剧
    "https://v.qq.com/x/bu/pagesheet/list?_all=1&append=1&channel=tv&iarea={iarea}&listpage=1&offset={ofset}&pagesize=30&sort=54",      ##剧集某地区高分好评
    "https://v.qq.com/x/bu/pagesheet/list?_all=1&append=1&channel=tv&iarea={iarea}&listpage=1&offset={ofset}&pagesize=30&sort=22",      ##剧集某地区知乎高分
    "https://v.qq.com/x/bu/pagesheet/list?_all=1&append=0&channel=movie&iarea={iarea}&listpage=1&offset={ofset}&pagesize=30&sort=18",   ##电影某地区最近热播
    "https://v.qq.com/x/bu/pagesheet/list?_all=1&append=0&channel=movie&iarea={iarea}&listpage=1&offset={ofset}&pagesize=30&sort=19",   #电影某地区最新上架
    "https://v.qq.com/x/bu/pagesheet/list?_all=1&append=0&channel=movie&iarea={iarea}&listpage=1&offset={ofset}&pagesize=30&sort=21",   #电影某地区高分好评
    "https://v.qq.com/x/bu/pagesheet/list?_all=1&append=0&channel=movie&iarea={iarea}&listpage=1&offset={ofset}&pagesize=30&sort=22",   #电影某地区知乎高分
    "https://v.qq.com/x/bu/pagesheet/list?_all=1&append=0&channel=variety&iarea={iarea}&listpage=1&offset={ofset}&pagesize=30&sort=5",  ##综艺某地区最新上架
    "https://v.qq.com/x/bu/pagesheet/list?_all=1&append=0&channel=variety&iarea={iarea}&listpage=1&offset={ofset}&pagesize=30&sort=4",  ##综艺某地区最近热播
    "https://v.qq.com/x/bu/pagesheet/list?_all=1&append=0&channel=cartoon&iarea={iarea}&listpage=1&offset={ofset}&pagesize=30&sort=19", ##动漫某地区最新
    "https://v.qq.com/x/bu/pagesheet/list?_all=1&append=0&channel=cartoon&iarea={iarea}&listpage=1&offset={ofset}&pagesize=30&sort=18", ##动漫某地区最热
    "https://v.qq.com/x/bu/pagesheet/list?_all=1&append=0&channel=cartoon&iarea={iarea}&listpage=1&offset={ofset}&pagesize=30&sort=20",  ##动漫某地区好评
    "https://v.qq.com/x/bu/pagesheet/list?_all=1&append=0&channel=child&iarea={iarea}&listpage=1&offset={ofset}&pagesize=30&sort=19",    ##少儿某地区最新
    "https://v.qq.com/x/bu/pagesheet/list?_all=1&append=0&channel=child&iarea={iarea}&listpage=1&offset={ofset}&pagesize=30&sort=18",    ##少儿某地区最热
    "https://v.qq.com/x/bu/pagesheet/list?_all=1&append=0&channel=child&iarea={iarea}&listpage=1&offset={ofset}&pagesize=30&sort=20",    ##少儿某地区好评
    ]

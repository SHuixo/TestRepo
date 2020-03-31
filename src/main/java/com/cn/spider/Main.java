package com.cn.spider;

import com.alibaba.fastjson.JSON;
import com.alibaba.fastjson.JSONArray;
import com.alibaba.fastjson.JSONObject;
import com.cn.spider.mapper.MovieMapper;
import com.cn.spider.model.Movie;
import com.cn.spider.util.GetJson;
import org.apache.ibatis.io.Resources;
import org.apache.ibatis.session.SqlSession;
import org.apache.ibatis.session.SqlSessionFactory;
import org.apache.ibatis.session.SqlSessionFactoryBuilder;

import java.io.IOException;
import java.io.InputStream;
import java.util.List;

public class Main {
    public static void main(String[] args) {
        //配置文件路径
        String resource = "mybatis-config.xml";
        InputStream inputStream = null;
        try {
            inputStream = Resources.getResourceAsStream(resource);
        } catch (IOException e) {
            e.printStackTrace();
        }
        //从mybatis中得到dao对象
        SqlSessionFactory sqlSessionFactory = new SqlSessionFactoryBuilder().build(inputStream);
        SqlSession sqlSession = sqlSessionFactory.openSession();//得到连接对象
        MovieMapper movieMapper = sqlSession.getMapper(MovieMapper.class);

        int start;//每页多少条
        int total = 0; //记录数
        int end = 9979; //总共的记录数
        for (start = 0; start <=end ; start+=20) {
            String address = "https://Movie.douban.com/j/new_search_subjects?sort=U&range=0,10&tags=&start=" + start;
            try {
                JSONObject dayLine = new GetJson().getHttpJson(address, 1);
                System.out.println("start:"+ start);
                JSONArray json = dayLine.getJSONArray("data");
                List<Movie> lists = JSON.parseArray(json.toString(), Movie.class);

                if (start >= end){
                    System.out.println("已经爬取到底了");
                    sqlSession.close();
                }
                for (Movie movie : lists){
                    movieMapper.insert(movie);
                    sqlSession.commit();
                }
                total += lists.size();
                System.out.println("正在爬取中--共抓取："+total+"条数据");
            } catch (Exception e) {
                e.printStackTrace();
            }
        }

    }
}

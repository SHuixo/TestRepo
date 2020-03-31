package com.cn.spider.mapper;

import com.cn.spider.model.Movie;
import java.util.List;

public interface MovieMapper {

    void insert(Movie movie);
    List<Movie> findAll();
}

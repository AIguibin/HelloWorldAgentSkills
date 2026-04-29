package com.aiguibin.platform.modules.dbcompare.model.dto;

import lombok.Data;

import java.util.List;
import java.util.Map;

/**
 * 设计文档数据
 *
 * @author aiguibin
 * @date 2025-01-15
 */
@Data
public class DocData {

    /**
     * 文件名
     */
    private String fileName;

    /**
     * 文件路径
     */
    private String filePath;

    /**
     * 目录数据
     */
    private List<MenuItem> menuList;

    /**
     * 表字段数据 Map<表名, 字段列表>
     */
    private Map<String, List<ColumnItem>> columnMap;

    /**
     * 索引数据 Map<表名, 索引列表>
     */
    private Map<String, List<IndexItem>> indexMap;
}

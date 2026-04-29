package com.aiguibin.platform.modules.dbcompare.model.dto;

import lombok.Data;

/**
 * 索引信息
 *
 * @author aiguibin
 * @date 2025-01-15
 */
@Data
public class IndexInfo {

    private String indexName;
    private String indexType;
    private Integer nonUnique;
    private String indexColumn;
}

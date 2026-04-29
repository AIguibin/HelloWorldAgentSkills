package com.aiguibin.platform.modules.dbcompare.model.dto;

import lombok.Data;

/**
 * 索引项
 *
 * @author aiguibin
 * @date 2025-01-15
 */
@Data
public class IndexItem {

    private String tableName;
    private String tableComment;
    private String indexName;
    private String indexType;
    private String indexColumn;
    private String remark;
}

package com.aiguibin.platform.modules.dbcompare.model.dto;

import lombok.Data;

/**
 * 索引差异
 *
 * @author aiguibin
 * @date 2025-01-15
 */
@Data
public class IndexDiff {

    private String seq;
    private String fileName;
    private String checkDate;
    private String dbName;
    private String tableName;
    private String indexName;
    private String indexType;
    private String docIndexColumn;
    private String dbIndexColumn;
    private String diffType;
    private String diffNote;
    private String processScript;
    private String remark;
}

package com.aiguibin.platform.modules.dbcompare.model.dto;

import lombok.Data;

/**
 * 字段差异
 *
 * @author aiguibin
 * @date 2025-01-15
 */
@Data
public class ColumnDiff {

    private String seq;
    private String fileName;
    private String checkDate;
    private String dbName;
    private String tableName;
    private String tableComment;
    private String docColumnName;
    private String dbColumnName;
    private String standardColumnName;
    private String docColumnComment;
    private String dbColumnComment;
    private String standardColumnComment;
    private String docColumnType;
    private String dbColumnType;
    private String standardColumnType;
    private String diffType;
    private String diffNote;
    private String processScript;
    private String remark;
}

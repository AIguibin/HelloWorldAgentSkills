package com.aiguibin.platform.modules.dbcompare.model.dto;

import lombok.Data;

/**
 * 字段项
 *
 * @author aiguibin
 * @date 2025-01-15
 */
@Data
public class ColumnItem {

    private String seq;
    private String tableName;
    private String tableComment;
    private String columnName;
    private String columnType;
    private String columnComment;
    private String isNullable;
    private String isPk;
    private String dictCode;
    private String isBusPk;
    private String isBusRequired;
    private String changeDate;
    private String remark;
}

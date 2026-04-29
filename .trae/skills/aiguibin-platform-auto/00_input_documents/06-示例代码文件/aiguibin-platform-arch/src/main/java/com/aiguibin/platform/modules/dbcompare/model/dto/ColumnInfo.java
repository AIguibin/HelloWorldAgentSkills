package com.aiguibin.platform.modules.dbcompare.model.dto;

import lombok.Data;

/**
 * 字段信息
 *
 * @author aiguibin
 * @date 2025-01-15
 */
@Data
public class ColumnInfo {

    private String columnName;
    private String columnComment;
    private String columnType;
    private String dataType;
    private String isNullable;
    private String columnDefault;
    private String columnKey;
    private String extra;
}

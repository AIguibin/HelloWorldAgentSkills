package com.aiguibin.platform.dto.excel;

import lombok.Data;

@Data
public class ColumnInfo {

    private String columnName;

    private String columnComment;

    private String columnType;

    private Integer columnLength;

    private Integer decimalPlaces;

    private Boolean nullable;

    private String defaultValue;

    private Boolean primaryKey;

    private Boolean autoIncrement;

    private String dataCode;
}

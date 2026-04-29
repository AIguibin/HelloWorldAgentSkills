package com.aiguibin.platform.dto.excel;

import lombok.Data;

import java.util.List;

@Data
public class TableInfo {

    private String tableName;

    private String tableComment;

    private List<ColumnInfo> columns;

    private List<IndexInfo> indexes;
}

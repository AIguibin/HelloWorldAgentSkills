package com.aiguibin.platform.modules.dbcompare.model.dto;

import lombok.Data;

/**
 * 表信息
 *
 * @author aiguibin
 * @date 2025-01-15
 */
@Data
public class TableInfo {

    private String tableName;
    private String tableComment;
    private String tableSchema;
}

package com.aiguibin.platform.modules.dbcompare.model.dto;

import lombok.Data;

/**
 * 贯标字段标准
 *
 * @author aiguibin
 * @date 2025-01-15
 */
@Data
public class StandardField {

    private String columnName;
    private String columnComment;
    private String columnType;
    private String dataCode;
}

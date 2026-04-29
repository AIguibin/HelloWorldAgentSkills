package com.aiguibin.platform.modules.dbcompare.model.dto;

import lombok.Data;

/**
 * 贯标异常
 *
 * @author aiguibin
 * @date 2025-01-15
 */
@Data
public class StandardViolation {

    private String seq;
    private String fileName;
    private String checkDate;
    private String dbName;
    private String tableName;
    private String columnName;
    private String violationType;
    private String violationNote;
}

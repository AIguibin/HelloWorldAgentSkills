package com.aiguibin.platform.modules.dbcompare.model.dto;

import lombok.Data;

/**
 * 表差异
 *
 * @author aiguibin
 * @date 2025-01-15
 */
@Data
public class TableDiff {

    private String seq;
    private String fileName;
    private String checkDate;
    private String dbName;
    private String tableName;
    private String tableComment;
    private String diffType;
    private String diffNote;
    private String processScript;
    private String backupScript;
    private String remark;
}

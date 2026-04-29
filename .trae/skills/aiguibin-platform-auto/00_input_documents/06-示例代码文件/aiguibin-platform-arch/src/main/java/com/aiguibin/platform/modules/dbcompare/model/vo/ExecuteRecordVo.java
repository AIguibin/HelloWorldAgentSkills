package com.aiguibin.platform.modules.dbcompare.model.vo;

import lombok.Data;

/**
 * 执行记录VO
 *
 * @author aiguibin
 * @date 2025-01-15
 */
@Data
public class ExecuteRecordVo {

    private String recordId;
    private String env;
    private String dbName;
    private String triggerType;
    private String startTime;
    private String status;
    private int tableDiffCount;
    private int columnDiffCount;
    private int indexDiffCount;
}

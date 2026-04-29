package com.aiguibin.platform.modules.dbcompare.model.dto;

import lombok.Data;

/**
 * 单数据库比对详情
 *
 * @author aiguibin
 * @date 2025-01-15
 */
@Data
public class DbCompareDetail {

    private String dsKey;
    private String dbName;
    private long durationMs;
    private boolean success;
    private String errorMsg;
    private int tableDiffCount;
    private int columnDiffCount;
    private int indexDiffCount;
    private String resultPath;

    public static DbCompareDetail success(String dsKey, String dbName, long durationMs,
                                          int tableDiffCount, int columnDiffCount, int indexDiffCount) {
        DbCompareDetail detail = new DbCompareDetail();
        detail.setDsKey(dsKey);
        detail.setDbName(dbName);
        detail.setDurationMs(durationMs);
        detail.setSuccess(true);
        detail.setTableDiffCount(tableDiffCount);
        detail.setColumnDiffCount(columnDiffCount);
        detail.setIndexDiffCount(indexDiffCount);
        return detail;
    }

    public static DbCompareDetail fail(String dsKey, String errorMsg) {
        DbCompareDetail detail = new DbCompareDetail();
        detail.setDsKey(dsKey);
        detail.setSuccess(false);
        detail.setErrorMsg(errorMsg);
        return detail;
    }
}

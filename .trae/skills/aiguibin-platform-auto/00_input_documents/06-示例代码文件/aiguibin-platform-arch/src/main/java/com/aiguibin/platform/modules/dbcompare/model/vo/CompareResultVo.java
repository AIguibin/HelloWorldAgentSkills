package com.aiguibin.platform.modules.dbcompare.model.vo;

import com.aiguibin.platform.modules.dbcompare.model.dto.DbCompareDetail;
import com.aiguibin.platform.modules.dbcompare.model.dto.MenuFieldCheckResult;
import lombok.Data;

import java.util.List;

/**
 * 比对结果VO
 *
 * @author aiguibin
 * @date 2025-01-15
 */
@Data
public class CompareResultVo {

    private String env;
    private String triggerType;
    private String startTime;
    private long durationMs;
    private String status;
    private int totalDbCount;
    private int successCount;
    private int totalTableDiff;
    private int totalColumnDiff;
    private int totalIndexDiff;
    private List<DbCompareDetail> dbResults;
    private List<MenuFieldCheckResult> menuCheckResults;
}

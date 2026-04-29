package com.aiguibin.platform.controller;

import com.baomidou.mybatisplus.core.conditions.query.LambdaQueryWrapper;
import com.baomidou.mybatisplus.extension.plugins.pagination.Page;
import com.aiguibin.platform.common.result.Result;
import com.aiguibin.platform.entity.DbExecuteRecord;
import com.aiguibin.platform.mapper.DbExecuteRecordMapper;
import com.aiguibin.platform.service.DbCompareService;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.Parameter;
import io.swagger.v3.oas.annotations.tags.Tag;
import lombok.RequiredArgsConstructor;
import org.springframework.web.bind.annotation.*;

@Tag(name = "数据库比对", description = "数据库比对执行、记录查询等接口")
@RestController
@RequestMapping("/api/db/compare")
@RequiredArgsConstructor
public class DbCompareController {

    private final DbCompareService dbCompareService;
    private final DbExecuteRecordMapper dbExecuteRecordMapper;

    @Operation(summary = "执行数据库比对")
    @PostMapping("/execute/{datasourceId}")
    public Result<String> executeCompare(
            @Parameter(description = "数据源ID", required = true)
            @PathVariable Long datasourceId) {
        String recordNo = dbCompareService.executeCompare(datasourceId);
        return Result.success(recordNo);
    }

    @Operation(summary = "分页查询比对记录")
    @GetMapping("/records/page")
    public Result<Page<DbExecuteRecord>> queryRecordsPage(
            @Parameter(description = "页码", defaultValue = "1")
            @RequestParam(defaultValue = "1") Integer pageNum,
            @Parameter(description = "每页条数", defaultValue = "10")
            @RequestParam(defaultValue = "10") Integer pageSize,
            @Parameter(description = "环境")
            @RequestParam(required = false) String env,
            @Parameter(description = "状态")
            @RequestParam(required = false) String status) {
        
        Page<DbExecuteRecord> page = new Page<>(pageNum, pageSize);
        LambdaQueryWrapper<DbExecuteRecord> wrapper = new LambdaQueryWrapper<>();
        if (env != null) {
            wrapper.eq(DbExecuteRecord::getEnv, env);
        }
        if (status != null) {
            wrapper.eq(DbExecuteRecord::getStatus, status);
        }
        wrapper.orderByDesc(DbExecuteRecord::getCreateTime);
        
        Page<DbExecuteRecord> resultPage = dbExecuteRecordMapper.selectPage(page, wrapper);
        return Result.success(resultPage);
    }

    @Operation(summary = "获取比对记录详情")
    @GetMapping("/records/{recordId}")
    public Result<DbExecuteRecord> getRecordDetail(
            @Parameter(description = "记录ID", required = true)
            @PathVariable Long recordId) {
        DbExecuteRecord record = dbExecuteRecordMapper.selectById(recordId);
        return Result.success(record);
    }
}

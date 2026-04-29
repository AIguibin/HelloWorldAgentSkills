package com.aiguibin.platform.controller;

import com.baomidou.mybatisplus.extension.plugins.pagination.Page;
import com.aiguibin.platform.common.result.Result;
import com.aiguibin.platform.dto.OperLogQueryDTO;
import com.aiguibin.platform.service.OperLogService;
import com.aiguibin.platform.vo.OperLogVO;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.Parameter;
import io.swagger.v3.oas.annotations.tags.Tag;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import org.springframework.web.bind.annotation.*;

@Tag(name = "操作日志", description = "操作日志查询、删除等接口")
@RestController
@RequestMapping("/api/system/oper-logs")
@RequiredArgsConstructor
public class OperLogController {

    private final OperLogService operLogService;

    @Operation(summary = "分页查询操作日志")
    @GetMapping("/page")
    public Result<Page<OperLogVO>> queryOperLogPage(@Valid OperLogQueryDTO queryDTO) {
        Page<OperLogVO> page = operLogService.queryOperLogPage(queryDTO);
        return Result.success(page);
    }

    @Operation(summary = "获取操作日志详情")
    @GetMapping("/{logId}")
    public Result<OperLogVO> getOperLogDetail(
            @Parameter(description = "日志ID", required = true)
            @PathVariable Long logId) {
        OperLogVO logVO = operLogService.getOperLogDetail(logId);
        return Result.success(logVO);
    }

    @Operation(summary = "删除操作日志")
    @DeleteMapping("/{logId}")
    public Result<Void> deleteOperLog(
            @Parameter(description = "日志ID", required = true)
            @PathVariable Long logId) {
        operLogService.deleteOperLog(logId);
        return Result.success();
    }

    @Operation(summary = "清空操作日志")
    @DeleteMapping("/clear")
    public Result<Void> clearOperLog() {
        operLogService.clearOperLog();
        return Result.success();
    }
}

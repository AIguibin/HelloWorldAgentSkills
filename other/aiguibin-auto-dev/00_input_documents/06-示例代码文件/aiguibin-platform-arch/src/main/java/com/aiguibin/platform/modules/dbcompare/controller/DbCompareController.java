package com.aiguibin.platform.modules.dbcompare.controller;

import com.aiguibin.platform.common.result.Result;
import com.aiguibin.platform.modules.dbcompare.model.vo.CompareResultVo;
import com.aiguibin.platform.modules.dbcompare.model.vo.ExecuteRecordVo;
import com.aiguibin.platform.modules.dbcompare.service.DbCompareService;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.tags.Tag;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.web.bind.annotation.*;

import java.util.List;

/**
 * 数据库比对控制器
 *
 * @author aiguibin
 * @date 2025-01-15
 */
@Slf4j
@RestController
@RequestMapping("/api/dbcompare")
@RequiredArgsConstructor
@Tag(name = "数据库比对", description = "数据库设计文档比对接口")
public class DbCompareController {

    private final DbCompareService compareService;

    @PostMapping("/dev")
    @Operation(summary = "执行DEV环境比对")
    public Result<CompareResultVo> compareDev() {
        log.info("执行DEV环境比对");
        CompareResultVo result = compareService.compareEnv("DEV", "MANUAL");
        return Result.success(result);
    }

    @PostMapping("/sit")
    @Operation(summary = "执行SIT环境比对")
    public Result<CompareResultVo> compareSit() {
        log.info("执行SIT环境比对");
        CompareResultVo result = compareService.compareEnv("SIT", "MANUAL");
        return Result.success(result);
    }

    @PostMapping("/uat")
    @Operation(summary = "执行UAT环境比对")
    public Result<CompareResultVo> compareUat() {
        log.info("执行UAT环境比对");
        CompareResultVo result = compareService.compareEnv("UAT", "MANUAL");
        return Result.success(result);
    }

    @PostMapping("/all")
    @Operation(summary = "执行全环境比对")
    public Result<List<CompareResultVo>> compareAll() {
        log.info("执行全环境比对");
        List<CompareResultVo> results = compareService.compareAllEnv("MANUAL");
        return Result.success(results);
    }

    @PostMapping("/{env}/{dbKey}")
    @Operation(summary = "执行指定数据库比对")
    public Result<CompareResultVo> compareSingleDb(@PathVariable String env, @PathVariable String dbKey) {
        log.info("执行{}环境{}数据库比对", env, dbKey);
        CompareResultVo result = compareService.compareSingleDb(env, dbKey, "MANUAL");
        return Result.success(result);
    }

    @GetMapping("/records")
    @Operation(summary = "查询执行记录")
    public Result<List<ExecuteRecordVo>> getRecords(
            @RequestParam(required = false) String env,
            @RequestParam(required = false) String status) {
        List<ExecuteRecordVo> records = compareService.getRecords(env, status);
        return Result.success(records);
    }

    @GetMapping("/result/{recordId}")
    @Operation(summary = "获取执行结果")
    public Result<CompareResultVo> getResult(@PathVariable String recordId) {
        CompareResultVo result = compareService.getResult(recordId);
        return Result.success(result);
    }
}

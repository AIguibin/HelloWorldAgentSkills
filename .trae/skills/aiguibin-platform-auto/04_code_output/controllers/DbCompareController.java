package com.aiguibin.platform.modules.dbcompare.controller;

import com.aiguibin.platform.common.model.Result;
import com.aiguibin.platform.modules.dbcompare.service.DbCompareService;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.tags.Tag;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.*;

@Tag(name = "数据库比对")
@RestController
@RequestMapping("/api/dbcompare")
@Slf4j
public class DbCompareController {
    
    @Autowired
    private DbCompareService compareService;
    
    @Operation(summary = "执行DEV环境比对")
    @PostMapping("/dev")
    public Result<Void> compareDev() {
        compareService.compareEnv("DEV", "MANUAL");
        return Result.success();
    }
    
    @Operation(summary = "执行SIT环境比对")
    @PostMapping("/sit")
    public Result<Void> compareSit() {
        compareService.compareEnv("SIT", "MANUAL");
        return Result.success();
    }
    
    @Operation(summary = "执行UAT环境比对")
    @PostMapping("/uat")
    public Result<Void> compareUat() {
        compareService.compareEnv("UAT", "MANUAL");
        return Result.success();
    }
    
    @Operation(summary = "执行全环境比对")
    @PostMapping("/all")
    public Result<Void> compareAll() {
        compareService.compareAllEnv("MANUAL");
        return Result.success();
    }
    
    @Operation(summary = "执行指定环境指定数据库比对")
    @PostMapping("/{env}/{db}")
    public Result<Void> compareSingle(@PathVariable String env, @PathVariable String db) {
        compareService.compareSingleDb(env, db);
        return Result.success();
    }
}

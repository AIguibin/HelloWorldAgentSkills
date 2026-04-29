package com.aiguibin.platform.controller;

import com.aiguibin.platform.common.result.Result;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.tags.Tag;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import java.time.LocalDateTime;
import java.util.HashMap;
import java.util.Map;

@Tag(name = "测试接口", description = "项目测试接口")
@RestController
@RequestMapping("/test")
public class TestController {
    
    @Operation(summary = "健康检查")
    @GetMapping("/health")
    public Result<Map<String, Object>> health() {
        Map<String, Object> data = new HashMap<>();
        data.put("status", "UP");
        data.put("timestamp", LocalDateTime.now());
        data.put("service", "aiguibin-platform-arch");
        data.put("version", "1.0.0");
        return Result.success(data);
    }
    
    @Operation(summary = "欢迎页面")
    @GetMapping("/welcome")
    public Result<String> welcome() {
        return Result.success("欢迎使用 AI Guibin Platform!");
    }
}

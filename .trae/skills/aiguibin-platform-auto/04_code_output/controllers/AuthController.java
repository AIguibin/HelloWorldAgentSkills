package com.aiguibin.platform.core.auth.controller;

import com.aiguibin.platform.common.model.Result;
import com.aiguibin.platform.core.auth.dto.*;
import com.aiguibin.platform.core.auth.service.AuthService;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.tags.Tag;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.validation.Valid;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.*;

@Tag(name = "认证管理")
@RestController
@RequestMapping("/api/auth")
@Slf4j
public class AuthController {
    
    @Autowired
    private AuthService authService;
    
    @Operation(summary = "第一步登录-账号密码验证")
    @PostMapping("/login")
    public Result<LoginStep1Response> login(@RequestBody @Valid LoginRequest request,
                                             HttpServletRequest httpRequest) {
        String ip = getClientIp(httpRequest);
        LoginStep1Response response = authService.loginStep1(request, ip);
        return Result.success(response);
    }
    
    @Operation(summary = "第二步登录-选择机构")
    @PostMapping("/select-org")
    public Result<LoginResponse> selectOrg(@RequestBody @Valid SelectOrgRequest request) {
        LoginResponse response = authService.loginStep2(request);
        return Result.success(response);
    }
    
    @Operation(summary = "登出")
    @PostMapping("/logout")
    public Result<Void> logout(@RequestHeader(value = "Authorization", required = false) String token) {
        if (token != null && token.startsWith("Bearer ")) {
            authService.logout(token.substring(7));
        }
        return Result.success();
    }
    
    @Operation(summary = "刷新Token")
    @PostMapping("/refresh")
    public Result<TokenResponse> refresh(@RequestHeader("X-Refresh-Token") String refreshToken) {
        TokenResponse response = authService.refreshToken(refreshToken);
        return Result.success(response);
    }
    
    @Operation(summary = "获取当前用户信息")
    @GetMapping("/user-info")
    public Result<UserInfoResponse> getUserInfo() {
        return Result.success(authService.getCurrentUserInfo());
    }
    
    private String getClientIp(HttpServletRequest request) {
        String ip = request.getHeader("X-Forwarded-For");
        if (ip == null || ip.isEmpty() || "unknown".equalsIgnoreCase(ip)) {
            ip = request.getHeader("X-Real-IP");
        }
        if (ip == null || ip.isEmpty() || "unknown".equalsIgnoreCase(ip)) {
            ip = request.getRemoteAddr();
        }
        return ip;
    }
}

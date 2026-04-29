package com.aiguibin.platform.controller;

import com.aiguibin.platform.common.result.Result;
import com.aiguibin.platform.dto.LoginStep1DTO;
import com.aiguibin.platform.dto.LoginStep2DTO;
import com.aiguibin.platform.service.AuthService;
import com.aiguibin.platform.vo.LoginStep1VO;
import com.aiguibin.platform.vo.LoginStep2VO;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.tags.Tag;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import org.springframework.web.bind.annotation.*;

@Tag(name = "认证授权", description = "用户认证与授权接口")
@RestController
@RequestMapping("/auth")
@RequiredArgsConstructor
public class AuthController {
    
    private final AuthService authService;
    
    @Operation(summary = "第一步登录 - 账号密码验证")
    @PostMapping("/login/step1")
    public Result<LoginStep1VO> loginStep1(@Valid @RequestBody LoginStep1DTO dto) {
        LoginStep1VO vo = authService.loginStep1(dto);
        return Result.success(vo);
    }
    
    @Operation(summary = "第二步登录 - 选择机构")
    @PostMapping("/login/step2")
    public Result<LoginStep2VO> loginStep2(@Valid @RequestBody LoginStep2DTO dto) {
        LoginStep2VO vo = authService.loginStep2(dto);
        return Result.success(vo);
    }
    
    @Operation(summary = "用户登出")
    @PostMapping("/logout")
    public Result<Void> logout(@RequestHeader(value = "Authorization", required = false) String token) {
        authService.logout(token);
        return Result.success();
    }
}

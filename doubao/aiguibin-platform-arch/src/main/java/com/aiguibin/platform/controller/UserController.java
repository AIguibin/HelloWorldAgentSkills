package com.aiguibin.platform.controller;

import com.baomidou.mybatisplus.extension.plugins.pagination.Page;
import com.aiguibin.platform.common.result.Result;
import com.aiguibin.platform.dto.UserCreateDTO;
import com.aiguibin.platform.dto.UserQueryDTO;
import com.aiguibin.platform.dto.UserUpdateDTO;
import com.aiguibin.platform.service.UserService;
import com.aiguibin.platform.vo.UserVO;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.Parameter;
import io.swagger.v3.oas.annotations.tags.Tag;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import org.springframework.web.bind.annotation.*;

@Tag(name = "用户管理", description = "用户增删改查、密码重置、锁定解锁等接口")
@RestController
@RequestMapping("/api/system/users")
@RequiredArgsConstructor
public class UserController {

    private final UserService userService;

    @Operation(summary = "分页查询用户列表")
    @GetMapping("/page")
    public Result<Page<UserVO>> queryUserPage(@Valid UserQueryDTO queryDTO) {
        Page<UserVO> page = userService.queryUserPage(queryDTO);
        return Result.success(page);
    }

    @Operation(summary = "获取用户详情")
    @GetMapping("/{userId}")
    public Result<UserVO> getUserDetail(
            @Parameter(description = "用户ID", required = true)
            @PathVariable Long userId) {
        UserVO userVO = userService.getUserDetail(userId);
        return Result.success(userVO);
    }

    @Operation(summary = "创建用户")
    @PostMapping
    public Result<Void> createUser(@Valid @RequestBody UserCreateDTO createDTO) {
        userService.createUser(createDTO);
        return Result.success();
    }

    @Operation(summary = "更新用户")
    @PutMapping
    public Result<Void> updateUser(@Valid @RequestBody UserUpdateDTO updateDTO) {
        userService.updateUser(updateDTO);
        return Result.success();
    }

    @Operation(summary = "删除用户")
    @DeleteMapping("/{userId}")
    public Result<Void> deleteUser(
            @Parameter(description = "用户ID", required = true)
            @PathVariable Long userId) {
        userService.deleteUser(userId);
        return Result.success();
    }

    @Operation(summary = "重置密码")
    @PostMapping("/{userId}/reset-password")
    public Result<Void> resetPassword(
            @Parameter(description = "用户ID", required = true)
            @PathVariable Long userId,
            @Parameter(description = "新密码", required = true)
            @RequestParam String newPassword) {
        userService.resetPassword(userId, newPassword);
        return Result.success();
    }

    @Operation(summary = "锁定/解锁用户")
    @PostMapping("/{userId}/toggle-lock")
    public Result<Void> toggleLock(
            @Parameter(description = "用户ID", required = true)
            @PathVariable Long userId,
            @Parameter(description = "是否锁定：0-解锁，1-锁定", required = true)
            @RequestParam Integer isLocked,
            @Parameter(description = "锁定原因")
            @RequestParam(required = false) String lockReason) {
        userService.toggleLock(userId, isLocked, lockReason);
        return Result.success();
    }
}

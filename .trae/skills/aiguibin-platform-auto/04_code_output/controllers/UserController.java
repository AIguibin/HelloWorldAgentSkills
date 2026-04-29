package com.aiguibin.platform.core.user.controller;

import com.aiguibin.platform.common.model.Result;
import com.aiguibin.platform.core.user.entity.SysUser;
import com.aiguibin.platform.core.user.service.SysUserService;
import com.baomidou.mybatisplus.core.metadata.IPage;
import com.baomidou.mybatisplus.extension.plugins.pagination.Page;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.tags.Tag;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.*;

@Tag(name = "用户管理")
@RestController
@RequestMapping("/api/user")
@Slf4j
public class UserController {
    
    @Autowired
    private SysUserService userService;
    
    @Operation(summary = "用户列表")
    @GetMapping
    public Result<IPage<SysUser>> list(Page<SysUser> page, SysUser query) {
        IPage<SysUser> result = userService.page(page);
        return Result.success(result);
    }
    
    @Operation(summary = "新增用户")
    @PostMapping
    public Result<Void> add(@RequestBody SysUser user) {
        userService.save(user);
        return Result.success();
    }
    
    @Operation(summary = "编辑用户")
    @PutMapping("/{id}")
    public Result<Void> update(@PathVariable Long id, @RequestBody SysUser user) {
        user.setId(id);
        userService.updateById(user);
        return Result.success();
    }
    
    @Operation(summary = "删除用户")
    @DeleteMapping("/{id}")
    public Result<Void> delete(@PathVariable Long id) {
        userService.removeById(id);
        return Result.success();
    }
    
    @Operation(summary = "锁定用户")
    @PostMapping("/{id}/lock")
    public Result<Void> lock(@PathVariable Long id, @RequestParam String reason) {
        userService.lockUser(id, reason);
        return Result.success();
    }
    
    @Operation(summary = "解锁用户")
    @PostMapping("/{id}/unlock")
    public Result<Void> unlock(@PathVariable Long id) {
        userService.unlockUser(id);
        return Result.success();
    }
}

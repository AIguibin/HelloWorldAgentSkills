package com.aiguibin.platform.core.role.controller;

import com.aiguibin.platform.common.model.Result;
import com.aiguibin.platform.core.role.entity.SysRole;
import com.aiguibin.platform.core.role.service.SysRoleService;
import com.baomidou.mybatisplus.core.metadata.IPage;
import com.baomidou.mybatisplus.extension.plugins.pagination.Page;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.tags.Tag;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.*;

@Tag(name = "角色管理")
@RestController
@RequestMapping("/api/role")
@Slf4j
public class RoleController {
    
    @Autowired
    private SysRoleService roleService;
    
    @Operation(summary = "角色列表")
    @GetMapping
    public Result<IPage<SysRole>> list(Page<SysRole> page) {
        IPage<SysRole> result = roleService.page(page);
        return Result.success(result);
    }
    
    @Operation(summary = "新增角色")
    @PostMapping
    public Result<Void> add(@RequestBody SysRole role) {
        roleService.save(role);
        return Result.success();
    }
    
    @Operation(summary = "编辑角色")
    @PutMapping("/{id}")
    public Result<Void> update(@PathVariable Long id, @RequestBody SysRole role) {
        role.setId(id);
        roleService.updateById(role);
        return Result.success();
    }
    
    @Operation(summary = "删除角色")
    @DeleteMapping("/{id}")
    public Result<Void> delete(@PathVariable Long id) {
        roleService.removeById(id);
        return Result.success();
    }
}

package com.aiguibin.platform.controller;

import com.baomidou.mybatisplus.extension.plugins.pagination.Page;
import com.aiguibin.platform.common.result.Result;
import com.aiguibin.platform.dto.RoleCreateDTO;
import com.aiguibin.platform.dto.RoleQueryDTO;
import com.aiguibin.platform.dto.RoleUpdateDTO;
import com.aiguibin.platform.service.RoleService;
import com.aiguibin.platform.vo.RoleVO;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.Parameter;
import io.swagger.v3.oas.annotations.tags.Tag;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@Tag(name = "角色管理", description = "角色增删改查等接口")
@RestController
@RequestMapping("/api/system/roles")
@RequiredArgsConstructor
public class RoleController {

    private final RoleService roleService;

    @Operation(summary = "分页查询角色列表")
    @GetMapping("/page")
    public Result<Page<RoleVO>> queryRolePage(@Valid RoleQueryDTO queryDTO) {
        Page<RoleVO> page = roleService.queryRolePage(queryDTO);
        return Result.success(page);
    }

    @Operation(summary = "获取所有启用的角色")
    @GetMapping("/all")
    public Result<List<RoleVO>> getAllRoles() {
        List<RoleVO> roleList = roleService.getAllRoles();
        return Result.success(roleList);
    }

    @Operation(summary = "获取角色详情")
    @GetMapping("/{roleId}")
    public Result<RoleVO> getRoleDetail(
            @Parameter(description = "角色ID", required = true)
            @PathVariable Long roleId) {
        RoleVO roleVO = roleService.getRoleDetail(roleId);
        return Result.success(roleVO);
    }

    @Operation(summary = "创建角色")
    @PostMapping
    public Result<Void> createRole(@Valid @RequestBody RoleCreateDTO createDTO) {
        roleService.createRole(createDTO);
        return Result.success();
    }

    @Operation(summary = "更新角色")
    @PutMapping
    public Result<Void> updateRole(@Valid @RequestBody RoleUpdateDTO updateDTO) {
        roleService.updateRole(updateDTO);
        return Result.success();
    }

    @Operation(summary = "删除角色")
    @DeleteMapping("/{roleId}")
    public Result<Void> deleteRole(
            @Parameter(description = "角色ID", required = true)
            @PathVariable Long roleId) {
        roleService.deleteRole(roleId);
        return Result.success();
    }
}

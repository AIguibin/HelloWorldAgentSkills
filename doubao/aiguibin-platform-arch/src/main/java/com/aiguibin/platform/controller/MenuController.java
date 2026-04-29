package com.aiguibin.platform.controller;

import com.aiguibin.platform.common.result.Result;
import com.aiguibin.platform.dto.MenuCreateDTO;
import com.aiguibin.platform.dto.MenuQueryDTO;
import com.aiguibin.platform.dto.MenuUpdateDTO;
import com.aiguibin.platform.service.MenuService;
import com.aiguibin.platform.vo.MenuTreeVO;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.Parameter;
import io.swagger.v3.oas.annotations.tags.Tag;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@Tag(name = "菜单管理", description = "菜单树查询、增删改查等接口")
@RestController
@RequestMapping("/api/system/menus")
@RequiredArgsConstructor
public class MenuController {

    private final MenuService menuService;

    @Operation(summary = "获取菜单树")
    @GetMapping("/tree")
    public Result<List<MenuTreeVO>> getMenuTree(@Valid MenuQueryDTO queryDTO) {
        List<MenuTreeVO> treeList = menuService.getMenuTree(queryDTO);
        return Result.success(treeList);
    }

    @Operation(summary = "获取菜单详情")
    @GetMapping("/{menuId}")
    public Result<MenuTreeVO> getMenuDetail(
            @Parameter(description = "菜单ID", required = true)
            @PathVariable Long menuId) {
        MenuTreeVO menuVO = menuService.getMenuDetail(menuId);
        return Result.success(menuVO);
    }

    @Operation(summary = "创建菜单")
    @PostMapping
    public Result<Void> createMenu(@Valid @RequestBody MenuCreateDTO createDTO) {
        menuService.createMenu(createDTO);
        return Result.success();
    }

    @Operation(summary = "更新菜单")
    @PutMapping
    public Result<Void> updateMenu(@Valid @RequestBody MenuUpdateDTO updateDTO) {
        menuService.updateMenu(updateDTO);
        return Result.success();
    }

    @Operation(summary = "删除菜单")
    @DeleteMapping("/{menuId}")
    public Result<Void> deleteMenu(
            @Parameter(description = "菜单ID", required = true)
            @PathVariable Long menuId) {
        menuService.deleteMenu(menuId);
        return Result.success();
    }
}

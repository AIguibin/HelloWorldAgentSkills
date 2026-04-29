package com.aiguibin.platform.controller;

import com.baomidou.mybatisplus.extension.plugins.pagination.Page;
import com.aiguibin.platform.common.result.Result;
import com.aiguibin.platform.dto.DatasourceCreateDTO;
import com.aiguibin.platform.dto.DatasourceQueryDTO;
import com.aiguibin.platform.dto.DatasourceUpdateDTO;
import com.aiguibin.platform.service.DatasourceService;
import com.aiguibin.platform.vo.DatasourceVO;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.Parameter;
import io.swagger.v3.oas.annotations.tags.Tag;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@Tag(name = "数据源配置", description = "数据源CRUD、连接测试等接口")
@RestController
@RequestMapping("/api/db/datasources")
@RequiredArgsConstructor
public class DatasourceController {

    private final DatasourceService datasourceService;

    @Operation(summary = "分页查询数据源列表")
    @GetMapping("/page")
    public Result<Page<DatasourceVO>> queryDatasourcePage(@Valid DatasourceQueryDTO queryDTO) {
        Page<DatasourceVO> page = datasourceService.queryDatasourcePage(queryDTO);
        return Result.success(page);
    }

    @Operation(summary = "获取所有启用的数据源")
    @GetMapping("/all")
    public Result<List<DatasourceVO>> getAllEnabledDatasources() {
        List<DatasourceVO> dsList = datasourceService.getAllEnabledDatasources();
        return Result.success(dsList);
    }

    @Operation(summary = "获取数据源详情")
    @GetMapping("/{dsId}")
    public Result<DatasourceVO> getDatasourceDetail(
            @Parameter(description = "数据源ID", required = true)
            @PathVariable Long dsId) {
        DatasourceVO dsVO = datasourceService.getDatasourceDetail(dsId);
        return Result.success(dsVO);
    }

    @Operation(summary = "创建数据源")
    @PostMapping
    public Result<Void> createDatasource(@Valid @RequestBody DatasourceCreateDTO createDTO) {
        datasourceService.createDatasource(createDTO);
        return Result.success();
    }

    @Operation(summary = "更新数据源")
    @PutMapping
    public Result<Void> updateDatasource(@Valid @RequestBody DatasourceUpdateDTO updateDTO) {
        datasourceService.updateDatasource(updateDTO);
        return Result.success();
    }

    @Operation(summary = "删除数据源")
    @DeleteMapping("/{dsId}")
    public Result<Void> deleteDatasource(
            @Parameter(description = "数据源ID", required = true)
            @PathVariable Long dsId) {
        datasourceService.deleteDatasource(dsId);
        return Result.success();
    }

    @Operation(summary = "测试数据源连接（按ID）")
    @PostMapping("/{dsId}/test")
    public Result<Boolean> testConnection(
            @Parameter(description = "数据源ID", required = true)
            @PathVariable Long dsId) {
        boolean success = datasourceService.testConnection(dsId);
        return Result.success(success);
    }

    @Operation(summary = "测试数据源连接（按配置）")
    @PostMapping("/test")
    public Result<Boolean> testConnectionByConfig(@Valid @RequestBody DatasourceCreateDTO config) {
        boolean success = datasourceService.testConnectionByConfig(config);
        return Result.success(success);
    }
}

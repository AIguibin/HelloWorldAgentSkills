package com.aiguibin.platform.controller;

import com.aiguibin.platform.common.result.Result;
import com.aiguibin.platform.dto.OrgCreateDTO;
import com.aiguibin.platform.dto.OrgQueryDTO;
import com.aiguibin.platform.dto.OrgUpdateDTO;
import com.aiguibin.platform.service.OrgService;
import com.aiguibin.platform.vo.OrgTreeVO;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.Parameter;
import io.swagger.v3.oas.annotations.tags.Tag;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@Tag(name = "机构管理", description = "机构树查询、增删改查等接口")
@RestController
@RequestMapping("/api/system/orgs")
@RequiredArgsConstructor
public class OrgController {

    private final OrgService orgService;

    @Operation(summary = "获取机构树")
    @GetMapping("/tree")
    public Result<List<OrgTreeVO>> getOrgTree(@Valid OrgQueryDTO queryDTO) {
        List<OrgTreeVO> treeList = orgService.getOrgTree(queryDTO);
        return Result.success(treeList);
    }

    @Operation(summary = "获取机构详情")
    @GetMapping("/{orgId}")
    public Result<OrgTreeVO> getOrgDetail(
            @Parameter(description = "机构ID", required = true)
            @PathVariable Long orgId) {
        OrgTreeVO orgVO = orgService.getOrgDetail(orgId);
        return Result.success(orgVO);
    }

    @Operation(summary = "创建机构")
    @PostMapping
    public Result<Void> createOrg(@Valid @RequestBody OrgCreateDTO createDTO) {
        orgService.createOrg(createDTO);
        return Result.success();
    }

    @Operation(summary = "更新机构")
    @PutMapping
    public Result<Void> updateOrg(@Valid @RequestBody OrgUpdateDTO updateDTO) {
        orgService.updateOrg(updateDTO);
        return Result.success();
    }

    @Operation(summary = "删除机构")
    @DeleteMapping("/{orgId}")
    public Result<Void> deleteOrg(
            @Parameter(description = "机构ID", required = true)
            @PathVariable Long orgId) {
        orgService.deleteOrg(orgId);
        return Result.success();
    }
}

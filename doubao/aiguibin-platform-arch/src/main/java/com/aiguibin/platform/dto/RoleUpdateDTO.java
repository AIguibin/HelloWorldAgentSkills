package com.aiguibin.platform.dto;

import io.swagger.v3.oas.annotations.media.Schema;
import lombok.Data;

import java.util.List;

@Data
@Schema(description = "角色更新请求")
public class RoleUpdateDTO {

    @Schema(description = "角色ID", required = true)
    private Long id;

    @Schema(description = "角色名称")
    private String roleName;

    @Schema(description = "角色类型")
    private String roleType;

    @Schema(description = "数据权限范围")
    private Integer dataScope;

    @Schema(description = "备注")
    private String remark;

    @Schema(description = "状态")
    private Integer status;

    @Schema(description = "菜单ID列表")
    private List<Long> menuIds;
}

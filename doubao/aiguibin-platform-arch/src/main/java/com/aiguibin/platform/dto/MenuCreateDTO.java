package com.aiguibin.platform.dto;

import io.swagger.v3.oas.annotations.media.Schema;
import jakarta.validation.constraints.NotBlank;
import lombok.Data;

@Data
@Schema(description = "菜单创建请求")
public class MenuCreateDTO {

    @Schema(description = "菜单编码", required = true)
    @NotBlank(message = "菜单编码不能为空")
    private String menuCode;

    @Schema(description = "菜单名称", required = true)
    @NotBlank(message = "菜单名称不能为空")
    private String menuName;

    @Schema(description = "父菜单ID")
    private Long parentId;

    @Schema(description = "菜单类型：1-目录，2-菜单，3-按钮", required = true)
    private Integer menuType;

    @Schema(description = "图标")
    private String icon;

    @Schema(description = "路由地址")
    private String path;

    @Schema(description = "组件路径")
    private String component;

    @Schema(description = "权限标识")
    private String permission;

    @Schema(description = "排序")
    private Integer sortOrder;
}

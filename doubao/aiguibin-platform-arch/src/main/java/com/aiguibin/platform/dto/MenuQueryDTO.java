package com.aiguibin.platform.dto;

import io.swagger.v3.oas.annotations.media.Schema;
import lombok.Data;

@Data
@Schema(description = "菜单查询请求")
public class MenuQueryDTO {

    @Schema(description = "菜单名称")
    private String menuName;

    @Schema(description = "菜单类型")
    private Integer menuType;

    @Schema(description = "状态")
    private Integer status;
}

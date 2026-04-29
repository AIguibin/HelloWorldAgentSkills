package com.aiguibin.platform.dto;

import io.swagger.v3.oas.annotations.media.Schema;
import lombok.Data;

@Data
@Schema(description = "机构更新请求")
public class OrgUpdateDTO {

    @Schema(description = "机构ID", required = true)
    private Long id;

    @Schema(description = "机构名称")
    private String orgName;

    @Schema(description = "机构类型")
    private String orgType;

    @Schema(description = "上级机构编码")
    private String parentCode;

    @Schema(description = "排序")
    private Integer sortOrder;

    @Schema(description = "状态")
    private Integer status;
}

package com.aiguibin.platform.dto;

import io.swagger.v3.oas.annotations.media.Schema;
import jakarta.validation.constraints.NotBlank;
import lombok.Data;

@Data
@Schema(description = "机构创建请求")
public class OrgCreateDTO {

    @Schema(description = "机构编码", required = true)
    @NotBlank(message = "机构编码不能为空")
    private String orgCode;

    @Schema(description = "机构名称", required = true)
    @NotBlank(message = "机构名称不能为空")
    private String orgName;

    @Schema(description = "机构类型", required = true)
    @NotBlank(message = "机构类型不能为空")
    private String orgType;

    @Schema(description = "上级机构编码")
    private String parentCode;

    @Schema(description = "排序")
    private Integer sortOrder;
}

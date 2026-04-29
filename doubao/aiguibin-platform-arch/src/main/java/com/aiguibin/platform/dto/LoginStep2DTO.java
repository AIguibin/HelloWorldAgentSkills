package com.aiguibin.platform.dto;

import io.swagger.v3.oas.annotations.media.Schema;
import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.NotNull;
import lombok.Data;

@Data
@Schema(description = "第二步登录请求")
public class LoginStep2DTO {
    
    @Schema(description = "临时Token", required = true)
    @NotBlank(message = "临时Token不能为空")
    private String tempToken;
    
    @Schema(description = "选择的机构编码", required = true)
    @NotBlank(message = "机构编码不能为空")
    private String orgCode;
}

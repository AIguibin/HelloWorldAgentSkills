package com.aiguibin.platform.vo;

import io.swagger.v3.oas.annotations.media.Schema;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
@Schema(description = "机构信息VO")
public class OrgVO {
    
    @Schema(description = "机构编码")
    private String orgCode;
    
    @Schema(description = "机构名称")
    private String orgName;
    
    @Schema(description = "机构类型")
    private String orgType;
}

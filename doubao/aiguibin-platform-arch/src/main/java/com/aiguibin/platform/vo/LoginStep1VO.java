package com.aiguibin.platform.vo;

import io.swagger.v3.oas.annotations.media.Schema;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.util.List;

@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
@Schema(description = "第一步登录响应")
public class LoginStep1VO {
    
    @Schema(description = "临时Token")
    private String tempToken;
    
    @Schema(description = "用户姓名")
    private String realName;
    
    @Schema(description = "可选择的机构列表")
    private List<OrgVO> orgList;
}

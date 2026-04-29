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
@Schema(description = "第二步登录响应")
public class LoginStep2VO {
    
    @Schema(description = "Access Token")
    private String accessToken;
    
    @Schema(description = "Refresh Token")
    private String refreshToken;
    
    @Schema(description = "Token类型")
    private String tokenType;
    
    @Schema(description = "过期时间(秒)")
    private Long expiresIn;
    
    @Schema(description = "用户信息")
    private UserInfoVO userInfo;
}

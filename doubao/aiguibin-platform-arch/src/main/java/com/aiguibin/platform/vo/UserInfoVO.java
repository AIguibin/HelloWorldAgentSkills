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
@Schema(description = "用户信息VO")
public class UserInfoVO {
    
    @Schema(description = "用户ID")
    private Long userId;
    
    @Schema(description = "用户名")
    private String username;
    
    @Schema(description = "真实姓名")
    private String realName;
    
    @Schema(description = "头像")
    private String avatar;
    
    @Schema(description = "当前机构编码")
    private String orgCode;
    
    @Schema(description = "当前机构名称")
    private String orgName;
    
    @Schema(description = "部门编码")
    private String deptCode;
    
    @Schema(description = "角色列表")
    private List<String> roles;
    
    @Schema(description = "权限列表")
    private List<String> permissions;
}

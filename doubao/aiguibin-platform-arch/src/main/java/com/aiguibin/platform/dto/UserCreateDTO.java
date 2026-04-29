package com.aiguibin.platform.dto;

import io.swagger.v3.oas.annotations.media.Schema;
import jakarta.validation.constraints.NotBlank;
import lombok.Data;

import java.util.List;

@Data
@Schema(description = "用户创建请求")
public class UserCreateDTO {
    
    @Schema(description = "用户编号", required = true)
    @NotBlank(message = "用户编号不能为空")
    private String userNo;
    
    @Schema(description = "用户名", required = true)
    @NotBlank(message = "用户名不能为空")
    private String username;
    
    @Schema(description = "密码", required = true)
    @NotBlank(message = "密码不能为空")
    private String password;
    
    @Schema(description = "真实姓名")
    private String realName;
    
    @Schema(description = "邮箱")
    private String email;
    
    @Schema(description = "手机号")
    private String phone;
    
    @Schema(description = "头像")
    private String avatar;
    
    @Schema(description = "默认机构编码")
    private String orgCode;
    
    @Schema(description = "默认部门编码")
    private String deptCode;
    
    @Schema(description = "角色ID列表")
    private List<Long> roleIds;
    
    @Schema(description = "机构编码列表")
    private List<String> orgCodes;
}

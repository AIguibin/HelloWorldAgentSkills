package com.aiguibin.platform.vo;

import io.swagger.v3.oas.annotations.media.Schema;
import lombok.Data;

import java.time.LocalDateTime;
import java.util.List;

@Data
@Schema(description = "用户信息响应")
public class UserVO {

    @Schema(description = "用户ID")
    private Long id;

    @Schema(description = "用户编号")
    private String userNo;

    @Schema(description = "用户名")
    private String username;

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

    @Schema(description = "默认机构名称")
    private String orgName;

    @Schema(description = "默认部门编码")
    private String deptCode;

    @Schema(description = "默认部门名称")
    private String deptName;

    @Schema(description = "是否锁定")
    private Integer isLocked;

    @Schema(description = "锁定原因")
    private String lockReason;

    @Schema(description = "最后登录时间")
    private LocalDateTime lastLoginTime;

    @Schema(description = "最后登录IP")
    private String lastLoginIp;

    @Schema(description = "状态")
    private Integer status;

    @Schema(description = "创建时间")
    private LocalDateTime createTime;

    @Schema(description = "更新时间")
    private LocalDateTime updateTime;

    @Schema(description = "角色ID列表")
    private List<Long> roleIds;

    @Schema(description = "机构编码列表")
    private List<String> orgCodes;
}

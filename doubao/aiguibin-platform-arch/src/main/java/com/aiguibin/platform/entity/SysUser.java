package com.aiguibin.platform.entity;

import com.baomidou.mybatisplus.annotation.TableName;
import lombok.Data;
import lombok.EqualsAndHashCode;

@Data
@EqualsAndHashCode(callSuper = true)
@TableName("sys_user")
public class SysUser extends BaseEntity {
    
    private String userNo;
    
    private String username;
    
    private String password;
    
    private String realName;
    
    private String email;
    
    private String phone;
    
    private String avatar;
    
    private String orgCode;
    
    private String deptCode;
    
    private Integer isLocked;
    
    private String lockReason;
    
    private java.time.LocalDateTime lastLoginTime;
    
    private String lastLoginIp;
    
    private Integer status;
}

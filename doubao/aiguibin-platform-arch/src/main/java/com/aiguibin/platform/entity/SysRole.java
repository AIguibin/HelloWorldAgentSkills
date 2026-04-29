package com.aiguibin.platform.entity;

import com.baomidou.mybatisplus.annotation.TableName;
import lombok.Data;
import lombok.EqualsAndHashCode;

@Data
@EqualsAndHashCode(callSuper = true)
@TableName("sys_role")
public class SysRole extends BaseEntity {
    
    private String roleCode;
    
    private String roleName;
    
    private String roleType;
    
    private Integer dataScope;
    
    private String remark;
    
    private Integer status;
}

package com.aiguibin.platform.entity;

import com.baomidou.mybatisplus.annotation.TableName;
import lombok.Data;
import lombok.EqualsAndHashCode;

@Data
@EqualsAndHashCode(callSuper = true)
@TableName("sys_org")
public class SysOrg extends BaseEntity {
    
    private String orgCode;
    
    private String orgName;
    
    private String orgType;
    
    private String parentCode;
    
    private String parentCodes;
    
    private Integer level;
    
    private Integer sortOrder;
    
    private Integer status;
}

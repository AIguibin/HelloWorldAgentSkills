package com.aiguibin.platform.entity;

import com.baomidou.mybatisplus.annotation.TableName;
import lombok.Data;
import lombok.EqualsAndHashCode;

@Data
@EqualsAndHashCode(callSuper = true)
@TableName("sys_menu")
public class SysMenu extends BaseEntity {
    
    private String menuCode;
    
    private String menuName;
    
    private Long parentId;
    
    private Integer menuType;
    
    private String icon;
    
    private String path;
    
    private String component;
    
    private String permission;
    
    private Integer sortOrder;
    
    private Integer status;
}

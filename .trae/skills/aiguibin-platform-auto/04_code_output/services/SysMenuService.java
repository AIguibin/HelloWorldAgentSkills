package com.aiguibin.platform.core.menu.service;

import com.aiguibin.platform.core.menu.entity.SysMenu;
import com.baomidou.mybatisplus.extension.service.IService;
import java.util.List;

public interface SysMenuService extends IService<SysMenu> {
    
    List<SysMenu> getMenusByUserId(Long userId);
    
    List<SysMenu> getMenusByRoleId(Long roleId);
}

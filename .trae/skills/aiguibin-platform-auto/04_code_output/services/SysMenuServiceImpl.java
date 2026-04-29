package com.aiguibin.platform.core.menu.service.impl;

import com.aiguibin.platform.core.menu.entity.SysMenu;
import com.aiguibin.platform.core.menu.mapper.SysMenuMapper;
import com.aiguibin.platform.core.menu.service.SysMenuService;
import com.baomidou.mybatisplus.extension.service.impl.ServiceImpl;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;
import java.util.List;

@Service
public class SysMenuServiceImpl extends ServiceImpl<SysMenuMapper, SysMenu> implements SysMenuService {
    
    @Autowired
    private SysMenuMapper menuMapper;
    
    @Override
    public List<SysMenu> getMenusByUserId(Long userId) {
        return menuMapper.selectMenusByUserId(userId);
    }
    
    @Override
    public List<SysMenu> getMenusByRoleId(Long roleId) {
        return menuMapper.selectMenusByRoleId(roleId);
    }
}

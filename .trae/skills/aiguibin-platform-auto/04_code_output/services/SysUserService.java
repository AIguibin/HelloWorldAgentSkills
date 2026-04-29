package com.aiguibin.platform.core.user.service;

import com.aiguibin.platform.core.user.entity.SysUser;
import com.baomidou.mybatisplus.extension.service.IService;
import java.util.List;

public interface SysUserService extends IService<SysUser> {
    
    SysUser getByUsername(String username);
    
    List<String> getUserRoles(Long userId);
    
    List<String> getUserPermissions(Long userId);
    
    Integer getDataScope(Long userId);
    
    void updateLoginInfo(Long userId, String loginIp);
    
    void lockUser(Long userId, String lockReason);
    
    void unlockUser(Long userId);
}

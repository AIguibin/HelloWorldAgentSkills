package com.aiguibin.platform.core.user.service.impl;

import com.aiguibin.platform.core.user.entity.SysUser;
import com.aiguibin.platform.core.user.mapper.SysUserMapper;
import com.aiguibin.platform.core.user.service.SysUserService;
import com.baomidou.mybatisplus.extension.service.impl.ServiceImpl;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;
import java.util.List;

@Service
public class SysUserServiceImpl extends ServiceImpl<SysUserMapper, SysUser> implements SysUserService {
    
    @Autowired
    private SysUserMapper userMapper;
    
    @Override
    public SysUser getByUsername(String username) {
        return userMapper.selectByUsername(username);
    }
    
    @Override
    public List<String> getUserRoles(Long userId) {
        return userMapper.selectUserRoles(userId);
    }
    
    @Override
    public List<String> getUserPermissions(Long userId) {
        return userMapper.selectUserPermissions(userId);
    }
    
    @Override
    public Integer getDataScope(Long userId) {
        Integer dataScope = userMapper.selectDataScope(userId);
        return dataScope != null ? dataScope : 4;
    }
    
    @Override
    public void updateLoginInfo(Long userId, String loginIp) {
        userMapper.updateLoginInfo(userId, loginIp);
    }
    
    @Override
    public void lockUser(Long userId, String lockReason) {
        userMapper.lockUser(userId, lockReason);
    }
    
    @Override
    public void unlockUser(Long userId) {
        userMapper.unlockUser(userId);
    }
}

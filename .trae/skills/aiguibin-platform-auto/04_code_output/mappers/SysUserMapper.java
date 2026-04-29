package com.aiguibin.platform.core.user.mapper;

import com.aiguibin.platform.core.user.entity.SysUser;
import com.baomidou.mybatisplus.core.mapper.BaseMapper;
import org.apache.ibatis.annotations.Mapper;
import org.apache.ibatis.annotations.Param;
import java.util.List;

@Mapper
public interface SysUserMapper extends BaseMapper<SysUser> {
    
    SysUser selectByUsername(@Param("username") String username);
    
    List<String> selectUserRoles(@Param("userId") Long userId);
    
    List<String> selectUserPermissions(@Param("userId") Long userId);
    
    Integer selectDataScope(@Param("userId") Long userId);
    
    int updateLoginInfo(@Param("userId") Long userId, 
                        @Param("loginIp") String loginIp);
    
    int lockUser(@Param("userId") Long userId, 
                 @Param("lockReason") String lockReason);
    
    int unlockUser(@Param("userId") Long userId);
}

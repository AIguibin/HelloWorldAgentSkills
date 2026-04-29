package com.aiguibin.platform.mapper;

import com.aiguibin.platform.entity.SysUser;
import com.baomidou.mybatisplus.core.mapper.BaseMapper;
import org.apache.ibatis.annotations.Mapper;
import org.apache.ibatis.annotations.Param;

import java.util.List;

@Mapper
public interface SysUserMapper extends BaseMapper<SysUser> {
    
    SysUser selectByUsername(@Param("username") String username);
    
    List<Long> selectRoleIdsByUserId(@Param("userId") Long userId);
    
    List<String> selectPermissionsByUserId(@Param("userId") Long userId);
    
    List<String> selectOrgCodesByUserId(@Param("userId") Long userId);
}

package com.aiguibin.platform.mapper;

import com.aiguibin.platform.entity.SysRole;
import com.baomidou.mybatisplus.core.mapper.BaseMapper;
import org.apache.ibatis.annotations.Mapper;
import org.apache.ibatis.annotations.Param;

import java.util.List;

@Mapper
public interface SysRoleMapper extends BaseMapper<SysRole> {
    
    List<SysRole> selectRolesByUserId(@Param("userId") Long userId);
    
    List<Long> selectMenuIdsByRoleId(@Param("roleId") Long roleId);
}

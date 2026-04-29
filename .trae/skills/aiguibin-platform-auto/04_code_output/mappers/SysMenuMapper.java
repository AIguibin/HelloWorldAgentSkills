package com.aiguibin.platform.core.menu.mapper;

import com.aiguibin.platform.core.menu.entity.SysMenu;
import com.baomidou.mybatisplus.core.mapper.BaseMapper;
import org.apache.ibatis.annotations.Mapper;
import org.apache.ibatis.annotations.Param;
import java.util.List;

@Mapper
public interface SysMenuMapper extends BaseMapper<SysMenu> {
    
    List<SysMenu> selectMenusByUserId(@Param("userId") Long userId);
    
    List<SysMenu> selectMenusByRoleId(@Param("roleId") Long roleId);
}

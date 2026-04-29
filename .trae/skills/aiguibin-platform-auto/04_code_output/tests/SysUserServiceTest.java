package com.aiguibin.platform.core.user.service;

import com.aiguibin.platform.core.user.entity.SysUser;
import com.aiguibin.platform.core.user.mapper.SysUserMapper;
import com.aiguibin.platform.core.user.service.impl.SysUserServiceImpl;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;
import java.util.Arrays;
import java.util.List;
import static org.junit.jupiter.api.Assertions.*;
import static org.mockito.Mockito.*;

@ExtendWith(MockitoExtension.class)
class SysUserServiceTest {
    
    @Mock
    private SysUserMapper userMapper;
    
    @InjectMocks
    private SysUserServiceImpl userService;
    
    private SysUser testUser;
    
    @BeforeEach
    void setUp() {
        testUser = new SysUser();
        testUser.setId(1L);
        testUser.setUsername("testuser");
        testUser.setRealName("测试用户");
        testUser.setStatus(1);
    }
    
    @Test
    @DisplayName("根据用户名查询用户")
    void testGetByUsername() {
        when(userMapper.selectByUsername("testuser")).thenReturn(testUser);
        
        SysUser result = userService.getByUsername("testuser");
        
        assertNotNull(result);
        assertEquals("testuser", result.getUsername());
        verify(userMapper, times(1)).selectByUsername("testuser");
    }
    
    @Test
    @DisplayName("获取用户角色列表")
    void testGetUserRoles() {
        List<String> roles = Arrays.asList("admin", "user");
        when(userMapper.selectUserRoles(1L)).thenReturn(roles);
        
        List<String> result = userService.getUserRoles(1L);
        
        assertEquals(2, result.size());
        assertTrue(result.contains("admin"));
        verify(userMapper, times(1)).selectUserRoles(1L);
    }
    
    @Test
    @DisplayName("获取用户权限列表")
    void testGetUserPermissions() {
        List<String> permissions = Arrays.asList("user:add", "user:edit");
        when(userMapper.selectUserPermissions(1L)).thenReturn(permissions);
        
        List<String> result = userService.getUserPermissions(1L);
        
        assertEquals(2, result.size());
        verify(userMapper, times(1)).selectUserPermissions(1L);
    }
    
    @Test
    @DisplayName("锁定用户")
    void testLockUser() {
        doNothing().when(userMapper).lockUser(1L, "测试锁定");
        
        userService.lockUser(1L, "测试锁定");
        
        verify(userMapper, times(1)).lockUser(1L, "测试锁定");
    }
}

package com.aiguibin.platform.core.auth;

import com.aiguibin.platform.core.auth.controller.AuthController;
import com.aiguibin.platform.core.auth.dto.*;
import com.aiguibin.platform.core.auth.service.AuthService;
import com.aiguibin.platform.common.model.Result;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;
import org.springframework.mock.web.MockHttpServletRequest;
import java.util.Arrays;
import java.util.List;
import static org.junit.jupiter.api.Assertions.*;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.ArgumentMatchers.anyString;
import static org.mockito.Mockito.*;

@ExtendWith(MockitoExtension.class)
class AuthControllerTest {
    
    @Mock
    private AuthService authService;
    
    @InjectMocks
    private AuthController authController;
    
    private MockHttpServletRequest request;
    
    @BeforeEach
    void setUp() {
        request = new MockHttpServletRequest();
        request.setRemoteAddr("127.0.0.1");
    }
    
    @Test
    @DisplayName("第一步登录成功")
    void testLoginStep1Success() {
        LoginRequest loginRequest = new LoginRequest();
        loginRequest.setUsername("admin");
        loginRequest.setPassword("admin123");
        
        LoginStep1Response response = new LoginStep1Response();
        response.setTempToken("temp-token-123");
        
        List<UserOrgVO> orgList = Arrays.asList(
            new UserOrgVO("100000", "总公司", 1),
            new UserOrgVO("110000", "北京分公司", 0)
        );
        response.setOrgList(orgList);
        
        when(authService.loginStep1(any(LoginRequest.class), anyString())).thenReturn(response);
        
        Result<LoginStep1Response> result = authController.login(loginRequest, request);
        
        assertEquals(200, result.getCode());
        assertNotNull(result.getData());
        assertEquals("temp-token-123", result.getData().getTempToken());
        assertEquals(2, result.getData().getOrgList().size());
    }
    
    @Test
    @DisplayName("第二步登录-选择机构成功")
    void testSelectOrgSuccess() {
        SelectOrgRequest selectOrgRequest = new SelectOrgRequest();
        selectOrgRequest.setTempToken("temp-token-123");
        selectOrgRequest.setOrgCode("100000");
        
        LoginResponse loginResponse = new LoginResponse();
        loginResponse.setAccessToken("access-token-123");
        loginResponse.setRefreshToken("refresh-token-123");
        
        when(authService.loginStep2(any(SelectOrgRequest.class))).thenReturn(loginResponse);
        
        Result<LoginResponse> result = authController.selectOrg(selectOrgRequest);
        
        assertEquals(200, result.getCode());
        assertNotNull(result.getData().getAccessToken());
    }
}

package com.aiguibin.platform.common.constant;

public class Constants {
    
    public static final String SUCCESS_CODE = "200";
    public static final String ERROR_CODE = "500";
    public static final String UNAUTHORIZED_CODE = "401";
    public static final String FORBIDDEN_CODE = "403";
    
    public static final String DEFAULT_CHARSET = "UTF-8";
    
    public static final Long SUPER_ADMIN_ID = 1L;
    
    public static final Integer DATA_SCOPE_ALL = 1;
    public static final Integer DATA_SCOPE_ORG = 2;
    public static final Integer DATA_SCOPE_DEPT = 3;
    public static final Integer DATA_SCOPE_SELF = 4;
    
    public static final Integer STATUS_ENABLE = 1;
    public static final Integer STATUS_DISABLE = 0;
    
    public static final Integer YES = 1;
    public static final Integer NO = 0;
    
    public static final String TOKEN_HEADER = "Authorization";
    public static final String TOKEN_PREFIX = "Bearer ";
    
    private Constants() {
    }
}

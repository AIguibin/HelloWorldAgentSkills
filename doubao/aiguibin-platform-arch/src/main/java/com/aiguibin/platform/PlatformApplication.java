package com.aiguibin.platform;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;

@SpringBootApplication
public class PlatformApplication {
    
    public static void main(String[] args) {
        SpringApplication.run(PlatformApplication.class, args);
        System.out.println("========================================");
        System.out.println("  AI Guibin Platform 启动成功！");
        System.out.println("  接口文档: http://localhost:8080/api/doc.html");
        System.out.println("========================================");
    }
}

package com.aiguibin.platform.common.result;

import com.aiguibin.platform.common.constant.Constants;
import lombok.Data;

import java.io.Serializable;

@Data
public class Result<T> implements Serializable {
    
    private static final long serialVersionUID = 1L;
    
    private String code;
    private String message;
    private T data;
    private long timestamp;
    
    public Result() {
        this.timestamp = System.currentTimeMillis();
    }
    
    public Result(String code, String message, T data) {
        this.code = code;
        this.message = message;
        this.data = data;
        this.timestamp = System.currentTimeMillis();
    }
    
    public static <T> Result<T> success() {
        return new Result<>(Constants.SUCCESS_CODE, "操作成功", null);
    }
    
    public static <T> Result<T> success(T data) {
        return new Result<>(Constants.SUCCESS_CODE, "操作成功", data);
    }
    
    public static <T> Result<T> success(String message, T data) {
        return new Result<>(Constants.SUCCESS_CODE, message, data);
    }
    
    public static <T> Result<T> error() {
        return new Result<>(Constants.ERROR_CODE, "操作失败", null);
    }
    
    public static <T> Result<T> error(String message) {
        return new Result<>(Constants.ERROR_CODE, message, null);
    }
    
    public static <T> Result<T> error(String code, String message) {
        return new Result<>(code, message, null);
    }
    
    public boolean isSuccess() {
        return Constants.SUCCESS_CODE.equals(this.code);
    }
}

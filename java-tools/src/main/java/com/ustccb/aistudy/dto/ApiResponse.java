package com.ustccb.aistudy.dto;

import lombok.AllArgsConstructor;
import lombok.Data;

import java.util.List;
import java.util.Map;

@Data
@AllArgsConstructor
public class ApiResponse<T> {
    private int code;
    private String message;
    private T data;

    public static <T> ApiResponse<T> ok(T data)             { return new ApiResponse<>(0, "ok", data); }
    public static <T> ApiResponse<T> error(int c, String m) { return new ApiResponse<>(c, m, null); }
}

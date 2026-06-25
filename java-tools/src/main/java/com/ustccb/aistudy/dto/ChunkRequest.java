package com.ustccb.aistudy.dto;

import jakarta.validation.constraints.Min;
import jakarta.validation.constraints.NotBlank;
import lombok.Data;

@Data
public class ChunkRequest {
    @NotBlank
    private String text;
    @Min(50)
    private Integer chunkSize;     // 字符数（中文按 1 字符）
    @Min(0)
    private Integer overlap;        // 重叠字符数
    private String source;          // 来源标识，方便回溯
}

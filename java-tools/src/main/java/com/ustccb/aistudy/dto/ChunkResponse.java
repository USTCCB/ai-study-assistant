package com.ustccb.aistudy.dto;

import lombok.AllArgsConstructor;
import lombok.Data;

import java.util.List;

@Data
@AllArgsConstructor
public class ChunkResponse {
    private int total;
    private long tookMs;
    private List<Chunk> chunks;
}

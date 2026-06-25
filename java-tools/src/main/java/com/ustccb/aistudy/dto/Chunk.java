package com.ustccb.aistudy.dto;

import lombok.AllArgsConstructor;
import lombok.Data;

@Data
@AllArgsConstructor
public class Chunk {
    private int index;
    private String text;
    private int charCount;
    private String source;
}

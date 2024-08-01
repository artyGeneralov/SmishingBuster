package com.proj.phishingBuster.database_dir;

import androidx.annotation.NonNull;

import java.util.HashMap;
import java.util.Map;

public class Screenshot {
    private final int id;

    private final byte[] binaryData;
    private final int messageId;

    public Screenshot(int id,  byte[] binaryData, int messageId) {
        this.id = id;

        this.binaryData = binaryData;
        this.messageId = messageId;
    }

    public int getId() {
        return id;
    }

    public byte[] getBinaryData() {
        return binaryData;
    }

    public int getMessageId() {
        return messageId;
    }

    @NonNull
    @Override
    public String toString() {
        return "ID: " + id + ", Message ID: " + messageId;
    }

    public Map<String, String> getScreenshotAsMap(){
        Map<String, String> map = new HashMap<>();
        map.put("ID", String.valueOf(id));
        map.put("Message ID", String.valueOf(messageId));
        return map;
    }
}
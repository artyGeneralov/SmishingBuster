package com.proj.phishingBuster.database_dir;

import com.fasterxml.jackson.databind.ObjectMapper;
import org.json.JSONArray;
import org.json.JSONException;
import org.json.JSONObject;

import java.util.HashMap;
import java.util.Iterator;
import java.util.Map;
import java.util.logging.Level;
import java.util.logging.Logger;

public class JSONMessageParser {

    private static final ObjectMapper objectMapper = new ObjectMapper();
    private static final Logger logger = Logger.getLogger(JSONMessageParser.class.getName());

    public static Map<String, Object> parseStringToObjectMap(String jsonAsString) {
        try {
            JSONObject jsonObject = new JSONObject(jsonAsString);
            return toMap(jsonObject);
        } catch (JSONException e) {
            e.printStackTrace();
            return null;
        }
    }

    public static Map<String, Integer> parseStringToIntMap(String jsonAsString) {
        Map<String, Object> objectMap = parseStringToObjectMap(jsonAsString);
        Map<String, Integer> intMap = new HashMap<>();
        if (objectMap != null) {
            for (String key : objectMap.keySet()) {
                Object value = objectMap.get(key);
                if (value instanceof Double) {
                    intMap.put(key, (int) Math.round((Double) value));
                } else if (value instanceof Integer) {
                    intMap.put(key, (Integer) value);
                } else {
                    throw new IllegalArgumentException("Unsupported value type: " + value.getClass().getName());
                }
            }
        }
        return intMap;
    }

    public static Map<String, String> parseStringToStringMap(String jsonAsString) {
        Map<String, Object> objectMap = JSONMessageParser.parseStringToObjectMap(jsonAsString);
        Map<String, String> strMap = new HashMap<>();
        if (objectMap != null) {
            for (String key : objectMap.keySet()) {
                strMap.put(key, (String) objectMap.get(key));
            }
        }
        return strMap;
    }

    public static String convertMapToString(Map<String, ?> map) {
        try {
            return objectMapper.writeValueAsString(map);
        } catch (Exception e) {
            logger.log(Level.SEVERE, "Failed to convert Map to JSON String: " + e.getMessage(), e);
            return null;
        }
    }

    private static Map<String, Object> toMap(JSONObject jsonObject) throws JSONException {
        Map<String, Object> map = new HashMap<>();
        Iterator<String> keys = jsonObject.keys();

        while (keys.hasNext()) {
            String key = keys.next();
            Object value = jsonObject.get(key);

            if (value instanceof JSONArray) {
                value = toList((JSONArray) value);
            } else if (value instanceof JSONObject) {
                value = toMap((JSONObject) value);
            }

            map.put(key, value);
        }

        return map;
    }

    private static Object toList(JSONArray array) throws JSONException {
        java.util.List<Object> list = new java.util.ArrayList<>();
        for (int i = 0; i < array.length(); i++) {
            Object value = array.get(i);
            if (value instanceof JSONArray) {
                value = toList((JSONArray) value);
            } else if (value instanceof JSONObject) {
                value = toMap((JSONObject) value);
            }
            list.add(value);
        }
        return list;
    }
}

package com.proj.phishingBuster.database_dir;

import android.util.Log;
import androidx.annotation.NonNull;

import java.util.Map;

public class Message {
    private final int id;
    private final String sender;
    private final String msg;
    private final String date;
    private int score;
    private String report;
    private String links;
    private String screenshots;
    private String vt_results;
    private String google_results;

    // Constructor with ID
    public Message(int id, String sender, String msg, String date) {
        this.id = id;
        this.sender = sender;
        this.msg = msg;
        this.date = date;
    }


    public int getId() {
        return id;
    }


    public String getSender() {
        return sender;
    }

    public String getMsg() {
        Log.d("msgBod", msg);
        return msg;
    }

    public String getDate() {
        return date;
    }

    public void setReport(String report) {
        this.report = report;
    }

    public String getReport() {
        return report;
    }

    public String getLinks(){ return links; }
    public String getScreenshots(){ return screenshots; }
    public void setLinks(String links){this.links = links;}
    public void setScreenshots(String screenshots){ this.screenshots = screenshots; }

    @NonNull
    @Override
    public String toString() {
        return "ID: " + id + ", Sender: " + sender +
                ", Message: " + msg + ", Date: " + date + ", Score: " + score +
                ", Report: " + report; // Include report in toString
    }

    public void setScore(int score) {
        this.score = score;
    }

    public int getScore() {
        return score;
    }

    public Map<String, Integer> getReportAsMap(){
        return JSONMessageParser.parseStringToIntMap(report);
    }

    public Map<String, String> getLinksAsMap(){
        return JSONMessageParser.parseStringToStringMap(links);
    }

    public Map<String, String> getScreenshotsAsMap(){
        return JSONMessageParser.parseStringToStringMap(screenshots);
    }

    public void setVT(String vt){
        this.vt_results = vt;
    }

    public void setGoogle(String google){
        this.google_results = google;
    }

    public Map<String, Integer> getVTAsMap(){
        return JSONMessageParser.parseStringToIntMap(vt_results);
    }

    public Map<String, Integer> getGoogleAsMap(){
        return JSONMessageParser.parseStringToIntMap(google_results);
    }
}
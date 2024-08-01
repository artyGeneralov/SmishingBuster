package com.proj.phishingBuster.database_dir;

import android.annotation.SuppressLint;
import android.content.ContentValues;
import android.content.Context;
import android.database.Cursor;
import android.database.sqlite.SQLiteDatabase;
import android.database.sqlite.SQLiteOpenHelper;
import android.util.Log;


import androidx.annotation.Nullable;

import java.util.ArrayList;
import java.util.List;

public class DbManager extends SQLiteOpenHelper {

    private static final String TAG = "MyDBHelper";
    // Table my_sms
    private static final String DATABASE_NAME = "Context.db";
    private static final int DATA_VERSION = 2;

    private static final String TABLE_MESSAGES = "my_sms";

    private static final String COLUMN_MESSAGE_ID = "id";
    private static final String COLUMN_SENDER = "sender";
    private static final String COLUMN_CONTENT = "content";
    private static final String COLUMN_TIME = "time";
    private static final String COLUMN_SCORE = "score";
    private static final String COLUMN_REPORT = "report";

    private static final String COLUMN_LINKS = "links";
    private static final String COLUMN_SCREENSHOTS_NAMES = "screenshots";
    private static final String COLUMN_VT_RESULTS = "Virustotal_results";
    private static final String COLUMN_GOOGLE_SAFE_RESULTS = "Google_SafeBrowsing_results";

    // Table screenshots:
    private static final String TABLE_SCREENSHOTS = "screenshot_table";
    private static final String COLUMN_SCREENSHOT_ID = "screenshot_id";
    private static final String COLUMN_SCREENSHOT = "screenshot_binary";
    private static final String COLUMN_SCREENSHOT_MESSAGE_ID = "message_id";

    private static final String CREATE_TABLE_MESSAGES =
            "CREATE TABLE " + TABLE_MESSAGES + " ("
                    + COLUMN_MESSAGE_ID + " INTEGER PRIMARY KEY AUTOINCREMENT, "
                    + COLUMN_SENDER + " TEXT, "
                    + COLUMN_CONTENT + " TEXT, "
                    + COLUMN_TIME + " TEXT, "
                    + COLUMN_SCORE + " FLOAT, "
                    + COLUMN_REPORT + " TEXT, "
                    + COLUMN_LINKS + " TEXT, "
                    + COLUMN_VT_RESULTS + " TEXT, "
                    + COLUMN_GOOGLE_SAFE_RESULTS + " TEXT, "
                    + COLUMN_SCREENSHOTS_NAMES + " TEXT);";

    private static final String CREATE_TABLE_SCREENSHOTS =
            "CREATE TABLE " + TABLE_SCREENSHOTS + " (" +
                    COLUMN_SCREENSHOT_ID + " INTEGER PRIMARY KEY AUTOINCREMENT, " +
                    COLUMN_SCREENSHOT + " BLOB, " +
                    COLUMN_SCREENSHOT_MESSAGE_ID + " INTEGER, " +
                    "FOREIGN KEY(" + COLUMN_SCREENSHOT_MESSAGE_ID + ") REFERENCES " + TABLE_MESSAGES + "(" + COLUMN_MESSAGE_ID + "));";


    private static DbManager sInstance;

    private DbManager(@Nullable Context context) {
        super(context, DATABASE_NAME, null, DATA_VERSION);
    }

    public static DbManager getInstance(Context context) {
        if (sInstance == null) {
            sInstance = new DbManager(context.getApplicationContext());
        }
        return sInstance;
    }

    @Override
    public void onCreate(SQLiteDatabase db) {
        db.execSQL(CREATE_TABLE_MESSAGES);
        db.execSQL(CREATE_TABLE_SCREENSHOTS);
    }

    @Override
    public void onUpgrade(SQLiteDatabase db, int oldVersion, int newVersion) {
        db.execSQL("DROP TABLE IF EXISTS " + TABLE_MESSAGES);
        onCreate(db);
    }
    public void flushTableDb(){
        SQLiteDatabase db = this.getReadableDatabase();
        db.execSQL("DELETE FROM " + TABLE_MESSAGES);
        closeDB(db);
    }
    public Message addMessage(String sender, String content, String time, int score, String report, String links, String screenshots, String vtRes, String googleRes) {
        SQLiteDatabase db = this.getWritableDatabase();
        ContentValues values = new ContentValues();
        values.put(COLUMN_SENDER, sender);
        values.put(COLUMN_CONTENT, content);
        values.put(COLUMN_TIME, time);
        values.put(COLUMN_SCORE, score);
        values.put(COLUMN_REPORT, report);
        values.put(COLUMN_LINKS, links);
        values.put(COLUMN_SCREENSHOTS_NAMES, screenshots);
        values.put(COLUMN_VT_RESULTS, vtRes);
        values.put(COLUMN_GOOGLE_SAFE_RESULTS, googleRes);
        long id = db.insert(TABLE_MESSAGES, null, values);
        closeDB(db);

        // Create and return the Message object with the newly generated ID
        Message message = new Message((int) id, sender, content, time);
        message.setScore(score);
        message.setReport(report);
        message.setVT(vtRes);
        message.setGoogle(googleRes);
        return message;
    }

    public Screenshot addScreenshotById(int messageId, byte[] binaryData){
        SQLiteDatabase db = this.getWritableDatabase();
        ContentValues values = new ContentValues();
        values.put(COLUMN_SCREENSHOT, binaryData);
        values.put(COLUMN_SCREENSHOT_MESSAGE_ID, messageId);
        long id = db.insert(TABLE_SCREENSHOTS, null, values);
        closeDB(db);
        return new Screenshot((int) id, binaryData, messageId);
    }

    public List<String> getAllContacts() {
        List<String> contactsList = new ArrayList<>();
        SQLiteDatabase db = this.getReadableDatabase();
        String query = "SELECT * FROM " + TABLE_MESSAGES;
        Cursor cursor = db.rawQuery(query, null);

        if (cursor.moveToFirst()) {
            do {
                int idIndex = cursor.getColumnIndex(COLUMN_MESSAGE_ID);
                int senderIndex = cursor.getColumnIndex(COLUMN_SENDER);
                int msgIndex = cursor.getColumnIndex(COLUMN_CONTENT);
                int dateIndex = cursor.getColumnIndex(COLUMN_TIME);
                int scoreIndex = cursor.getColumnIndex(COLUMN_SCORE);
                if (idIndex != -1 && senderIndex != -1 && msgIndex != -1 && dateIndex != -1) {
                    int id = cursor.getInt(idIndex);
                    String fullSender = cursor.getString(senderIndex);
                    String fullMsg = cursor.getString(msgIndex);
                    String formattedDate = cursor.getString(dateIndex);
                    Message message = new Message(id, fullSender, fullMsg, formattedDate);
                    message.setScore(cursor.getInt(scoreIndex));
                    contactsList.add(message.toString());
                }
            } while (cursor.moveToNext());
        }
        cursor.close();
        closeDB(db);
        return contactsList;
    }

    public List<Message> getAllMessagesRaw() {
        List<Message> messagesList = new ArrayList<>();
        SQLiteDatabase db = this.getReadableDatabase();
        String query = "SELECT * FROM " + TABLE_MESSAGES;
        Cursor cursor = db.rawQuery(query, null);

        if (cursor.moveToFirst()) {
            do {
                int idIndex = cursor.getColumnIndex(COLUMN_MESSAGE_ID);
                int senderIndex = cursor.getColumnIndex(COLUMN_SENDER);
                int msgIndex = cursor.getColumnIndex(COLUMN_CONTENT);
                int dateIndex = cursor.getColumnIndex(COLUMN_TIME);
                int scoreIndex = cursor.getColumnIndex(COLUMN_SCORE);
                int reportIndex = cursor.getColumnIndex(COLUMN_REPORT);
                int linksIndex = cursor.getColumnIndex(COLUMN_LINKS);
                int screenshotsIndex = cursor.getColumnIndex(COLUMN_SCREENSHOTS_NAMES);
                if (idIndex != -1 && senderIndex != -1 && msgIndex != -1 && dateIndex != -1) {
                    int id = cursor.getInt(idIndex);
                    String fullSender = cursor.getString(senderIndex);
                    String fullMsg = cursor.getString(msgIndex);
                    String formattedDate = cursor.getString(dateIndex);
                    Message message = new Message(id, fullSender, fullMsg, formattedDate);
                    message.setScore(cursor.getInt(scoreIndex));
                    message.setReport(cursor.getString(reportIndex));
                    message.setLinks(cursor.getString(linksIndex));
                    message.setScreenshots(cursor.getString(screenshotsIndex));
                    messagesList.add(message);
                }
            } while (cursor.moveToNext());
        }
        cursor.close();
        //closeDB(db);

        return messagesList;
    }

    public Message getMessageById(int id) {
        SQLiteDatabase db = this.getReadableDatabase();
        String query = "SELECT * FROM " + TABLE_MESSAGES + " WHERE " + COLUMN_MESSAGE_ID + " = ?";
        Cursor cursor = db.rawQuery(query, new String[]{String.valueOf(id)});

        if (cursor != null && cursor.moveToFirst()) {
            int senderIndex = cursor.getColumnIndex(COLUMN_SENDER);
            int contentIndex = cursor.getColumnIndex(COLUMN_CONTENT);
            int timeIndex = cursor.getColumnIndex(COLUMN_TIME);
            int scoreIndex = cursor.getColumnIndex(COLUMN_SCORE);
            int reportIndex = cursor.getColumnIndex(COLUMN_REPORT);
            int linksIndex = cursor.getColumnIndex(COLUMN_LINKS);
            int screenshotsIndex = cursor.getColumnIndex(COLUMN_SCREENSHOTS_NAMES);
            int vtIndex = cursor.getColumnIndex(COLUMN_VT_RESULTS);
            int googleIndex = cursor.getColumnIndex(COLUMN_GOOGLE_SAFE_RESULTS);

            if (senderIndex == -1 || contentIndex == -1 || timeIndex == -1 || scoreIndex == -1 || reportIndex == -1) {
                // Close the cursor and database if any column is missing
                cursor.close();
                closeDB(db);
                throw new IllegalStateException("Column missing in the database schema.");
            }

            String sender = cursor.getString(senderIndex);
            String content = cursor.getString(contentIndex);
            String time = cursor.getString(timeIndex);
            int score = cursor.getInt(scoreIndex);
            String report = cursor.getString(reportIndex);
            String vt = cursor.getString(vtIndex);
            String google = cursor.getString(googleIndex);

            Message message = new Message(id, sender, content, time);
            message.setScore(score);
            message.setReport(report); // Set the report
            message.setLinks(cursor.getString(linksIndex));
            message.setScreenshots(cursor.getString(screenshotsIndex));
            message.setVT(vt);
            message.setGoogle(google);

            cursor.close();
            closeDB(db);
            Log.d(TAG, message.toString());
            return message;
        }

        if (cursor != null) {
            cursor.close();
        }
        closeDB(db);
        return null;
    }

    public void updateMessageGoogle(int id, String google){
        SQLiteDatabase db = this.getWritableDatabase();
        ContentValues values = new ContentValues();
        values.put(COLUMN_GOOGLE_SAFE_RESULTS, google);
        int rowsAffected = db.update(TABLE_MESSAGES, values, COLUMN_MESSAGE_ID + " = ?", new String[]{String.valueOf(id)});
        closeDB(db);

        if(rowsAffected == 0){
            throw new IllegalStateException("No rows updated, message ID may not exist.");
        }
    }

    public void updateMessageVT(int id, String vt){
        SQLiteDatabase db = this.getWritableDatabase();
        ContentValues values = new ContentValues();
        values.put(COLUMN_VT_RESULTS, vt);
        int rowsAffected = db.update(TABLE_MESSAGES, values, COLUMN_MESSAGE_ID + " = ?", new String[]{String.valueOf(id)});
        closeDB(db);

        if(rowsAffected == 0){
            throw new IllegalStateException("No rows updated, message ID may not exist.");
        }
    }

    public void updateMessageScore(int id, double newScore) {
        SQLiteDatabase db = this.getWritableDatabase();
        ContentValues values = new ContentValues();
        values.put(COLUMN_SCORE, newScore);

        int rowsAffected = db.update(TABLE_MESSAGES, values, COLUMN_MESSAGE_ID + " = ?", new String[]{String.valueOf(id)});
        closeDB(db);

        if (rowsAffected == 0) {
            throw new IllegalStateException("No rows updated, message ID may not exist.");
        }
    }

    public void updateMessageReport(int id, String newReport) {
        SQLiteDatabase db = this.getWritableDatabase();
        ContentValues values = new ContentValues();
        values.put(COLUMN_REPORT, newReport);

        int rowsAffected = db.update(TABLE_MESSAGES, values, COLUMN_MESSAGE_ID + " = ?", new String[]{String.valueOf(id)});
        closeDB(db);

        if (rowsAffected == 0) {
            throw new IllegalStateException("No rows updated, message ID may not exist.");
        }
    }

    public void updateMessageLinksAndScreenshots(int id, String links, String screenshots){
        SQLiteDatabase db = this.getWritableDatabase();
        ContentValues values = new ContentValues();
        values.put(COLUMN_LINKS, links);
        values.put(COLUMN_SCREENSHOTS_NAMES, screenshots);

        int rowsAffected = db.update(TABLE_MESSAGES, values, COLUMN_MESSAGE_ID + " = ?", new String[]{String.valueOf(id)});
        closeDB(db);

        if (rowsAffected == 0) {
            throw new IllegalStateException("No rows updated, message ID may not exist.");
        }
    }


    public Screenshot addScreenshot(byte[] byteArray, int messageId){
        SQLiteDatabase db = this.getWritableDatabase();
        ContentValues values = new ContentValues();
        values.put(COLUMN_SCREENSHOT, byteArray);
        values.put(COLUMN_SCREENSHOT_MESSAGE_ID, messageId);
        long id = db.insert(TABLE_SCREENSHOTS, null, values);
        closeDB(db);

        return new Screenshot((int) id, byteArray, messageId);
    }
    public List<Screenshot> getScreenshotsByMessageId(int messageId) {
        List<Screenshot> screenshots = new ArrayList<>();
        SQLiteDatabase db = this.getReadableDatabase();
        Cursor cursor = db.query(TABLE_SCREENSHOTS,
                null,
                COLUMN_SCREENSHOT_MESSAGE_ID + "=?",
                new String[]{String.valueOf(messageId)},
                null,
                null,
                null);

        if (cursor != null) {
            while (cursor.moveToNext()) {
                @SuppressLint("Range") Screenshot screenshot = new Screenshot(
                        cursor.getInt(cursor.getColumnIndex(COLUMN_SCREENSHOT_ID)),
                        cursor.getBlob(cursor.getColumnIndex(COLUMN_SCREENSHOT)),
                        cursor.getInt(cursor.getColumnIndex(COLUMN_SCREENSHOT_MESSAGE_ID))
                );
                screenshots.add(screenshot);
            }
            cursor.close();
        }

        return screenshots;
    }

    public void deleteMessageById(int message_id) {
        SQLiteDatabase db = this.getWritableDatabase();
        db.delete(TABLE_MESSAGES, COLUMN_MESSAGE_ID + " = ?", new String[]{String.valueOf(message_id)});
        closeDB(db);
    }

    private void closeDB(SQLiteDatabase db){
        db.close();
    }
}

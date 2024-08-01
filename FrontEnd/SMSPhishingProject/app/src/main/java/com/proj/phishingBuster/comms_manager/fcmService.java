package com.proj.phishingBuster.comms_manager;

import com.fasterxml.jackson.databind.ObjectMapper;
import com.google.firebase.messaging.FirebaseMessagingService;
import com.google.firebase.messaging.RemoteMessage;
import com.proj.phishingBuster.MainActivity;
import com.proj.phishingBuster.R;
import com.proj.phishingBuster.database_dir.DbManager;
import com.proj.phishingBuster.database_dir.JSONMessageParser;

import android.app.NotificationChannel;
import android.app.NotificationManager;
import android.app.PendingIntent;
import android.content.Context;
import android.content.Intent;
import android.content.SharedPreferences;
import android.graphics.Bitmap;
import android.graphics.BitmapFactory;
import android.graphics.Color;
import android.graphics.drawable.Drawable;
import android.media.RingtoneManager;
import android.net.Uri;
import android.os.Build;
import android.util.Log;

import android.os.Handler;
import android.os.Looper;

import androidx.annotation.NonNull;
import androidx.core.app.NotificationCompat;
import androidx.core.content.ContextCompat;
import androidx.localbroadcastmanager.content.LocalBroadcastManager;

import com.proj.phishingBuster.database_dir.Message;
import com.proj.phishingBuster.database_dir.Screenshot;
import com.squareup.picasso.Callback;
import com.squareup.picasso.MemoryPolicy;
import com.squareup.picasso.NetworkPolicy;
import com.squareup.picasso.Picasso;
import com.squareup.picasso.Target;

import java.io.ByteArrayOutputStream;
import java.util.ArrayList;
import java.util.List;
import java.util.Map;

public class fcmService extends FirebaseMessagingService {
    private static final String TAG = "fcmService";
    public static final String ACTION_MESSAGE_BROADCAST = "com.example.yourapp.MESSAGE_BROADCAST";
    public static final String EXTRA_MESSAGE = "message";
    private static final String screenshot_url = "/screenshots";

    public void onMessageReceived(@NonNull RemoteMessage remoteMessage) {
        if (remoteMessage.getData().size() > 0) {
            Log.d("fcm", "Message data payload: " + remoteMessage.getData());

            String message = remoteMessage.getData().get("reply");
            updateDB(message);
            // Send broadcast
            Intent intent = new Intent(ACTION_MESSAGE_BROADCAST);
            intent.putExtra(EXTRA_MESSAGE, message);
            LocalBroadcastManager.getInstance(this).sendBroadcast(intent);
        }
    }


    public void onNewToken(@NonNull String token) {
        Log.d("newToken", "New token has been generated " + token);
        saveTokenToPreferences(token);
    }

    private void saveTokenToPreferences(String token) {
        SharedPreferences preferences = getSharedPreferences("app_prefs", Context.MODE_PRIVATE);
        SharedPreferences.Editor editor = preferences.edit();
        editor.putString("fcm_token", token);
        editor.apply();
    }

    private void updateDB(String message) {
        DbManager db = DbManager.getInstance(this);

        try {
            Map<String, Object> outerJson = JSONMessageParser.parseStringToObjectMap(message);
            if (outerJson == null) {
                Log.e(TAG, "Failed to parse outer JSON");
                return;
            }
            Log.d(TAG, "Parsed outer JSON successfully: " + outerJson);

            Object dataObj = outerJson.get("data");
            if (!(dataObj instanceof Map)) {
                Log.e(TAG, "'data' field is missing or not a JSON object");
                return;
            }
            Map<String, Object> dataJson = (Map<String, Object>) dataObj;
            Log.d(TAG, "Extracted 'data' JSON successfully: " + dataJson);

            Object messageIdObj = dataJson.get("localMessageID");
            if (!(messageIdObj instanceof Number)) {
                Log.e(TAG, "'localMessageID' is missing or not a number");
                return;
            }
            Integer messageID = ((Number) messageIdObj).intValue();
            Log.d(TAG, "Extracted 'localMessageID' successfully: " + messageID);

            Object analyzedMessageObj = dataJson.get("analyzedMessage");
            if (!(analyzedMessageObj instanceof String)) {
                Log.e(TAG, "'analyzedMessage' is missing or not a string");
                return;
            }
            String analyzedMessage = (String) analyzedMessageObj;
            Log.d(TAG, "Extracted 'analyzedMessage' successfully: " + analyzedMessage);

            Map<String, Object> analyzedMessageJson = JSONMessageParser.parseStringToObjectMap(analyzedMessage);
            if (analyzedMessageJson == null) {
                Log.e(TAG, "Failed to parse 'analyzedMessage' JSON");
                return;
            }
            Log.d(TAG, "Parsed 'analyzedMessage' JSON successfully: " + analyzedMessageJson);

            Number statisticScoreNumber = (Number) analyzedMessageJson.get("statistic_score");
            Float statisticScore = statisticScoreNumber != null ? statisticScoreNumber.floatValue() : null;
            String nnPrediction = (String) analyzedMessageJson.get("nn_prediction");
            String lmPrediction = (String) analyzedMessageJson.get("lm_prediction");
            String report = (String) analyzedMessageJson.get("features_report");
            Number finalScoreNumber = (Number) analyzedMessageJson.get("final_score");
            Double finalScore = finalScoreNumber != null ? finalScoreNumber.doubleValue() : null;
            String vt = (String) analyzedMessageJson.get("virus_total_scores");
            String goog = (String) analyzedMessageJson.get("google_safe_scores");

            if (finalScore == null) {
                Log.e(TAG, "'final_score' is missing or not a number");
                return;
            }

            db.updateMessageScore(messageID, finalScore);
            db.updateMessageReport(messageID, report);


            ObjectMapper objectMapper = new ObjectMapper();

            Object linksObj = dataJson.get("links");
            Object screenshotsObj = dataJson.get("screenshots");
            if (!(linksObj instanceof Map) || !(screenshotsObj instanceof Map)) {
                Log.e(TAG, "'links' or 'screenshots' is missing or not a JSON object");
                return;
            }
            Map<String, String> links = (Map<String, String>) linksObj;
            Map<String, String> screenshots = (Map<String, String>) screenshotsObj;
            Log.d(TAG, "Extracted 'links' and 'screenshots' successfully: " + links + ", " + screenshots);

            String linksJson = objectMapper.writeValueAsString(links);
            String screenshotsJson = objectMapper.writeValueAsString(screenshots);

            db.updateMessageLinksAndScreenshots(messageID, linksJson, screenshotsJson);

            String baseUrl = getString(R.string.mainURL);

            for (Map.Entry<String, String> entry : screenshots.entrySet()) {
                String screenshotName = entry.getValue();
                String screenshotUrl = baseUrl + screenshot_url + "/" + screenshotName;
                fetchAndSaveScreenshot(screenshotUrl, messageID);
            }

            Log.d(TAG, "virusTotal : " + vt);
            db.updateMessageVT(messageID, vt);


            //TODO: uncomment once google safe browsing is implemented
//            Object googleSafeObject = dataJson.get("google_safe_scores");
//            if (!(googleSafeObject instanceof String)) {
//                Log.e(TAG, "'virus_total_scores' is missing or not a string");
//                return;
//            }
//            db.updateMessageGoogle(messageID, goog);
            Message msg = db.getMessageById(messageID);
            sendNotification(messageID, msg.getMsg(), (Double)finalScoreNumber);
            Log.d(TAG, "Database updated successfully for messageID: " + messageID);

        } catch (Exception e) {
            Log.e(TAG, "Error updating database: " + e.getMessage(), e);
        }
    }

    private List<Target> targetList = new ArrayList<>();

    private void fetchAndSaveScreenshot(String url, int messageId) {
        Handler mainHandler = new Handler(Looper.getMainLooper());
        Log.d(TAG, "Fetching URL: " + url);

        try {
            Picasso.get();
        } catch (IllegalStateException e) {
            Picasso picasso = new Picasso.Builder(this)
                    .loggingEnabled(true)
                    .indicatorsEnabled(true)
                    .build();
            Picasso.setSingletonInstance(picasso);
        }

        Target target = new Target() {
            @Override
            public void onBitmapLoaded(Bitmap bitmap, Picasso.LoadedFrom from) {
                Log.d(TAG, "BITMAP LOADED");
                ByteArrayOutputStream stream = new ByteArrayOutputStream();
                bitmap.compress(Bitmap.CompressFormat.PNG, 100, stream);
                byte[] byteArray = stream.toByteArray();
                Log.d(TAG, "Byte array size: " + byteArray.length);

                DbManager db = DbManager.getInstance(getApplicationContext());
                Screenshot result = db.addScreenshot(byteArray, messageId);
                if (result.getBinaryData().length > 1) {
                    Log.d(TAG, "Database updated successfully for messageID: " + messageId);
                } else {
                    Log.e(TAG, "Database update failed for messageID: " + messageId);
                }
                db.close();
            }

            @Override
            public void onBitmapFailed(Exception e, Drawable errorDrawable) {
                Log.e(TAG, "Failed to load screenshot", e);
            }

            @Override
            public void onPrepareLoad(Drawable placeHolderDrawable) {
                Log.d(TAG, "Preparing to load bitmap");
            }
        };

        // Add the target to the list to prevent it from being garbage collected
        targetList.add(target);

        mainHandler.post(() -> Picasso.get()
                .load(url)
                //.networkPolicy(NetworkPolicy.NO_CACHE)
                //.memoryPolicy(MemoryPolicy.NO_CACHE)
                .into(target));

        Picasso.get()
                .load(url)
                .fetch(new Callback() {
                    @Override
                    public void onSuccess() {
                        Log.d(TAG, "Image fetch success");
                    }

                    @Override
                    public void onError(Exception e) {
                        Log.e(TAG, "Image fetch error", e);
                    }
                });
    }

    private void sendNotification(int messageID, String message, double score) {
        NotificationManager notificationManager = (NotificationManager) getSystemService(Context.NOTIFICATION_SERVICE);
        String channelId = "your_channel_id";
        String channelName = "Your Channel Name";

        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
            NotificationChannel channel = new NotificationChannel(channelId, channelName, NotificationManager.IMPORTANCE_DEFAULT);
            notificationManager.createNotificationChannel(channel);
        }

        Intent intent = new Intent(this, MainActivity.class);
        intent.addFlags(Intent.FLAG_ACTIVITY_CLEAR_TOP);
        PendingIntent pendingIntent = PendingIntent.getActivity(this, 0, intent, PendingIntent.FLAG_ONE_SHOT | PendingIntent.FLAG_IMMUTABLE);

        Uri defaultSoundUri = RingtoneManager.getDefaultUri(RingtoneManager.TYPE_NOTIFICATION);

        int icon;
        int backgroundColor;
        int threshold_high = 70;
        int threshold_low = 40;

        if (score > threshold_high) {
            icon = R.drawable.high_risk_icon;
            backgroundColor = R.color.score_high_bg;
        } else if (score > threshold_low) {
            icon = R.drawable.medium_risk_icon;
            backgroundColor = R.color.score_medium_bg;
        } else {
            icon = R.drawable.low_risk_icon;
            backgroundColor = R.color.score_low_bg;
        }



        int maxMessageLen = 20;
        String notificationMessage = message.length() > maxMessageLen ? message.substring(0, maxMessageLen) + "..." : message;

        Bitmap iconBitmap = BitmapFactory.decodeResource(getResources(), icon);
        Bitmap scaledIconBitmap = Bitmap.createScaledBitmap(iconBitmap, 128, 128, false);

        NotificationCompat.Builder notificationBuilder = new NotificationCompat.Builder(this, channelId)
                .setSmallIcon(icon)
                .setContentTitle("Message:")
                .setContentText(notificationMessage)
                .setAutoCancel(true)
                .setSound(defaultSoundUri)
                .setContentIntent(pendingIntent)
                .setColor(ContextCompat.getColor(this, backgroundColor))
                .setLargeIcon(scaledIconBitmap);

        notificationManager.notify(messageID, notificationBuilder.build());
    }
}

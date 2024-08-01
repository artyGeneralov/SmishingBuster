package com.proj.phishingBuster.comms_manager;
import android.content.Context;
import android.content.SharedPreferences;
import android.util.Log;

import androidx.annotation.NonNull;

import com.proj.phishingBuster.R;
import com.proj.phishingBuster.database_dir.Message;

import okhttp3.Call;
import okhttp3.Callback;
import okhttp3.MediaType;
import okhttp3.OkHttpClient;
import okhttp3.Request;
import okhttp3.RequestBody;
import okhttp3.Response;
import org.json.JSONException;
import org.json.JSONObject;
import java.io.IOException;
import java.util.concurrent.TimeUnit;

public class serverComms {
    private static final String TAG = "serverComms";
    private static final String server_url ="/analysis";
    public static void sendMessageForAnalysis(Context context, @NonNull Message message) {
        SharedPreferences preferences = context.getSharedPreferences("app_prefs", Context.MODE_PRIVATE);
        String token = preferences.getString("fcm_token", null);
        int messageId = message.getId();
        StringBuilder messageBody = new StringBuilder();
        StringBuilder messageSender = new StringBuilder();
        messageBody.append(message.getMsg());
        messageSender.append(message.getSender());

        if (token != null) {
            JSONObject payload = new JSONObject();
            try {
                payload.put("registration_id", token);
                payload.put("localMessageID", messageId);
                payload.put("sender", messageSender);
                payload.put("message", messageBody);
            } catch (JSONException e) {
                e.printStackTrace();
            }
            sendMessageRequestToServer(context, payload);
        } else {
            Log.e(TAG, "FCM token is null");
        }
    }


    private static void sendMessageRequestToServer(Context context, JSONObject payload) {
        OkHttpClient client = new OkHttpClient.Builder()
                .connectTimeout(30, TimeUnit.SECONDS)
                .writeTimeout(30, TimeUnit.SECONDS)
                .readTimeout(30, TimeUnit.SECONDS)
                .build();
        String fullURL = context.getString(R.string.mainURL);
        RequestBody body = RequestBody.create(payload.toString(), MediaType.parse("application/json"));
        Request request = new Request.Builder()
                .url(fullURL+ server_url)
                .post(body)
                .build();

        client.newCall(request).enqueue(new Callback() {
            @Override
            public void onFailure(@NonNull Call call, @NonNull IOException e) {
                Log.e(TAG, "Failed to send request", e);
            }

            @Override
            public void onResponse(@NonNull Call call, @NonNull Response response) throws IOException {
                if (response.isSuccessful()) {
                    Log.d(TAG, "Request sent successfully");
                } else {
                    Log.e(TAG, "Failed to send request: " + response.message());
                }
            }
        });
    }
}

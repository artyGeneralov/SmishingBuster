package com.proj.phishingBuster.sms_interceptor;


import android.app.NotificationChannel;
import android.app.NotificationManager;
import android.content.BroadcastReceiver;
import android.content.Context;
import android.content.Intent;
import android.os.Build;
import com.proj.phishingBuster.comms_manager.serverComms;



import android.os.Bundle;
import android.telephony.SmsMessage;
import android.util.Log;

import androidx.core.app.NotificationCompat;
import androidx.localbroadcastmanager.content.LocalBroadcastManager;

import com.proj.phishingBuster.R;
import com.proj.phishingBuster.database_dir.Message;
import com.proj.phishingBuster.database_dir.DbManager;

import java.text.SimpleDateFormat;
import java.util.Calendar;
import java.util.Locale;

/*
* SMSBroadcastReceiver - A BroadcastReceiver that receives an intent on SMS_RECEIVED:
* android.provider.Telephony.SMS_RECEIVED
* Adds message to local SQLite database.
* Passes SMS message to receiver that handles client-server communication.
* */
public class SMSBroadcastReceiver extends BroadcastReceiver {

    @Override
    public void onReceive(Context context, Intent intent) {


        DbManager dbHelper = DbManager.getInstance(context);

        Bundle bundle = intent.getExtras();

        if(bundle != null){
            Object[] pdus = (Object[]) bundle.get("pdus");
            if(pdus != null){
                String sender = null;
                StringBuilder fullMsg = new StringBuilder();
                StringBuilder fullSender = new StringBuilder();
                for(Object pdu : pdus){
                    SmsMessage sms = SmsMessage.createFromPdu((byte[]) pdu);
                    if(sender == null) {
                        sender = sms.getOriginatingAddress();
                        fullSender.append(sender);
                    }
                    String content = sms.getMessageBody();
                    fullMsg.append(content);

                }
                Log.d("smsLog", "fullMsg: " + fullMsg + " fullSender: " + fullSender);

                Calendar calendar = Calendar.getInstance();
                SimpleDateFormat dateFormat = new SimpleDateFormat("dd/MM/yyyy HH:mm:ss", Locale.getDefault());
                String formattedDate = dateFormat.format(calendar.getTime());

                int score = -1;
                String report = "";
                String links = "";
                String screenshots = "";
                String vt = "";
                String google = "";
                Message message = dbHelper.addMessage(fullSender.toString(), fullMsg.toString(), formattedDate, score, report, links, screenshots, vt, google);

                Intent newMsgIntent = new Intent("SMS_UPDATE_ACTION");
                LocalBroadcastManager.getInstance(context).sendBroadcast(newMsgIntent);

                serverComms.sendMessageForAnalysis(context, message);

            }
        }
    }


    private void createNotification(Context context, String content) {
        NotificationManager notificationManager = (NotificationManager) context.getSystemService(Context.NOTIFICATION_SERVICE);

        // Create a notification channel for API 26+
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
            NotificationChannel channel = new NotificationChannel("CHANNEL_ID", "Channel Name", NotificationManager.IMPORTANCE_HIGH);
            notificationManager.createNotificationChannel(channel);
        }

        // Create the notification
        NotificationCompat.Builder builder = new NotificationCompat.Builder(context, "CHANNEL_ID")
                .setSmallIcon(R.mipmap.ic_launcher) // replace with your own icon
                .setContentTitle("SMS Alert")
                .setContentText("Your Message: " + content);

        // Show the notification
        notificationManager.notify(1, builder.build());
    }
}

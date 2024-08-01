package com.proj.phishingBuster.sms_interceptor;


import android.app.Service;
import android.content.BroadcastReceiver;
import android.content.Intent;
import android.content.IntentFilter;
import android.os.IBinder;

/*
* MySMSService - service that runs in the background
* TODO: change to foreground process to avoid system auto-termination
* Registers a BroadcastReceiver with the SMS_RECEIVED intent.
* */
public class SMSInterceptService extends Service {
    private BroadcastReceiver receiver;
    private boolean isReceiverRegistered = false;

    public IBinder onBind(Intent intent){
        return null;
    }

    public int onStartCommand(Intent intent, int flags, int startId){
        if (!isReceiverRegistered) {
            registerReceiver();
            isReceiverRegistered = true;
        }
        return START_STICKY;
    }

    private void registerReceiver(){
        receiver = new SMSBroadcastReceiver();
        IntentFilter filter = new IntentFilter("android.provider.Telephony.SMS_RECEIVED");
        registerReceiver(receiver, filter);
    }

    private void unregisterReceiver(){
        if(receiver != null){
            unregisterReceiver(receiver);
            receiver = null;
        }
    }

    public void onDestroy(){
        super.onDestroy();
        unregisterReceiver();
    }
}
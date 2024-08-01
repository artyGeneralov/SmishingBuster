package com.proj.phishingBuster;

import androidx.appcompat.app.AppCompatActivity;
import androidx.localbroadcastmanager.content.LocalBroadcastManager;

import android.content.BroadcastReceiver;
import android.content.Context;
import android.content.Intent;
import android.content.IntentFilter;
import android.os.Bundle;
import android.view.View;
import android.widget.Button;
import android.widget.TextView;

import com.proj.phishingBuster.comms_manager.serverComms;
import com.proj.phishingBuster.comms_manager.fcmService;
import com.proj.phishingBuster.database_dir.Message;


public class Settings extends AppCompatActivity {
    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_settings);
        Button buttonReturn = (Button) findViewById(R.id.ret);
        buttonReturn.setOnClickListener(new View.OnClickListener(){
            public void onClick (View v){
                returnHomePage();
            }
        });
    }
    private void returnHomePage() {
        finish();
    }

    protected void onDestroy() {
        super.onDestroy();
    }
}
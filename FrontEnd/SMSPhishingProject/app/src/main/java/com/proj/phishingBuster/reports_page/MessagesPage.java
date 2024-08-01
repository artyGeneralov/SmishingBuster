package com.proj.phishingBuster.reports_page;

import androidx.appcompat.app.AppCompatActivity;
import androidx.recyclerview.widget.LinearLayoutManager;
import androidx.recyclerview.widget.RecyclerView;

import android.content.Intent;
import android.os.Bundle;
import android.view.View;
import android.widget.Button;

import com.proj.phishingBuster.R;
import com.proj.phishingBuster.database_dir.Message;
import com.proj.phishingBuster.database_dir.DbManager;


import java.util.Collections;
import java.util.List;

public class MessagesPage extends AppCompatActivity  implements OnItemClickListener{
    private RecyclerView rvMessages;
    private MessageBoxAdapter adapter;
    private List<Message> messages;
    DbManager dbHelper;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_messages);
        rvMessages = findViewById(R.id.rvMessages);
        rvMessages.setLayoutManager(new LinearLayoutManager(this));
        setupMessages();
        Button buttonReturn = (Button) findViewById(R.id.ret);
        buttonReturn.setOnClickListener(new View.OnClickListener(){
            public void onClick (View v){
                returnHomePage();
            }
        });
    }
    @Override
    protected void onResume() {

        super.onResume();
        setupMessages();
    }

    private void setupMessages(){
        dbHelper = DbManager.getInstance(this);
        messages = dbHelper.getAllMessagesRaw();
        Collections.reverse(messages);
        adapter = new MessageBoxAdapter(messages, this);
        rvMessages.setAdapter(adapter);
    }

    public void onItemClick(int position){
        Message clickedItem = messages.get(position);
        Intent intent = new Intent(this, ReportPageLinear.class);
        intent.putExtra("messageID", clickedItem.getId());
        this.startActivity(intent);
    }
    private void returnHomePage() {
        finish();
    }


}
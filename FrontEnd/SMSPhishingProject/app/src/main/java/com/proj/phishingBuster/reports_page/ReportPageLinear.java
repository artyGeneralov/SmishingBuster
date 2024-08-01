package com.proj.phishingBuster.reports_page;
import android.content.Intent;
import android.graphics.Bitmap;
import android.graphics.BitmapFactory;
import android.graphics.Typeface;
import android.os.Bundle;
import android.text.Spannable;
import android.text.SpannableStringBuilder;
import android.text.style.AbsoluteSizeSpan;
import android.text.style.ForegroundColorSpan;
import android.text.style.StyleSpan;
import android.util.Log;
import android.view.View;
import android.widget.ImageView;
import android.widget.LinearLayout;
import android.widget.TextView;
import androidx.appcompat.app.AppCompatActivity;
import androidx.core.content.ContextCompat;

import com.google.android.material.button.MaterialButton;
import com.proj.phishingBuster.R;
import com.proj.phishingBuster.database_dir.Message;
import com.proj.phishingBuster.database_dir.DbManager;
import com.proj.phishingBuster.database_dir.Screenshot;

import java.util.List;
import java.util.Map;

public class ReportPageLinear extends AppCompatActivity {
    final static String TAG = "ReportPageLinear";
    Message message;
    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_report_linear);

        TextView arrivedTime = findViewById(R.id.arrived_time);
        TextView sender = findViewById(R.id.sender);
        TextView messageBody = findViewById(R.id.message_body);
        TextView dangerScore = findViewById(R.id.danger_score);
        LinearLayout suspiciousElementsContainer = findViewById(R.id.suspicious_elements_container);
        TextView suspiciousElements = findViewById(R.id.suspicious_elements);
        LinearLayout linksContainer = findViewById(R.id.links_container);
        TextView links = findViewById(R.id.links);
        LinearLayout screenshotsContainer = findViewById(R.id.link_screenshots_container);
        MaterialButton btnDelete = findViewById(R.id.btn_delete_message);

        DbManager db = DbManager.getInstance(this);

        Intent intent = getIntent();
        int messageID = 0;
        try {
            messageID = intent.getIntExtra("messageID",0);
        } catch (NullPointerException | NumberFormatException e) {
            Log.d(TAG, "Null or invalid message ID" + intent.getIntExtra("messageID",0));
            finish();
        }

        this.message = db.getMessageById(messageID);
        if (this.message == null) {
            Log.d(TAG, "Message not found");
            finish();
        }

        String arrivedTimeText = message.getDate();
        String senderText = message.getSender();
        String messageBodyText = message.getMsg();
        int score = message.getScore();

        String dangerScoreText = score + "/100";
        SpannableStringBuilder dangerScoreStr = new SpannableStringBuilder();
        if(score == -1){
            //TODO
        }
        else{
            int start = dangerScoreStr.length();
            dangerScoreStr.append(String.valueOf(score));
            int end = dangerScoreStr.length();
            dangerScoreStr.setSpan(new ForegroundColorSpan(getColorForPercentage(String.valueOf(score))), start, end, Spannable.SPAN_EXCLUSIVE_EXCLUSIVE);
            dangerScoreStr.setSpan(new StyleSpan(Typeface.BOLD), start, end, Spannable.SPAN_EXCLUSIVE_EXCLUSIVE);
            dangerScoreStr.setSpan(new AbsoluteSizeSpan(26, true), start, end, Spannable.SPAN_EXCLUSIVE_EXCLUSIVE);
            dangerScoreStr.append(" /100");
        }




        if (!arrivedTimeText.isEmpty()) {
            arrivedTime.setText(arrivedTimeText);
            arrivedTime.setVisibility(View.VISIBLE);
        }

        if (!senderText.isEmpty()) {
            sender.setText(senderText);
            sender.setVisibility(View.VISIBLE);
        }

        if (!messageBodyText.isEmpty()) {
            messageBody.setText(messageBodyText);
            messageBody.setVisibility(View.VISIBLE);
        }

        dangerScore.setText(dangerScoreStr);
        dangerScore.setVisibility(View.VISIBLE);

        Map<String, Integer> reportMap = message.getReportAsMap();

        String[] suspiciousElementsArray = reportMap.keySet().toArray(new String[0]);
        if (suspiciousElementsArray.length > 1) {
            suspiciousElementsContainer.setVisibility(View.VISIBLE);
            StringBuilder sb = new StringBuilder();
            for (String element : suspiciousElementsArray) {
                if(element.contains("Contains ")){
                    String newElem = element.replace("Contains ", "");
                    newElem = newElem.substring(0, 1).toUpperCase() + newElem.substring(1);
                    element = newElem;
                }
                if(element.contains("Amount")) continue;
                if(element.equals("Message length")) continue;
                sb.append("• ").append(element).append("\n");
            }
            suspiciousElements.setText(sb.toString().trim());
            suspiciousElements.setVisibility(View.VISIBLE);
        }

        Map<String, Integer> vtMap = message.getVTAsMap();
        Map<String, Integer> googleMap = message.getGoogleAsMap();
        Map<String, String> linksMap = message.getLinksAsMap();
        Log.d(TAG, vtMap.values().toString());
        String[] linksArray = linksMap.values().toArray(new String[0]);
        Integer[] vtArray = vtMap.values().toArray(new Integer[0]);
        Integer[] googleArray = googleMap.values().toArray(new Integer[0]);
        if (linksArray.length > 0) {
            linksContainer.setVisibility(View.VISIBLE);
            SpannableStringBuilder sb = new SpannableStringBuilder();
            for(int i = 0; i < linksArray.length; i++){
                String link = linksArray[i];
                sb.append("• ").append(link).append("\n");
                String vtString = "";
                String googleString = "";
                if(i < vtArray.length){
                    vtString = String.valueOf(vtArray[i]);
                }
                if(i < googleArray.length){
                    googleString = String.valueOf(googleArray[i]);
                }
                if (!vtString.isEmpty()) {
                    sb.append("\t\t Found ");
                    int start = sb.length();
                    sb.append(vtString).append("% suspicious by");
                    int end = start + vtString.length() + 1;
                    sb.setSpan(new ForegroundColorSpan(getColorForPercentage(vtString)), start, end, Spannable.SPAN_EXCLUSIVE_EXCLUSIVE);
                    sb.setSpan(new StyleSpan(Typeface.BOLD), start, end, Spannable.SPAN_EXCLUSIVE_EXCLUSIVE);
                    start = sb.length(); // Adjust for " suspicious by "
                    sb.append(" VirusTotal\n\n");
                    end = sb.length();
                    sb.setSpan(new ForegroundColorSpan(ContextCompat.getColor(this, R.color.element_txt_color)), start, end, Spannable.SPAN_EXCLUSIVE_EXCLUSIVE);
                    sb.setSpan(new StyleSpan(Typeface.BOLD), start, end, Spannable.SPAN_EXCLUSIVE_EXCLUSIVE);
                }
                if(!googleString.isEmpty())
                {
                    sb.append("\t\t Found ").append(vtString).append("% suspicious by GoogleSafeBrowsing\n\n");
                }
            }
            links.setText(sb);
            links.setVisibility(View.VISIBLE);
        }

        List<Screenshot> screenshotsList = db.getScreenshotsByMessageId(messageID);
        if (!screenshotsList.isEmpty()) {
            screenshotsContainer.setVisibility(View.VISIBLE);
            for (Screenshot screenshot : screenshotsList) {
                ImageView imageView = new ImageView(this);
                LinearLayout.LayoutParams layoutParams = new LinearLayout.LayoutParams(
                        LinearLayout.LayoutParams.WRAP_CONTENT,
                        LinearLayout.LayoutParams.WRAP_CONTENT);
                layoutParams.setMargins(0, 8, 0, 8);
                imageView.setLayoutParams(layoutParams);
                Bitmap screenshotBitmap = BitmapFactory.decodeByteArray(
                        screenshot.getBinaryData(), 0, screenshot.getBinaryData().length);
                imageView.setImageBitmap(screenshotBitmap);
                imageView.setScaleType(ImageView.ScaleType.CENTER_CROP);
                screenshotsContainer.addView(imageView);
            }
        }

        final int finalMessageID = messageID;
        btnDelete.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                db.deleteMessageById(finalMessageID);
                finish();
            }
        });
    }

    private int getColorForPercentage(String percentageString) {
        int percentage = Integer.parseInt(percentageString);
        if (percentage < 45) {
            return ContextCompat.getColor(this, R.color.score_low_txt);
        } else if (percentage > 75) {
            return ContextCompat.getColor(this, R.color.score_high_txt);
        } else {
            return ContextCompat.getColor(this, R.color.score_medium_txt);
        }
    }
}
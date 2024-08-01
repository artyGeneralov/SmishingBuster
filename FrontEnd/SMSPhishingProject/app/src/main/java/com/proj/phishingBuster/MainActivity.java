package com.proj.phishingBuster;

import androidx.annotation.NonNull;
import androidx.appcompat.app.AppCompatActivity;
import androidx.core.app.ActivityCompat;
import androidx.core.app.NotificationManagerCompat;
import androidx.core.content.ContextCompat;
import androidx.localbroadcastmanager.content.LocalBroadcastManager;

import android.animation.ArgbEvaluator;
import android.animation.ValueAnimator;
import android.content.BroadcastReceiver;
import android.content.Context;
import android.content.Intent;
import android.content.IntentFilter;
import android.content.SharedPreferences;
import android.content.pm.PackageManager;
import android.graphics.Typeface;
import android.graphics.drawable.GradientDrawable;
import android.graphics.drawable.LayerDrawable;
import android.os.Build;
import android.os.Bundle;
import android.text.Spannable;
import android.text.SpannableString;
import android.text.style.ForegroundColorSpan;
import android.text.style.StyleSpan;
import android.util.Log;
import android.view.MotionEvent;
import android.view.View;
import android.widget.Button;
import android.widget.TextView;

import com.google.android.gms.tasks.OnCompleteListener;
import com.google.android.gms.tasks.Task;
import com.google.android.material.button.MaterialButton;
import com.google.firebase.messaging.FirebaseMessaging;
import com.proj.phishingBuster.reports_page.MessagesPage;
import com.proj.phishingBuster.database_dir.DbManager;
import com.proj.phishingBuster.sms_interceptor.SMSInterceptService;

public class MainActivity extends AppCompatActivity {

    private static final String TAG = "MainActivity";
    private static final int SMS_PERMISSION_CODE = 100;
    private static final int POST_NOTIFICATIONS_REQUEST_CODE = 123;

    private boolean hasSMSPermission = false;
    private boolean hasNotificationPermission = false;
    private boolean serviceRunning = false;

    private DbManager dbHelper;
    private TextView protectionStatusTextView;
    private MaterialButton toggleButton;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);

        setContentView(R.layout.activity_main);
        dbHelper = DbManager.getInstance(this);

        MaterialButton buttonSettings = findViewById(R.id.settings);
        Button buttonReports = findViewById(R.id.reports);
        toggleButton = findViewById(R.id.toggleButton);
        protectionStatusTextView = findViewById(R.id.tvServiceStatus);

        SharedPreferences preferences = getSharedPreferences("app_prefs", Context.MODE_PRIVATE);
        serviceRunning = preferences.getBoolean("service_running", false);
        toggleButton.setChecked(serviceRunning);
        updateTextView(serviceRunning);
        updateBackgroundColor(serviceRunning);

        if (!hasPermission()) {
            requestPermissions();
        } else {
            requestNotificationPermission();
            startAppFunctions();
        }

        // Toggle button for starting/stopping service
        toggleButton.setOnTouchListener(new View.OnTouchListener() {
            @Override
            public boolean onTouch(View view, MotionEvent event) {
                switch (event.getAction()) {
                    case MotionEvent.ACTION_DOWN:
                        view.getBackground().setAlpha(150);
                        break;
                    case MotionEvent.ACTION_UP:
                        view.getBackground().setAlpha(255);
                        handleToggleButtonClick();
                        break;
                    case MotionEvent.ACTION_CANCEL:
                        view.getBackground().setAlpha(255);
                        break;
                    default:
                        return false;
                }
                return true;
            }
        });

        buttonReports.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                openReports();
            }
        });

        buttonSettings.setOnTouchListener(new View.OnTouchListener() {
            @Override
            public boolean onTouch(View view, MotionEvent event) {
                switch (event.getAction()) {
                    case MotionEvent.ACTION_DOWN:
                        view.getBackground().setAlpha(150);
                        break;
                    case MotionEvent.ACTION_UP:
                        view.getBackground().setAlpha(255);
                        openSettings();
                }
                return true;
            }
        });
    }

    @Override
    protected void onStart() {
        super.onStart();
        LocalBroadcastManager.getInstance(this).registerReceiver(smsUpdateReceiver, new IntentFilter("SMS_UPDATE_ACTION"));
        updateServiceState();
    }

    @Override
    protected void onStop() {
        super.onStop();
        LocalBroadcastManager.getInstance(this).unregisterReceiver(smsUpdateReceiver);
    }

    private final BroadcastReceiver smsUpdateReceiver = new BroadcastReceiver() {
        @Override
        public void onReceive(Context context, Intent intent) {
            updateServiceState();
        }
    };

    private void updateServiceState() {
        // Check if the service is running and update UI accordingly
        serviceRunning = isServiceRunning();
        SharedPreferences preferences = getSharedPreferences("app_prefs", Context.MODE_PRIVATE);
        SharedPreferences.Editor editor = preferences.edit();
        editor.putBoolean("service_running", serviceRunning);
        editor.apply();
        toggleButton.setChecked(serviceRunning);
        updateTextView(serviceRunning);
        updateBackgroundColor(serviceRunning);

    }

    private void updateTextView(boolean isRunning) {
        String protectionStatus = isRunning ? "ON" : "OFF";
        String fullText = "Protection is " + protectionStatus;
        SpannableString spannableString = new SpannableString(fullText);
        int start = fullText.indexOf(protectionStatus);
        int end = start + protectionStatus.length();

        int textColor = ContextCompat.getColor(this, R.color.element_txt_color);
        spannableString.setSpan(new ForegroundColorSpan(textColor), 0, start, Spannable.SPAN_EXCLUSIVE_EXCLUSIVE);
        int statusColor = isRunning ? ContextCompat.getColor(this, R.color.protection_on)
                : ContextCompat.getColor(this, R.color.protection_off);
        spannableString.setSpan(new ForegroundColorSpan(statusColor), start, end, Spannable.SPAN_EXCLUSIVE_EXCLUSIVE);
        spannableString.setSpan(new StyleSpan(Typeface.BOLD), start, end, Spannable.SPAN_EXCLUSIVE_EXCLUSIVE);

        protectionStatusTextView.setText(spannableString);
    }

    private void updateBackgroundColor(boolean isRunning) {
        LayerDrawable layerDrawable = (LayerDrawable) ContextCompat.getDrawable(this, R.drawable.combined_bg_overlay);

        assert layerDrawable != null;
        GradientDrawable gradientDrawable = (GradientDrawable) layerDrawable.getDrawable(1);

        int currentEndColor = gradientDrawable.getColors() != null ? gradientDrawable.getColors()[2] : ContextCompat.getColor(this, R.color.main_bg_end_red);

        int newEndColor;
        if (isRunning) {
            newEndColor = ContextCompat.getColor(this, R.color.main_bg_end_green);
        } else {
            newEndColor = ContextCompat.getColor(this, R.color.main_bg_end_red);
        }

        ValueAnimator colorAnimator = ValueAnimator.ofObject(new ArgbEvaluator(), currentEndColor, newEndColor);
        colorAnimator.setDuration(500);
        colorAnimator.addUpdateListener(animation -> {
            int color = (int) animation.getAnimatedValue();
            gradientDrawable.setColors(new int[]{
                    ContextCompat.getColor(this, R.color.main_bg_start),
                    ContextCompat.getColor(this, R.color.main_bg_mid),
                    color
            });
            findViewById(android.R.id.content).setBackground(layerDrawable);
        });

        colorAnimator.start();
    }

    private void handleToggleButtonClick() {
        SharedPreferences preferences = getSharedPreferences("app_prefs", Context.MODE_PRIVATE);
        SharedPreferences.Editor editor = preferences.edit();

        Log.d(TAG, "CLICK");
        if (!serviceRunning && hasPermission()) {
            Log.d(TAG, "Starting service");
            Intent serviceIntent = new Intent(MainActivity.this, SMSInterceptService.class);
            ContextCompat.startForegroundService(MainActivity.this, serviceIntent);
            setServiceRunning(true);
            editor.putBoolean("service_running", true);
        } else if (serviceRunning) {
            Log.d(TAG, "Stopping service");
            Intent serviceIntent = new Intent(MainActivity.this, SMSInterceptService.class);
            stopService(serviceIntent);
            setServiceRunning(false);
            editor.putBoolean("service_running", false);
        }
        editor.apply();
        updateServiceState();
    }

    private void openSettings() {
        Intent intent = new Intent(this, Settings.class);
        startActivity(intent);
    }

    private void openReports() {
        Intent intent = new Intent(this, MessagesPage.class);
        startActivity(intent);
    }

    private boolean isServiceRunning() {
        return serviceRunning;
    }

    private void setServiceRunning(boolean isRunning) {
        if (isRunning) {
            startService(new Intent(MainActivity.this, SMSInterceptService.class));
        } else {
            stopService(new Intent(MainActivity.this, SMSInterceptService.class));
        }
        this.serviceRunning = isRunning;
    }

    private boolean hasPermission() {
        return ContextCompat.checkSelfPermission(this, android.Manifest.permission.RECEIVE_SMS) == PackageManager.PERMISSION_GRANTED &&
                ContextCompat.checkSelfPermission(this, android.Manifest.permission.SEND_SMS) == PackageManager.PERMISSION_GRANTED &&
                ContextCompat.checkSelfPermission(this, android.Manifest.permission.READ_SMS) == PackageManager.PERMISSION_GRANTED;
    }

    private void requestPermissions() {
        ActivityCompat.requestPermissions(this, new String[]{
                android.Manifest.permission.RECEIVE_SMS,
                android.Manifest.permission.READ_SMS,
                android.Manifest.permission.SEND_SMS
        }, SMS_PERMISSION_CODE);
    }

    private void requestNotificationPermission() {
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.TIRAMISU) {
            if (ContextCompat.checkSelfPermission(this, android.Manifest.permission.POST_NOTIFICATIONS) != PackageManager.PERMISSION_GRANTED) {
                Log.d(TAG, "Requesting notification permissions for Android 13 and above");
                ActivityCompat.requestPermissions(this, new String[]{android.Manifest.permission.POST_NOTIFICATIONS}, POST_NOTIFICATIONS_REQUEST_CODE);
            } else {
                // Permission is already granted
                hasNotificationPermission = true;
                startAppFunctions();
            }
        } else {
            // For Android versions below 13, check if notifications are enabled
            if (!NotificationManagerCompat.from(this).areNotificationsEnabled()) {
                Log.d(TAG, "Notifications are not enabled, prompt the user to enable them in settings");
                // Here you could prompt the user to enable notifications in settings, if necessary
            } else {
                // Notifications are enabled
                hasNotificationPermission = true;
                startAppFunctions();
            }
        }
    }

    @Override
    public void onRequestPermissionsResult(int requestCode, @NonNull String[] permissions, @NonNull int[] grantResults) {
        super.onRequestPermissionsResult(requestCode, permissions, grantResults);
        if (requestCode == SMS_PERMISSION_CODE) {
            hasSMSPermission = grantResults.length > 0 && grantResults[0] == PackageManager.PERMISSION_GRANTED;
            if (hasSMSPermission) {
                // Now request the notification permission
                requestNotificationPermission();
            } else {
                // Handle SMS permission denial
                Log.d(TAG, "SMS permission denied");
            }
        } else if (requestCode == POST_NOTIFICATIONS_REQUEST_CODE) {
            hasNotificationPermission = grantResults.length > 0 && grantResults[0] == PackageManager.PERMISSION_GRANTED;
            if (hasNotificationPermission) {
                // Start app functions now that all permissions are granted
                startAppFunctions();
            } else {
                // Handle notification permission denial
                Log.d(TAG, "Notification permission denied");
            }
        }
    }

    private void startAppFunctions() {
        // Get FCM token
        FirebaseMessaging.getInstance().getToken()
                .addOnCompleteListener(new OnCompleteListener<String>() {
                    @Override
                    public void onComplete(@NonNull Task<String> task) {
                        if (!task.isSuccessful()) {
                            Log.w("fcm", "Fetching FCM registration token failed", task.getException());
                            return;
                        }

                        // Get new FCM registration token
                        String token = task.getResult();
                        Log.d("fcm", "Token: " + token);

                        // Save token to preferences
                        SharedPreferences preferences = getSharedPreferences("app_prefs", Context.MODE_PRIVATE);
                        SharedPreferences.Editor editor = preferences.edit();
                        editor.putString("fcm_token", token);
                        editor.apply();
                    }
                });

        // Restore button state from SharedPreferences
        SharedPreferences preferences = getSharedPreferences("app_prefs", Context.MODE_PRIVATE);
        serviceRunning = preferences.getBoolean("service_running", false);
        toggleButton.setChecked(serviceRunning);
        updateTextView(serviceRunning);
        updateBackgroundColor(serviceRunning);
    }
}

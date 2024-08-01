package com.proj.phishingBuster.reports_page;

import android.graphics.drawable.GradientDrawable;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.TextView;

import androidx.annotation.NonNull;
import androidx.core.content.ContextCompat;
import androidx.recyclerview.widget.RecyclerView;


import com.proj.phishingBuster.R;
import com.proj.phishingBuster.database_dir.Message;


import java.util.List;




public class MessageBoxAdapter extends RecyclerView.Adapter<MessageBoxAdapter.MessageViewHolder> {
    private final List<Message> messages;
    private static final String TAG = "MessageBoxAdapter";

    static final int LOW_THRESHOLD = 45;
    static final int HIGH_THRESHOLD = 75;

    private OnItemClickListener itemClickListener;
    public MessageBoxAdapter(List<Message> messages, OnItemClickListener itemClickListener){
        this.messages = messages;
        this.itemClickListener = itemClickListener;
    }

    @NonNull
    @Override
    public MessageViewHolder onCreateViewHolder(@NonNull ViewGroup parent, int viewType){
        View view = LayoutInflater.from(parent.getContext()).inflate(R.layout.message_box, parent, false);
        return new MessageViewHolder(view, itemClickListener);
    }

    @Override
    public void onBindViewHolder(@NonNull MessageViewHolder holder, int position) {
        Message message = messages.get(position);
        holder.tvSender.setText(message.getSender());
        holder.tvMessage.setText(message.getMsg());

        int score = message.getScore();
        int scoreColor;
        int scoreBgColor;
        if(score == -1){
            holder.tvScore.setText("?");
            scoreColor = R.color.score_pending_txt;
            scoreBgColor = R.color.score_pending_bg;
        }
        else {
            holder.tvScore.setText(String.valueOf(score));


            if (score < LOW_THRESHOLD) {
                /*Set text and box color to blue*/
                scoreColor = R.color.score_low_txt;
                scoreBgColor = R.color.score_low_bg;
            }

            else if (score < HIGH_THRESHOLD) {
                /*Set text and box color to yellow*/
                scoreColor = R.color.score_medium_txt;
                scoreBgColor = R.color.score_medium_bg;
            }

            else {
                /*Set text and box color to red*/
                scoreColor = R.color.score_high_txt;
                scoreBgColor = R.color.score_high_bg;
            }

            holder.tvScore.setTextColor(ContextCompat.getColor(holder.tvScore.getContext(), scoreColor));
            GradientDrawable drawable = (GradientDrawable) holder.scoreBox.getBackground();
            drawable.setColor(ContextCompat.getColor(holder.scoreBox.getContext(), scoreBgColor));
            drawable.setCornerRadius(16f); // Adjust the radius as needed
        }
    }
    @Override

    public int getItemCount(){
        return messages.size();
    }

    static class MessageViewHolder extends RecyclerView.ViewHolder implements View.OnClickListener{
        TextView tvSender, tvMessage, tvScore;
        View scoreBox;

        OnItemClickListener itemClickListener;
        MessageViewHolder(View itemView, OnItemClickListener itemClickListener){
            super(itemView);
            tvSender = itemView.findViewById(R.id.tvSender);
            tvMessage = itemView.findViewById(R.id.tvMessage);
            tvScore = itemView.findViewById(R.id.tvScore);
            scoreBox = itemView.findViewById(R.id.score_square);
            this.itemClickListener = itemClickListener;
            itemView.setOnClickListener(this);
        }
        public void onClick(View view){
            if(itemClickListener != null){
                itemClickListener.onItemClick(getAdapterPosition());
            }
        }
    }
}



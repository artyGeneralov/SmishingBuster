# Generating 50 ham messages with different styles and contents
import pandas as pd

# Generating 50 ham messages with longer, more realistic content

longer_ham_messages = [
    ("ham", "Hey, I wanted to let you know that I'll be out of the office next week for a family vacation. If you need anything urgent, please contact Jane. Otherwise, I'll get back to you as soon as I'm back."),
    ("ham", "Just a reminder, the team meeting has been rescheduled to Wednesday at 10 AM. Please ensure you review the project updates before the meeting so we can discuss them."),
    ("ham", "Happy birthday, Sarah! I hope you have a wonderful day filled with joy and surprises. Don't forget to take some time off and celebrate with your loved ones."),
    ("ham", "Can you send me the contact details for the new client we discussed in yesterday's meeting? I need to set up an introductory call with them by the end of this week."),
    ("ham", "I just got back from an amazing vacation in Italy! The food, the culture, and the scenery were all incredible. I can't wait to share all the photos with you."),
    ("ham", "Let's catch up over coffee next week. There are some exciting updates about the project that I would love to discuss with you in person."),
    ("ham", "The quarterly financial review meeting has been rescheduled to Friday at 3 PM. Please ensure all your reports are submitted by Thursday noon."),
    ("ham", "I'll be working from home tomorrow due to a scheduled maintenance at my place. You can reach me via email or Slack if you need anything."),
    ("ham", "Great job on the presentation today! The client was really impressed with our proposal. Let's keep the momentum going for the final review."),
    ("ham", "Can we move our call to 2 PM instead of 1 PM? I have a conflicting meeting that I can't reschedule. Let me know if this works for you."),
    ("ham", "I'll see you at the office by 9 AM tomorrow. We need to go over the project plan before the client meeting at 10."),
    ("ham", "Did you finish reading the book I lent you? I'd love to hear your thoughts on it. I found it quite insightful."),
    ("ham", "I'm really excited for our trip to the mountains next month. It's been a while since we had a proper break, and I can't wait to relax and enjoy nature."),
    ("ham", "Don't forget to call Mom on her birthday this Sunday. She's been looking forward to hearing from you and catching up."),
    ("ham", "I'll be late to the meeting, so please start without me. I'll join in as soon as I can. Make sure to cover the key points of the agenda."),
    ("ham", "Let's meet at the new Italian restaurant downtown at 7 PM tonight. I've heard great things about their pasta and wine selection."),
    ("ham", "Just sent you the updated report. Please review it and let me know if there are any changes needed before we finalize it."),
    ("ham", "Are you available for a quick call later today? I need to discuss some details about the project timeline with you."),
    ("ham", "Thanks for all your help with the project. Your input was invaluable, and we couldn't have done it without you."),
    ("ham", "I'll bring the snacks for the team meeting tomorrow. Let me know if you have any special requests or dietary restrictions."),
    ("ham", "Looking forward to seeing you at the event next week. It's going to be a great opportunity to network and learn from industry leaders."),
    ("ham", "Can you review this document for me and provide your feedback? I want to ensure everything is accurate before we submit it."),
    ("ham", "Happy anniversary to you and John! I hope you both have a wonderful day celebrating your special milestone together."),
    ("ham", "The team did a great job this quarter. Let's celebrate our success with a team lunch next Friday. I'll send out the details soon."),
    ("ham", "I'll be there in 10 minutes. Traffic was a bit heavier than expected, but I'm on my way. See you soon!"),
    ("ham", "Let's plan a movie night soon. There are a few new releases that I've been wanting to watch. How about next Saturday?"),
    ("ham", "Can you send me the address again? I seem to have misplaced it, and I need it for the delivery scheduled for tomorrow."),
    ("ham", "I'll handle the client meeting tomorrow. Make sure to send me all the relevant documents and notes beforehand."),
    ("ham", "Remember to check your email for the details of the upcoming workshop. It's going to be a great learning experience."),
    ("ham", "Are you free this Friday evening? There's a new restaurant that I've been wanting to try, and I'd love for you to join me."),
    ("ham", "I'll take care of the presentation slides. Just send me the content you want included, and I'll put it together."),
    ("ham", "Join us for dinner at our place this weekend. We're having a small get-together, and it would be great to see you."),
    ("ham", "Just landed and heading to the hotel. The flight was smooth, and I'll update you on the schedule once I'm settled."),
    ("ham", "Thanks for the birthday wishes! I had a great day celebrating with family and friends. Your message made it even more special."),
    ("ham", "I'll be offline for the next hour due to a meeting. If you need anything urgent, please leave a message, and I'll get back to you."),
    ("ham", "Can you help me with this report? I need a second pair of eyes to review the data and ensure everything is accurate."),
    ("ham", "Just saw your email, and I'll respond soon. I need to gather some information before I can provide a detailed answer."),
    ("ham", "I'm free this weekend, let's catch up! It's been a while since we last talked, and I have so much to share with you."),
    ("ham", "I'll bring the dessert for the potluck on Sunday. Let me know if you have any preferences or if there's something specific you'd like."),
    ("ham", "Can we reschedule our lunch to tomorrow? I have an urgent meeting today that I can't miss."),
    ("ham", "The meeting has been rescheduled to 4 PM. Please update your calendar and make sure to be there on time."),
    ("ham", "I'll send the agenda for the next meeting shortly. Please review it and let me know if there's anything you want to add."),
    ("ham", "Are you attending the conference next month? It's a great opportunity to learn about the latest industry trends."),
    ("ham", "I'll be at the gym tomorrow morning for our workout session. Don't forget to bring your water bottle and towel."),
    ("ham", "Just finished the project and sending it your way now. Please review it and provide your feedback."),
    ("ham", "Can you check the status of my request? I submitted it last week, and I haven't received any updates yet."),
    ("ham", "I'll be working late tonight to finish up some tasks. If you need anything, you can reach me on my mobile."),
    ("ham", "Let's discuss the project details over lunch tomorrow. I have some new ideas that I think you'll find interesting."),
    ("ham", "Looking forward to your presentation next week. I'm sure you'll do a fantastic job as always.")
]

# Converting the list into a DataFrame
df_longer_ham = pd.DataFrame(longer_ham_messages, columns=["LABEL", "TEXT"])

# Saving the DataFrame to a CSV file
file_path_longer_ham = "longer_ham_messages.csv"
df_longer_ham.to_csv(file_path_longer_ham, index=False)

file_path_longer_ham



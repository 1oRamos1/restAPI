# app_name/services.py
import logging
from .models import Task
from ollama import chat  # Assuming your AI wrapper is imported here


def generate_and_save_summary(user_track):
    try:
        tasks = Task.objects.filter(user_learning_track=user_track, status="completed").order_by("id")
        if not tasks.exists():
            user_track.summary = "No progress yet."
            user_track.save(update_fields=['summary'])
            return user_track.summary

        progress_data = "\n".join(
            f"Title: {t.task.split('### Title:')[1].splitlines()[0].strip() if '### Title:' in t.task else 'Unknown'}\n"
            f"Grade: {t.grade}/5\n"
            f"Review: {t.review.strip()}"
            for t in tasks if t.grade is not None
        )

        prompt = (
            "Please summarize my progress.\n"
            "Here is the detailed progress so far:\n"
            f"{progress_data}\n\n"
            "Write a short summary (3–5 lines) that captures my overall progress, "
            "strengths, and areas I need to improve.\n"
            "Speak directly to me (second person). Start the summary with 'You...'.\n"
            "Do NOT repeat individual task details. Be clear and motivating."
            "VERY IMPORTANT:\n"
            "- Do NOT any greetings, follow-ups or titles, just clean review.\n"
            "Please summarize my progress.\n"
            "Here is the detailed progress so far:\n"
            f"{progress_data}\n\n"
            "Write a short summary (3–5 lines) that captures my overall progress, "
            "strengths, and areas I need to improve.\n"
            "Speak directly to me (second person). Start the summary with 'You...'.\n"
            "Do NOT repeat individual task details. Be clear and motivating."
            "VERY IMPORTANT:\n"
            "- Do NOT any greetings, follow-ups or titles, just clean review.\n"
        )

        response = chat(model="llama3", messages=[{"role": "user", "content": prompt}])
        concise_summary = response.get("message", {}).get("content") or response.get("content")

        user_track.summary = concise_summary.strip()
        user_track.save(update_fields=['summary'])

        return user_track.summary

    except Exception as e:
        logging.error(f"Summary generation failed: {e}")
        return None

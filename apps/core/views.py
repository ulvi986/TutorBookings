import json
import urllib.error
import urllib.request

from django.shortcuts import render
from django.views.generic import TemplateView


class HomeView(TemplateView):
    template_name = "core/home.html"


def chatbot_view(request):
    api_url = "https://u-sharifzade2007--teacher-router-api-fastapi-app.modal.run/predict"
    question = ""
    answer = ""
    error = ""
    history = request.session.get("chat_history", [])

    if request.method == "POST":
        question = request.POST.get("question", "").strip()
        if not question:
            error = "Please write a question first."
        else:
            try:
                payload = json.dumps({"text": question}).encode("utf-8")
                req = urllib.request.Request(
                    api_url,
                    data=payload,
                    headers={"Content-Type": "application/json"},
                    method="POST",
                )
                with urllib.request.urlopen(req, timeout=30) as response:
                    data = json.loads(response.read().decode("utf-8"))

                answer = (
                    data.get("answer")
                    or data.get("response")
                    or data.get("prediction")
                    or data.get("result")
                    or data.get("output")
                    or str(data)
                )
                history.append({"question": question, "answer": answer})
                request.session["chat_history"] = history[-10:]
            except urllib.error.HTTPError as exc:
                try:
                    details = exc.read().decode("utf-8")
                except Exception:
                    details = ""
                error = f"Chatbot service error: HTTP {exc.code}"
                if details:
                    error = f"{error} - {details}"
            except Exception:
                error = "Could not reach chatbot service. Please try again."

    return render(
        request,
        "core/chatbot.html",
        {"question": question, "answer": answer, "error": error, "history": history},
    )

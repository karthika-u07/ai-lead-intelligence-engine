from celery import shared_task
from django.conf import settings
from .models import Lead
from tavily import TavilyClient
from groq import Groq
from django.core.mail import send_mail


@shared_task(bind=True, autoretry_for=(Exception,), retry_kwargs={"max_retries": 3, "countdown": 5})
def enrich_lead_task(self, lead_id):
    lead = Lead.objects.get(id=lead_id)

    # ---------- Tavily Enrichment ----------
    tavily = TavilyClient(api_key=settings.TAVILY_API_KEY)

    # Phase 1 — Person identity (STRICT LinkedIn)
    person_result = tavily.search(
        query=f'site:linkedin.com/in "{lead.linkedin_url}" "{lead.name}"',
        max_results=5
    )

    # Phase 2 — Personal GitHub / portfolio (optional but powerful)
    portfolio_result = tavily.search(
        query=f'"{lead.name}" github OR portfolio',
        max_results=3
    )

    # Phase 3 — Company info
    company_result = tavily.search(
        query=f'{lead.company} official website recent news',
        max_results=3
    )

    summary = ""

    def relevant_person(text):
        return lead.name.lower() in text.lower() or "linkedin" in text.lower()

    # PERSON FIRST
    for r in person_result["results"] + portfolio_result["results"]:
        if relevant_person(r["content"]):
            summary += r["content"] + "\n"

    # COMPANY SECOND (only appended)
    for r in company_result["results"]:
        summary += r["content"] + "\n"

    lead.company_summary = summary
    lead.status = "ENRICHED"
    lead.save()

    # ---------- Groq Email Generation ----------
    client = Groq(api_key=settings.GROQ_API_KEY)

    prompt = f"""
    You are an AI research analyst.

    Using the web data below, build a professional intelligence report.

    DATA:
    {summary}

    Generate:

    1. Person Overview
    2. Current Role
    3. Key Skills / Background
    4. Projects or Achievements
    5. Company Information
    6. Recent News or Initiatives

    Format clean bullet points.

    Then give a short summary paragraph.
    """

    completion = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[
            {"role": "user", "content": prompt}
        ]
    )

    email_text = completion.choices[0].message.content

    lead.generated_email = email_text
    lead.status = "EMAIL_SENT"
    lead.save()
    send_mail(
        subject=f"AI Lead Intelligence Report – {lead.name}",
        message=email_text,
        from_email=settings.EMAIL_HOST_USER,
        recipient_list=["projectdjangoacc01@gmail.com"],
        fail_silently=False,
    )

    return True

import logging
from celery import shared_task
from django.conf import settings
from django.core.mail import send_mail
from .models import Lead
from tavily import TavilyClient
from groq import Groq
from django.core.cache import cache

logger = logging.getLogger(__name__)


@shared_task(bind=True, autoretry_for=(Exception,), retry_kwargs={"max_retries": 3, "countdown": 5})
def enrich_lead_task(self, lead_id):

    # ---------- GET LEAD ----------
    try:
        lead = Lead.objects.get(id=lead_id)
    except Lead.DoesNotExist:
        logger.error(f"Lead {lead_id} not found")
        return False

    # ---------- CACHE CHECK ----------
    cache_key = f"lead_enrichment:v1:{lead.email}:{lead.company}"

    cached_data = cache.get(cache_key)

    if cached_data:
        logger.info(f"⚡ Cache hit for lead {lead.id}")

        lead.generated_email = cached_data["email"]
        lead.company_summary = cached_data["summary"]
        lead.status = "EMAIL_SENT"
        lead.save()

        return True

    # ---------- STATUS: START ----------
    lead.status = "ENRICHING"
    lead.save()

    # ---------- TAVILY ----------
    try:
        tavily = TavilyClient(api_key=settings.TAVILY_API_KEY)

        # Person search (better context)
        person_result = tavily.search(
            query=f'"{lead.name}" {lead.company} LinkedIn profile',
            max_results=5
        )

        # Portfolio
        portfolio_result = tavily.search(
            query=f'"{lead.name}" github OR portfolio',
            max_results=3
        )

        # Company
        company_result = tavily.search(
            query=f'{lead.company} recent news OR product OR technology',
            max_results=3
        )

    except Exception:
        logger.error("Tavily failed", exc_info=True)
        lead.status = "FAILED"
        lead.save()
        return False

    # ---------- FILTER ----------
    def is_relevant(text):
        text = text.lower()
        return (
            lead.name.lower() in text and
            lead.company.lower() in text
        )

    summary_parts = []

    # Person + Portfolio
    for r in person_result.get("results", []) + portfolio_result.get("results", []):
        content = r.get("content", "")
        if is_relevant(content):
            summary_parts.append(content)

    # ---------- FALLBACK ----------
    if not summary_parts:
        logger.warning(f"Fallback to company data for lead {lead.id}")
        for r in company_result.get("results", []):
            summary_parts.append(r.get("content", ""))

    summary = "\n".join(summary_parts[:10])

    # ---------- EMPTY CHECK ----------
    if not summary:
        logger.error(f"No data found for lead {lead.id}")
        lead.status = "FAILED"
        lead.save()
        return False

    lead.company_summary = summary
    lead.status = "ENRICHED"
    lead.save()

    # ---------- GROQ ----------
    try:
        client = Groq(api_key=settings.GROQ_API_KEY)

        prompt = f"""
You are an AI research analyst.

Generate a structured professional report.

Lead:
Name: {lead.name}
Company: {lead.company}

Rules:
- Use ONLY relevant information
- Ignore unrelated people
- Be concise and professional

DATA:
{summary}

Output:
- Person Overview
- Role
- Skills
- Achievements
- Company Info
- Recent News

Then a short summary paragraph.
"""

        completion = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[{"role": "user", "content": prompt}]
        )

        email_text = completion.choices[0].message.content

    except Exception:
        logger.error("Groq failed", exc_info=True)
        lead.status = "FAILED"
        lead.save()
        return False

    # ---------- VALIDATION ----------
    if lead.name.lower() not in email_text.lower():
        logger.warning(f"Invalid output for lead {lead.id}")
        lead.status = "FAILED"
        lead.save()
        return False

    lead.generated_email = email_text

    # ---------- STORE IN CACHE ----------
    cache.set(cache_key, {
        "email": email_text,
        "summary": summary
    }, timeout=3600)

    # ---------- EMAIL ----------
    try:
        send_mail(
            subject=f"AI Lead Intelligence Report – {lead.name}",
            message=email_text,
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=["projectdjangoacc01@gmail.com"],
            fail_silently=False,
        )

        lead.status = "EMAIL_SENT"

    except Exception:
        logger.error("Email failed", exc_info=True)
        lead.status = "FAILED"
        lead.save()
        return False

    # ---------- FINAL SAVE ----------
    lead.save()

    logger.info(f"Lead {lead.id} processed successfully")

    return True
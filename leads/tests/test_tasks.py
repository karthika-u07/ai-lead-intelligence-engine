import pytest
from unittest.mock import patch, MagicMock
from leads.tasks import enrich_lead_task
from leads.models import Lead


# ---------------- SUCCESS CASE ---------------- #

@pytest.mark.django_db
@patch("leads.tasks.TavilyClient")
@patch("leads.tasks.Groq")
@patch("leads.tasks.send_mail")
def test_enrich_lead_task_success(mock_email, mock_groq, mock_tavily):

    mock_tavily.return_value.search.return_value = {
        "results": [{"content": "John Google data"}]
    }

    # FIXED
    mock_groq.return_value.chat.completions.create.return_value = MagicMock(
        choices=[MagicMock(message=MagicMock(content="John works at Google"))]
    )

    lead = Lead.objects.create(
        name="John",
        company="Google",
        email="john@test.com"
    )

    result = enrich_lead_task(lead.id)
    lead.refresh_from_db()

    assert result is True
    assert lead.generated_email is not None
    assert lead.status == "EMAIL_SENT"


# ---------------- EMPTY DATA CASE ---------------- #

@pytest.mark.django_db
@patch("leads.tasks.TavilyClient")
@patch("leads.tasks.Groq")
def test_enrich_lead_no_data(mock_groq, mock_tavily):

    mock_tavily.return_value.search.return_value = {"results": []}

    lead = Lead.objects.create(
        name="John",
        company="Google",
        email="empty@test.com"
    )

    result = enrich_lead_task(lead.id)
    lead.refresh_from_db()

    #  FIXED
    assert result is False
    assert lead.status == "FAILED"
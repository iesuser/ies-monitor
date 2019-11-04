from django.db import models

# Create your models here.

class Message(models.Model):

    sender = models.CharField(max_length=255, help_text="client-ის სკრიპტის სახელი საიდანაც მოვიდა შეტყობინება")
    message_type = models.CharField(max_length=50, help_text="შეტყობინების ტიპი")
    title = models.CharField(max_length=255, help_text="შეტყობინების სათაური")
    text = models.TextField(help_text="შეტყობინების შინაარსი")
    sent_message_datetime = models.DateField(help_text="შეტყობინების დრო როდესაც დაგენერირდა client-ის მხარეს")
    sender_ip = models.CharField(max_length=30, help_text="შეტყობინების გამომგზავნის IP")

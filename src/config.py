# Shared configuration — loads env vars and dropdown lists used across all pages and services.
import os
from dotenv import load_dotenv
from utils.categorical_lists import industries, countries, states

load_dotenv()

HF_TOKEN = os.getenv("HF_TOKEN")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")

INDUSTRIES = industries()
COUNTRIES = countries()
STATES = states()

# Prompt Templates

This directory contains AI prompt templates used by the AegisX planning engine.

## Templates

### weekly_plan.txt
Template for generating weekly plans. Used by the `/plan/week` endpoint.

### daily_plan.txt
Template for generating daily plans. Used by the `/plan/today` endpoint.

## Template Variables

All templates support the following variables:
- `{context}`: User-provided context about their current situation
- `{goals}`: List of goals to achieve
- `{constraints}`: Any constraints or limitations to consider

## Customization

You can customize these templates to adjust the planning behavior:
1. Edit the template files directly
2. Modify the instructions to change planning style
3. Add or remove sections as needed
4. Restart the service to load updated templates

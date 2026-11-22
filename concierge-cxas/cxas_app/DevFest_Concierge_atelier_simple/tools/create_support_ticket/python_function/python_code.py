def create_support_ticket(category: str, message: str) -> dict:
    """Ouvrir immédiatement une demande d'assistance pour un problème décrit, sans brouillon ni confirmation.

    Args:
        category: Code exact en minuscules : access, session, technical ou other.
            Utiliser technical pour la facturation GCP, le Wi-Fi, les navigateurs et logiciels.
            Jamais un libellé traduit ni un résumé du problème.
        message: Description du problème, 1 à 2000 caractères, telle que donnée par l'utilisateur.

    Returns:
        status ok avec le ticket (ticket_id, category, message) et une notice. Le même problème
        (même catégorie, même message) renvoie le ticket déjà ouvert dans la session.
    """
    import json
    import uuid
    if category not in ['access', 'session', 'technical', 'other']:
        return {'status': 'invalid_input', 'field': 'category', 'allowed_values': ['access', 'session', 'technical', 'other'], 'agent_action': 'Réessayer immédiatement avec le même message et un code de catégorie autorisé.'}
    if not isinstance(message, str) or not message.strip() or len(message) > 2000:
        return {'status': 'invalid_input', 'field': 'message', 'agent_action': 'Demander uniquement la description du problème, de 1 à 2000 caractères.'}
    text = message.strip()
    key = category + ':' + ' '.join(text.casefold().split())
    try:
        tickets = json.loads(context.state.get('support_tickets') or '{}')
        if key not in tickets:
            tickets[key] = {'ticket_id': 'TKT-' + uuid.uuid4().hex[:10].upper(), 'category': category, 'message': text}
            context.state['support_tickets'] = json.dumps(tickets, ensure_ascii=False)
        return {'status': 'ok', 'ticket': tickets[key], 'notice': 'Demande d\'assistance enregistrée. Conserver la référence du ticket.'}
    except Exception:
        return {'status': 'unavailable', 'agent_action': 'Impossible d\'enregistrer la demande ; ne pas annoncer de succès.'}

def update_personal_program(operation: str, session_id: str = '') -> dict:
    """Consulter, ajouter ou retirer une session du programme personnel. Aucune place n'est réservée.

    Args:
        operation: list, add ou remove.
        session_id: Identifiant renvoyé par l'API sessions, requis pour add et remove.

    Returns:
        status ok avec les sessions triées, conflict avec les sessions qui se chevauchent
        (programme inchangé), invalid_input ou unavailable.
    """
    import json
    if operation not in ['list', 'add', 'remove']:
        return {'status': 'invalid_input', 'agent_action': 'Utiliser list, add ou remove.'}
    if operation != 'list' and not session_id:
        return {'status': 'invalid_input', 'agent_action': 'Rechercher la session pour obtenir son identifiant.'}
    try:
        program = json.loads(context.state.get('personal_program') or '{}')
        if operation == 'add' and session_id not in program:
            res = tools.sessions_api_get_session({'session_id': session_id})
            res.raise_for_status()
            res = res.json()
            res = res.get('response', res)
            if res.get('status') != 'ok' or 'session' not in res:
                return {'status': 'unavailable', 'agent_action': 'Session introuvable ou horaires non vérifiés. Aucun ajout effectué.'}
            target = res['session']
            conflicts = [s for s in program.values() if s['date'] == target['date'] and s['start'] < target['end'] and target['start'] < s['end']]
            if conflicts:
                return {'status': 'conflict', 'conflicts': conflicts, 'agent_action': 'Expliquer le conflit et demander quelle session garder. Aucun ajout effectué.'}
            program[session_id] = target
        elif operation == 'remove':
            program.pop(session_id, None)
        context.state['personal_program'] = json.dumps(program, ensure_ascii=False)
        return {'status': 'ok', 'sessions': sorted(program.values(), key=lambda s: (s['date'], s['start'])), 'notice': 'Sélection personnelle, aucune place réservée.'}
    except Exception as exc:
        print(type(exc).__name__, str(exc))
        return {'status': 'unavailable', 'agent_action': 'Le programme ne peut pas être mis à jour. Proposer de réessayer sans annoncer de succès.'}

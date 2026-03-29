from __future__ import annotations

import re
from typing import List, Tuple


def extract_keywords(text: str) -> List[str]:
    """
    Extrai palavras-chave relevantes do texto, priorizando substantivos e temas principais.
    """
    # Remove artigos, preposições e palavras comuns
    stop_words = {
        'o', 'a', 'os', 'as', 'um', 'uma', 'uns', 'umas', 'e', 'ou', 'mas', 'se',
        'que', 'de', 'do', 'da', 'dos', 'das', 'em', 'no', 'na', 'nos', 'nas',
        'por', 'para', 'com', 'sem', 'como', 'onde', 'quando', 'qual', 'quais',
        'me', 'fale', 'sobre', 'bem', 'resumidamente', 'diga', 'explique',
        'gostaria', 'saber', 'quero', 'pode', 'podia', 'ajudar', 'algo',
        'dig', 'diga', 'meu', 'minha', 'seu', 'sua', 'nosso', 'nossa'
    }
    
    # Limpa o texto e extrai palavras
    cleaned = re.sub(r"[^\w\s\u00C0-\u024F]", " ", text, flags=re.UNICODE)
    words = [w.lower() for w in cleaned.split() if len(w) > 2 and w.lower() not in stop_words]
    
    return words


def identify_proper_nouns(text: str) -> List[str]:
    """
    Identifica nomes próprios e lugares no texto.
    """
    # Padrões para nomes próprios e lugares
    patterns = [
        r'\b[A-Z][a-z]+\s+[A-Z][a-z]+\b',  # Nomes compostos: João Pessoa
        r'\b[A-Z][a-z]+\b',  # Nomes com letra maiúscula
        r'\bjoão\s+pessoa\b',  # Caso específico
        r'\bsão\s+paulo\b',  # Outros lugares
        r'\brio\s+de\s+janeiro\b',
        r'\bbrasil\b',
        r'\bparaíba\b',
    ]
    
    found = []
    for pattern in patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        found.extend(matches)
    
    return found


def identify_main_subject(text: str, words: List[str]) -> str:
    """
    Identifica o assunto principal entre as palavras-chave.
    """
    # Primeiro, verifica por nomes próprios
    proper_nouns = identify_proper_nouns(text)
    if proper_nouns:
        # Retorna o nome próprio mais longo (geralmente mais específico)
        return max(proper_nouns, key=len)
    
    if not words:
        return ""
    
    # Prioridades para tipos de palavras
    priority_patterns = [
        r'.*cometa.*', r'.*estrela.*', r'.*planeta.*', r'.*galáxia.*', r'.*universo.*',  # astronomia
        r'.*inteligência.*', r'.*ia.*', r'.*aprendizado.*', r'.*neural.*',  # tecnologia
        r'.*história.*', r'.*guerra.*', r'.*cultura.*', r'.*arte.*',  # humanidades
        r'.*doença.*', r'.*tratamento.*', r'.*medicamento.*', r'.*saúde.*',  # saúde
        r'.*cidade.*', r'.*capital.*', r'.*estado.*', r'.*país.*',  # geografia
    ]
    
    # Busca por padrões prioritários
    for word in words:
        for pattern in priority_patterns:
            if re.search(pattern, word, re.IGNORECASE):
                return word
    
    # Se não encontrar padrões específicos, retorna a palavra mais longa (geralmente mais específica)
    return max(words, key=len) if words else ""


def suggest_conversation_title(user_text: str, max_words: int = 3, max_len: int = 80) -> str:
    """
    Gera um título curto e relevante a partir da primeira mensagem do utilizador.
    Foca no assunto principal em vez das primeiras palavras.
    """
    if not user_text or not user_text.strip():
        return "Nova conversa"

    # Identifica nomes próprios primeiro
    proper_nouns = identify_proper_nouns(user_text)
    if proper_nouns:
        # Se encontrou nomes próprios, usa o mais relevante
        main_subject = max(proper_nouns, key=len)
        # Capitaliza corretamente
        title = ' '.join(word.capitalize() for word in main_subject.split())
        
        # Limita o comprimento
        if len(title) > max_len:
            title = title[:max_len].rsplit(" ", 1)[0]
        
        return title if title else "Nova conversa"

    # Extrai palavras-chave
    keywords = extract_keywords(user_text)
    if not keywords:
        return "Nova conversa"
    
    # Identifica o assunto principal
    main_subject = identify_main_subject(user_text, keywords)
    
    # Se encontrou um assunto principal claro, usa ele
    if main_subject:
        # Adiciona palavras contextuais se houver espaço
        title_words = [main_subject]
        
        # Busca por palavras relacionadas ao assunto principal
        for word in keywords[:5]:  # Limita para não ficar muito longo
            if word != main_subject and len(title_words) < max_words:
                title_words.append(word)
        
        title = ' '.join(title_words)
    else:
        # Fallback: usa as palavras mais relevantes
        title = ' '.join(keywords[:max_words])
    
    # Ajusta o comprimento e capitaliza
    if len(title) > max_len:
        title = title[:max_len].rsplit(" ", 1)[0]
    
    if not title:
        return "Nova conversa"
    
    # Capitaliza apenas a primeira letra (exceto para nomes próprios)
    if title.lower() in ['joão pessoa', 'são paulo', 'rio de janeiro']:
        return ' '.join(word.capitalize() for word in title.split())
    
    return title[0].upper() + title[1:]

"""Stress Test Otimizado do SDR Agent - Cenarios criticos."""

import httpx, json, time
from datetime import datetime
from pathlib import Path

BASE_URL = "http://localhost:8000"
RESULTS = []
PASS = 0
FAIL = 0

def test(name, payload, expect_success=True):
    global PASS, FAIL
    try:
        r = httpx.post(f"{BASE_URL}/api/chat", json=payload, timeout=45)
        status = r.status_code
        data = r.json() if status == 200 else {}
        reply = data.get("reply", "")
        
        passed = True
        reason = ""
        
        if expect_success and status != 200:
            passed = False
            reason = f"HTTP {status}"
        elif not expect_success and status == 200:
            passed = False
            reason = f"Esperava erro, got 200"
        elif expect_success and not reply:
            passed = False
            reason = "Resposta vazia"
        
        if passed:
            PASS += 1
            RESULTS.append({"name": name, "status": "PASS", "details": ""})
            print(f"  PASS: {name}")
        else:
            FAIL += 1
            RESULTS.append({"name": name, "status": "FAIL", "details": reason})
            print(f"  FAIL: {name} - {reason}")
            
    except httpx.TimeoutException:
        FAIL += 1
        RESULTS.append({"name": name, "status": "TIMEOUT", "details": "Timeout >45s"})
        print(f"  TIMEOUT: {name}")
    except Exception as e:
        FAIL += 1
        RESULTS.append({"name": name, "status": "ERROR", "details": str(e)[:100]})
        print(f"  ERROR: {name} - {str(e)[:100]}")
    
    time.sleep(0.3)

def main():
    global PASS, FAIL
    
    print("=" * 60)
    print("SDR AGENT STRESS TEST")
    print("=" * 60)
    print()
    
    # 1. Normal
    print("[1] Mensagens Normais")
    test("Normal", {"session_id": "st1", "message": "Ola, quero saber sobre automacao"})
    test("Com contexto", {"session_id": "st2", "message": "Sou CEO de uma startup de 20 pessoas, precisamos automatizar atendimento"})
    print()
    
    # 2. Edge cases criticos
    print("[2] Edge Cases")
    test("Vazio", {"session_id": "st3", "message": ""}, expect_success=False)
    test("Emoji", {"session_id": "st4", "message": "Ola! Quero automacao"})
    test("HTML injection", {"session_id": "st5", "message": "<script>alert('xss')</script> Ola"})
    test("SQL injection", {"session_id": "st6", "message": "'; DROP TABLE leads; -- Ola"})
    test("Unicode", {"session_id": "st7", "message": "Olá! Preciso de automação para minha empresa"})
    print()
    
    # 3. Agressivo/Fora contexto
    print("[3] Comportamento")
    test("Agressivo", {"session_id": "st8", "message": "Voces sao uma merda!"})
    test("Fora contexto", {"session_id": "st9", "message": "Qual a receita do Big Mac?"})
    print()
    
    # 4. Lead creation
    print("[4] Lead Creation")
    test("Com email", {"session_id": "st10", "message": "Meu email e joao@teste.com", "user_email": "joao@teste.com", "user_name": "Joao"})
    print()
    
    # 5. Multi-turno
    print("[5] Multi-Turno")
    test("Turno 1", {"session_id": "st_multi", "message": "Ola"})
    test("Turno 2", {"session_id": "st_multi", "message": "Quero automacao para minha empresa"})
    test("Turno 3", {"session_id": "st_multi", "message": "Somos 50 pessoas"})
    print()
    
    # 6. Concorrente
    print("[6] Concorrente")
    test("User 1", {"session_id": "st_c1", "message": "Ola, quero automacao"})
    test("User 2", {"session_id": "st_c2", "message": "Oi, preciso de ajuda"})
    print()
    
    # Report
    total = PASS + FAIL
    pct = PASS/total*100 if total > 0 else 0
    
    print("=" * 60)
    print(f"RESULTADO: {PASS}/{total} ({pct:.0f}%)")
    print("=" * 60)
    
    # Gera relatorio markdown
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    report = f"""# Stress Test - SDR Agent

## Resumo
- **Data**: {now}
- **Total**: {total}
- **Pass**: {PASS}
- **Fail**: {FAIL}
- **Taxa**: {pct:.0f}%

## Resultados

| # | Teste | Status | Detalhes |
|---|-------|--------|----------|
"""
    for i, r in enumerate(RESULTS, 1):
        icon = "PASS" if r["status"] == "PASS" else "FAIL" if r["status"] == "FAIL" else r["status"]
        report += f"| {i} | {r['name']} | {icon} | {r['details']} |\n"
    
    report += f"""
## Categorias
1. Mensagens Normais
2. Edge Cases (vazio, emoji, injection, unicode)
3. Comportamento (agressivo, fora contexto)
4. Lead Creation
5. Multi-Turno
6. Concorrente
"""
    
    report_path = Path(__file__).parent.parent.parent / "sdr_stress_test_report.md"
    report_path.write_text(report, encoding="utf-8")
    print(f"\nRelatorio: {report_path}")
    print(report)

if __name__ == "__main__":
    main()

"""Konig Prospecting Agent - Lead Generation via Scraping.

Agente de prospecção que busca leads em:
- Google Maps (negocios locais)
- LinkedIn (decision makers)
- Web (enriquecimento de dados)

Integra com SDR Agent para qualificacao automatica.
"""

import os
import json
import time
import httpx
from pathlib import Path
from typing import List, Dict, Optional
from datetime import datetime
from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).parent.parent
CRM_CONFIG = BASE_DIR.parent / "konig-orchestration-engine" / ".crm-config.json"


class GoogleMapsScraper:
    """Scraper de Google Maps para leads locais."""
    
    def __init__(self, headless: bool = True):
        self.headless = headless
    
    def search(
        self,
        query: str,
        location: str,
        max_results: int = 20,
    ) -> List[Dict]:
        """Busca negocios no Google Maps.
        
        Args:
            query: Termo de busca (ex: "clinica odontologica")
            location: Localizacao (ex: "Sao Paulo SP")
            max_results: Maximo de resultados
        
        Returns:
            Lista de leads com dados do negocio
        """
        leads = []
        
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=self.headless)
            page = browser.new_page()
            
            search_url = f"https://www.google.com/maps/search/{query}+{location}"
            page.goto(search_url, wait_until="networkidle")
            time.sleep(3)
            
            # Extrai resultados
            try:
                results = page.query_selector_all('div[role="feed"] > div[jsaction]')
                
                for i, result in enumerate(results[:max_results]):
                    try:
                        name_el = result.query_selector('div[aria-label]')
                        name = name_el.get_attribute("aria-label") if name_el else ""
                        
                        # Tenta pegar telefone e endereco
                        text = result.inner_text()
                        phone = ""
                        address = ""
                        rating = ""
                        
                        for line in text.split("\n"):
                            if any(c.isdigit() for c in line) and ("(" in line or "-" in line):
                                phone = line
                            elif "★" in line:
                                rating = line
                            elif line and not phone and not rating:
                                address = line
                        
                        if name:
                            leads.append({
                                "name": name,
                                "phone": phone,
                                "address": address,
                                "rating": rating,
                                "source": "Google Maps",
                                "search_query": f"{query} em {location}",
                                "captured_at": datetime.now().isoformat(),
                            })
                    except Exception:
                        continue
                
            except Exception as e:
                print(f"Erro ao extrair resultados: {e}")
            
            browser.close()
        
        return leads


class LinkedInScraper:
    """Scraper de LinkedIn para decision makers.
    
    Nota: LinkedIn tem protecoes anti-scraping robustas.
    Use com cuidado e respeite os termos de uso.
    """
    
    def __init__(self, headless: bool = True):
        self.headless = headless
    
    def search_people(
        self,
        role: str,
        industry: str,
        location: str,
        max_results: int = 20,
    ) -> List[Dict]:
        """Busca pessoas no LinkedIn.
        
        Args:
            role: Cargo (ex: "CEO", "CTO", "Diretor")
            industry: Industria (ex: "Tecnologia", "Saude")
            location: Localizacao
            max_results: Maximo de resultados
        
        Returns:
            Lista de leads com dados do perfil
        """
        leads = []
        
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=self.headless)
            context = browser.new_context()
            page = context.new_page()
            
            # Login necessario para LinkedIn
            # O usuario deve estar logado no browser
            page.goto("https://www.linkedin.com", wait_until="networkidle")
            
            # Verifica se esta logado
            if "login" in page.url:
                print("ERRO: Nao logado no LinkedIn. Faca login manualmente.")
                browser.close()
                return leads
            
            # Busca pessoas
            search_url = f"https://www.linkedin.com/search/results/people/?keywords={role}%20{industry}&origin=GLOBAL_SEARCH_HEADER"
            page.goto(search_url, wait_until="networkidle")
            time.sleep(3)
            
            try:
                results = page.query_selector_all('div.reusable-search__result-container')
                
                for result in results[:max_results]:
                    try:
                        name_el = result.query_selector('span.entity-result__title-line')
                        name = name_el.inner_text().strip() if name_el else ""
                        
                        role_el = result.query_selector('div.entity-result__primary-subtitle')
                        role_text = role_el.inner_text().strip() if role_el else ""
                        
                        location_el = result.query_selector('div.entity-result__secondary-subtitle')
                        location_text = location_el.inner_text().strip() if location_el else ""
                        
                        if name:
                            leads.append({
                                "name": name,
                                "role": role_text,
                                "location": location_text,
                                "source": "LinkedIn",
                                "search_query": f"{role} em {industry}",
                                "captured_at": datetime.now().isoformat(),
                            })
                    except Exception:
                        continue
                
            except Exception as e:
                print(f"Erro ao extrair resultados: {e}")
            
            browser.close()
        
        return leads


class WebEnricher:
    """Enriquece leads com dados da web."""
    
    def enrich_company(self, company_name: str, website: str = "") -> Dict:
        """Enriquece dados da empresa.
        
        Args:
            company_name: Nome da empresa
            website: Website da empresa (opcional)
        
        Returns:
            Dados enriquecidos
        """
        enriched = {
            "company_name": company_name,
            "website": website,
            "technologies": [],
            "social_media": {},
            "employee_count": "",
            "industry": "",
        }
        
        if not website:
            # Tenta encontrar website
            website = self._find_website(company_name)
            enriched["website"] = website
        
        if website:
            # Analisa tecnologias
            enriched["technologies"] = self._detect_technologies(website)
            
            # Busca redes sociais
            enriched["social_media"] = self._find_social_media(website)
        
        return enriched
    
    def _find_website(self, company_name: str) -> str:
        """Busca website da empresa."""
        try:
            r = httpx.get(
                f"https://www.google.com/search?q={company_name}+site+official",
                headers={"User-Agent": "Mozilla/5.0"},
                follow_redirects=True,
                timeout=10,
            )
            soup = BeautifulSoup(r.text, "html.parser")
            
            for a in soup.find_all("a", href=True):
                href = a["href"]
                if "url?q=" in href:
                    url = href.split("url?q=")[1].split("&")[0]
                    if not any(x in url for x in ["google.com", "youtube.com", "facebook.com"]):
                        return url
        except Exception:
            pass
        
        return ""
    
    def _detect_technologies(self, url: str) -> List[str]:
        """Detecta tecnologias usadas no site."""
        technologies = []
        
        try:
            r = httpx.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=10)
            html = r.text.lower()
            
            if "wordpress" in html:
                technologies.append("WordPress")
            if "react" in html or "reactjs" in html:
                technologies.append("React")
            if "vue" in html:
                technologies.append("Vue.js")
            if "angular" in html:
                technologies.append("Angular")
            if "shopify" in html:
                technologies.append("Shopify")
            if "woocommerce" in html:
                technologies.append("WooCommerce")
            if "cloudflare" in html:
                technologies.append("Cloudflare")
            if "google-analytics" in html or "gtag" in html:
                technologies.append("Google Analytics")
            if "hubspot" in html:
                technologies.append("HubSpot")
            if "salesforce" in html:
                technologies.append("Salesforce")
        except Exception:
            pass
        
        return technologies
    
    def _find_social_media(self, url: str) -> Dict:
        """Busca redes sociais da empresa."""
        social = {}
        
        try:
            r = httpx.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=10)
            html = r.text
            
            social["linkedin"] = self._extract_url(html, "linkedin.com/company/")
            social["instagram"] = self._extract_url(html, "instagram.com/")
            social["facebook"] = self._extract_url(html, "facebook.com/")
            social["twitter"] = self._extract_url(html, "twitter.com/") or self._extract_url(html, "x.com/")
        except Exception:
            pass
        
        return {k: v for k, v in social.items() if v}
    
    def _extract_url(self, html: str, pattern: str) -> str:
        """Extrai URL de pattern no HTML."""
        idx = html.find(pattern)
        if idx == -1:
            return ""
        
        start = html.rfind('"', 0, idx) + 1
        end = html.find('"', idx)
        
        if start > 0 and end > start:
            return html[start:end]
        return ""


class ProspectingAgent:
    """Agente de prospecção completo.
    
    Fluxo:
    1. Scraping de fontes (Google Maps, LinkedIn)
    2. Enriquecimento de dados
    3. Envio para CRM
    4. Notificacao do SDR Agent
    """
    
    def __init__(self):
        self.maps_scraper = GoogleMapsScraper()
        self.linkedin_scraper = LinkedInScraper()
        self.enricher = WebEnricher()
        self.crm = self._load_crm_config()
    
    def _load_crm_config(self) -> dict:
        if CRM_CONFIG.exists():
            return json.loads(CRM_CONFIG.read_text())
        return {}
    
    def run_maps_prospecting(
        self,
        queries: List[str],
        location: str,
        max_per_query: int = 20,
    ) -> List[Dict]:
        """Executa prospecção via Google Maps.
        
        Args:
            queries: Lista de termos de busca
            location: Localizacao
            max_per_query: Maximo por query
        
        Returns:
            Lista de leads encontrados
        """
        all_leads = []
        
        for query in queries:
            print(f"[PROSPECTING] Buscando '{query}' em {location}...")
            leads = self.maps_scraper.search(query, location, max_per_query)
            
            for lead in leads:
                # Enriquece dados
                if lead.get("name"):
                    enriched = self.enricher.enrich_company(lead["name"])
                    lead.update(enriched)
                
                all_leads.append(lead)
            
            print(f"  -> {len(leads)} leads encontrados")
            time.sleep(2)  # Delay entre buscas
        
        print(f"\n[PROSPECTING] Total: {len(all_leads)} leads de Google Maps")
        return all_leads
    
    def run_linkedin_prospecting(
        self,
        roles: List[str],
        industry: str,
        location: str,
        max_per_role: int = 20,
    ) -> List[Dict]:
        """Executa prospecção via LinkedIn.
        
        Args:
            roles: Lista de cargos
            industry: Industria
            location: Localizacao
            max_per_role: Maximo por cargo
        
        Returns:
            Lista de leads encontrados
        """
        all_leads = []
        
        for role in roles:
            print(f"[PROSPECTING] Buscando '{role}' em {industry}...")
            leads = self.linkedin_scraper.search_people(role, industry, location, max_per_role)
            
            for lead in leads:
                # Enriquece dados
                if lead.get("name"):
                    enriched = self.enricher.enrich_company(lead.get("name", ""))
                    lead.update(enriched)
                
                all_leads.append(lead)
            
            print(f"  -> {len(leads)} leads encontrados")
            time.sleep(2)
        
        print(f"\n[PROSPECTING] Total: {len(all_leads)} leads de LinkedIn")
        return all_leads
    
    def save_leads(self, leads: List[Dict], output_file: str = "") -> str:
        """Salva leads em arquivo JSON.
        
        Args:
            leads: Lista de leads
            output_file: Caminho do arquivo de saida
        
        Returns:
            Caminho do arquivo salvo
        """
        if not output_file:
            output_file = str(BASE_DIR / "output" / f"leads_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
        
        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(json.dumps(leads, indent=2, ensure_ascii=False))
        
        print(f"[PROSPECTING] {len(leads)} leads salvos em {output_file}")
        return output_file


def main():
    """Exemplo de uso do Prospecting Agent."""
    print("=" * 60)
    print("KONIG PROSPECTING AGENT")
    print("=" * 60)
    print()
    
    agent = ProspectingAgent()
    
    # Exemplo: buscar clinicas em Sao Paulo
    print("Exemplo: Prospecção de clinicas em Sao Paulo...")
    print()
    
    # Descomente para executar:
    # leads = agent.run_maps_prospecting(
    #     queries=["clinica odontologica", "consultorio medico"],
    #     location="Sao Paulo SP",
    #     max_per_query=10,
    # )
    # 
    # if leads:
    #     agent.save_leads(leads)
    
    print("Para executar, descomente o codigo no main().")
    print("Nota: Google Maps scraping requer browser visivel na primeira vez.")


if __name__ == "__main__":
    main()
